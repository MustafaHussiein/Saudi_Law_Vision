"""
llm.py  —  Saudi Law RAG · Query & Answer Endpoint
====================================================
Multi-provider LLM support. Set LLM_PROVIDER env var to switch:

  LLM_PROVIDER=ollama   → local qwen2.5:7b  (default, free, private)
  LLM_PROVIDER=gemini   → Gemini 1.5 Flash  (recommended API: fast + cheap Arabic)
  LLM_PROVIDER=openai   → GPT-4o-mini       (reliable, good Arabic)
  LLM_PROVIDER=claude   → Claude Haiku      (best Arabic quality, higher cost)

Required env vars per provider:
  GEMINI_API_KEY    → https://aistudio.google.com/app/apikey
  OPENAI_API_KEY    → https://platform.openai.com/api-keys
  ANTHROPIC_API_KEY → https://console.anthropic.com/

Install deps:
  pip install google-generativeai openai anthropic langchain-ollama

NOTE: Embedding + Reranking always run locally regardless of provider.
      Only the final answer generation step hits the API.
"""

import os
import re
import logging
import threading
import time
import traceback
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer, CrossEncoder

logger = logging.getLogger("app.api.v1.endpoints.llm")

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════════

CURRENT_FILE_PATH = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(
             os.path.dirname(
               os.path.dirname(
                 os.path.dirname(
                   os.path.dirname(CURRENT_FILE_PATH)))))

COLLECTION_NAME = "saudi_law_data"   # change to "saudi_law" for 83-law collection

# ── Qdrant ────────────────────────────────────────────────────────────────────
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# ── Embedding + Reranker (always local, never changes) ────────────────────────
PRIMARY_EMBED  = "Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2"
RERANKER_MODEL = "Omartificial-Intelligence-Space/ARA-Reranker-V1"

# ── LLM Provider ──────────────────────────────────────────────────────────────
# Options: "ollama" | "gemini" | "openai" | "claude"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# Ollama settings (used when LLM_PROVIDER=ollama)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://127.0.0.1:11434")

# API keys (used when LLM_PROVIDER != ollama)
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY",    "AIzaSyCu3KHEhJayXAa9Fp0teYubBnb8cN8EIlo")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY",    "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# API model names (override via env if needed)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
OPENAI_MODEL    = os.getenv("OPENAI_MODEL",    "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

# ══════════════════════════════════════════════════════════════════════════════
#  GREETING DETECTION
# ══════════════════════════════════════════════════════════════════════════════

_GREET_RE = re.compile(
    r"^(مرحبا|مرحباً|السلام عليكم|اهلا|أهلاً|أهلا|هلا|هاي|هي"
    r"|صباح الخير|مساء الخير|كيف حالك|ماشو|شخبارك"
    r"|hi|hello|hey|good\s*(morning|evening|afternoon|day))\b",
    re.IGNORECASE,
)

_GREET_REPLY = (
    "مرحباً! أنا مساعدك القانوني المتخصص في الأنظمة السعودية. "
    "يمكنني الإجابة على أسئلتك حول الأنظمة واللوائح السعودية. "
    "كيف يمكنني مساعدتك اليوم؟"
)

def _is_greeting(text: str) -> bool:
    return bool(_GREET_RE.match(text.strip()))

# ══════════════════════════════════════════════════════════════════════════════
#  ARABIC NORMALIZATION  (must match ingest.py exactly)
# ══════════════════════════════════════════════════════════════════════════════

_CHAR_MAP = str.maketrans({
    "\u06BE": "\u0647",  # ھ → ه  (Urdu heh)
    "\u06C1": "\u0647",  # ہ → ه
    "\u06CC": "\u064A",  # ی → ي  (Farsi yeh)
    "\u0649": "\u064A",  # ى → ي  (alef maqsura)
    "\u06A9": "\u0643",  # ک → ك  (Farsi kaf)
    "\u0640": "",         # tatweel — remove
})

def normalize_arabic(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_CHAR_MAP)
    return re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", text)

# ══════════════════════════════════════════════════════════════════════════════
#  PROMPT BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _build_system_prompt() -> str:
    return (
        "أنت مساعد قانوني خبير في الأنظمة السعودية. "
        "مهمتك هي شرح الأنظمة بوضوح ودقة بناءً على النصوص المقدمة. "
        "قدم إجابة وافية تشرح المفهوم المطلوب، ثم اذكر اسم النظام ورقم المادة كمرجع."
    )

def _build_user_prompt(query: str, context: str) -> str:
    return (
        f"بناءً على النصوص القانونية التالية:\n{context}\n"
        f"السؤال: {query}\n"
        "الرجاء تقديم إجابة مفصلة تشرح النص القانوني مع الاستشهاد بالمواد والأنظمة المعنية:"
    )

# ══════════════════════════════════════════════════════════════════════════════
#  LLM BACKENDS
# ══════════════════════════════════════════════════════════════════════════════

class _OllamaBackend:
    """Local Ollama — free, private, no API key needed."""
    def __init__(self):
        from langchain_ollama import OllamaLLM
        self.llm = OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_URL,
            temperature=0,
        )
        logger.info(f"Ollama backend: {OLLAMA_MODEL} @ {OLLAMA_URL}")

    def invoke(self, query: str, context: str) -> str:
        # Ollama gets the system prompt baked into the user prompt
        prompt = _build_system_prompt() + "\n\n" + _build_user_prompt(query, context)
        return self.llm.invoke(prompt)


class _GeminiBackend:
    def __init__(self):
        import google.generativeai as genai
        # ... (key checks) ...
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Ensure the model name has the required prefix
        model_name = GEMINI_MODEL
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
            
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=_build_system_prompt(),
        )
        logger.info(f"Gemini backend: {model_name}")

    def invoke(self, query: str, context: str) -> str:
        response = self.model.generate_content(
            _build_user_prompt(query, context),
            generation_config={"temperature": 0.3},
        )
        return response.text


class _OpenAIBackend:
    """
    OpenAI GPT-4o-mini — reliable, good Arabic, moderate cost.
    ~$0.15/1M input tokens. Safe choice if you already have an OpenAI account.
    """
    def __init__(self):
        from openai import OpenAI
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not set. "
                "Get one at https://platform.openai.com/api-keys"
            )
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info(f"OpenAI backend: {OPENAI_MODEL}")

    def invoke(self, query: str, context: str) -> str:
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user",   "content": _build_user_prompt(query, context)},
            ],
            temperature=0,
            max_tokens=1024,
        )
        return response.choices[0].message.content


class _ClaudeBackend:
    """
    Anthropic Claude Haiku — best Arabic legal reasoning quality.
    Higher cost (~$0.80/1M tokens) but most accurate citations and analysis.
    """
    def __init__(self):
        import anthropic
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. "
                "Get one at https://console.anthropic.com/"
            )
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info(f"Claude backend: {ANTHROPIC_MODEL}")

    def invoke(self, query: str, context: str) -> str:
        response = self.client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=_build_system_prompt(),
            messages=[{
                "role": "user",
                "content": _build_user_prompt(query, context),
            }],
        )
        return response.content[0].text


def _build_llm_backend():
    """Factory — returns the right backend based on LLM_PROVIDER."""
    backends = {
        "ollama": _OllamaBackend,
        "gemini": _GeminiBackend,
        "openai": _OpenAIBackend,
        "claude": _ClaudeBackend,
    }
    if LLM_PROVIDER not in backends:
        raise ValueError(
            f"Unknown LLM_PROVIDER='{LLM_PROVIDER}'. "
            f"Valid options: {list(backends.keys())}"
        )
    logger.info(f"Initializing LLM_PROVIDER={LLM_PROVIDER}")
    return backends[LLM_PROVIDER]()

# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE  (singleton, loaded once in background thread)
# ══════════════════════════════════════════════════════════════════════════════

class _Engine:
    def __init__(self):
        self.embed_model: Optional[SentenceTransformer] = None
        self.reranker:    Optional[CrossEncoder]        = None
        self.qdrant:      Optional[QdrantClient]        = None
        self.llm_backend                                = None
        self.current_provider: Optional[str]            = None   # 👈 ADD THIS
        self.is_ready:    bool                          = False
        self.error:       str                           = ""

def _reset_llm_backend():
    """Free memory + reset LLM backend safely."""
    global _engine

    try:
        logger.warning("🔄 Resetting LLM backend...")

        # Delete backend
        if _engine.llm_backend:
            del _engine.llm_backend
            _engine.llm_backend = None

        # 🔥 IMPORTANT: free GPU memory if using torch
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

        _engine.current_provider = None

    except Exception as e:
        logger.error(f"Error during reset: {e}")
_engine = _Engine()

def _load_engine_task():
    try:
        logger.info(f"BASE_DIR     : {BASE_DIR}")
        logger.info(f"Qdrant       : {QDRANT_HOST}:{QDRANT_PORT}")
        logger.info(f"LLM_PROVIDER : {LLM_PROVIDER}")

        # 1. Embedding model — always local
        logger.info("Loading embedding model...")
        _engine.embed_model = SentenceTransformer(PRIMARY_EMBED, trust_remote_code=True)

        # 2. Reranker — always local
        logger.info("Loading reranker...")
        _engine.reranker = CrossEncoder(RERANKER_MODEL)

        # 3. LLM backend — local or API
        logger.info(f"Loading LLM backend: {LLM_PROVIDER}...")
        _engine.llm_backend = _build_llm_backend()

        # 4. Qdrant
        logger.info("Connecting to Qdrant...")
        for attempt in range(1, 11):
            try:
                _engine.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
                count = _engine.qdrant.count(COLLECTION_NAME).count
                logger.info(f"Qdrant OK — {count:,} vectors in '{COLLECTION_NAME}'")
                break
            except Exception as e:
                logger.warning(f"Qdrant attempt {attempt}/10: {e}")
                _engine.qdrant = None
                time.sleep(5)
        else:
            raise RuntimeError(
                f"Cannot connect to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}.\n"
                "Make sure qdrant.exe is running before starting the server."
            )

        _engine.is_ready = True
        logger.info("🟢 LEGAL AI ENGINE READY")

    except Exception:
        _engine.error = traceback.format_exc()
        logger.error(f"Engine startup failed:\n{_engine.error}")

threading.Thread(target=_load_engine_task, daemon=True).start()

# ══════════════════════════════════════════════════════════════════════════════
#  SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class SourceDetail(BaseModel):
    file:    str
    page:    int
    article: Optional[str] = "N/A"
    score:   float

class ChatResponse(BaseModel):
    answer:         str
    sources_detail: List[SourceDetail]
    type:           str
    chunks_used:    int
    provider:       str   # shows which LLM answered

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════

router = APIRouter(tags=["AI"])

def _guard():
    if _engine.error:
        raise HTTPException(
            status_code=500,
            detail=f"Engine failed to start: {_engine.error[:400]}"
        )
    raise HTTPException(
        status_code=503,
        detail="Engine still loading — retry in a few seconds."
    )

def _handle_query(query: str) -> ChatResponse:
    query = query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if _is_greeting(query):
        return ChatResponse(
            answer=_GREET_REPLY,
            sources_detail=[],
            type="greeting",
            chunks_used=0,
            provider=LLM_PROVIDER,
        )

    # 1. Normalize + Embed
    query_norm = normalize_arabic(query)
    query_vec  = _engine.embed_model.encode(
        query_norm, normalize_embeddings=True
    ).tolist()

    # 2. Vector search — top 10 candidates
    hits = _engine.qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=10,
    )

    if not hits:
        return ChatResponse(
            answer="لا تتوفر معلومات كافية في الأنظمة المتاحة حول هذا الموضوع.",
            sources_detail=[],
            type="legal",
            chunks_used=0,
            provider=LLM_PROVIDER,
        )

    # 3. Rerank → keep top 3
    pairs  = [(query_norm, h.payload["text"]) for h in hits]
    scores = _engine.reranker.predict(pairs)
    ranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)[:3]

    # 4. Build context
    context = ""
    for h, _ in ranked:
        p = h.payload
        context += (
            f"[{p.get('file_name', '')} | {p.get('article_ref', '')}]\n"
            f"{p.get('text', '')}\n\n"
        )

    # 5. Generate via selected backend
    try:
        # 🔥 Detect provider change
        if _engine.current_provider != LLM_PROVIDER:
            _reset_llm_backend()
            _engine.llm_backend = _build_llm_backend()
            _engine.current_provider = LLM_PROVIDER
        answer = _engine.llm_backend.invoke(query_norm, context)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM error ({LLM_PROVIDER}): {e}"
        )
    # 6. Strip CJK for local models only
    if LLM_PROVIDER == "ollama":
        cleaned = [
            line for line in answer.strip().splitlines()
            if sum(1 for c in line if "\u4e00" <= c <= "\u9fff") == 0
        ]
        answer = "\n".join(cleaned).strip()

    # 7. Build response
    details = [
        SourceDetail(
            file    = h.payload.get("file_name",   ""),
            page    = h.payload.get("page_number",  0),
            article = h.payload.get("article_ref", "N/A") or "N/A",
            score   = float(s),
        )
        for h, s in ranked
    ]

    return ChatResponse(
        answer=answer,
        sources_detail=details,
        type="legal",
        chunks_used=len(ranked),
        provider=LLM_PROVIDER,
    )

# ── POST /chat ────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_post(query: str = Query(..., description="السؤال القانوني")):
    if not _engine.is_ready:
        _guard()
    return _handle_query(query)

# ── GET /chat ─────────────────────────────────────────────────────────────────

@router.get("/chat", response_model=ChatResponse)
async def chat_get(query: str = Query(..., description="السؤال القانوني")):
    if not _engine.is_ready:
        _guard()
    return _handle_query(query)

# ── GET /status ───────────────────────────────────────────────────────────────

@router.get("/status")
async def status():
    info = {
        "ready":      _engine.is_ready,
        "provider":   LLM_PROVIDER,
        "qdrant":     f"{QDRANT_HOST}:{QDRANT_PORT}",
        "collection": COLLECTION_NAME,
        "reranker":   _engine.reranker is not None,
        "error":      _engine.error or None,
    }
    if LLM_PROVIDER == "ollama":
        info["model"]      = OLLAMA_MODEL
        info["ollama_url"] = OLLAMA_URL
    elif LLM_PROVIDER == "gemini":
        info["model"]       = GEMINI_MODEL
        info["api_key_set"] = bool(GEMINI_API_KEY)
    elif LLM_PROVIDER == "openai":
        info["model"]       = OPENAI_MODEL
        info["api_key_set"] = bool(OPENAI_API_KEY)
    elif LLM_PROVIDER == "claude":
        info["model"]       = ANTHROPIC_MODEL
        info["api_key_set"] = bool(ANTHROPIC_API_KEY)

    if _engine.is_ready:
        try:
            info["total_vectors"] = _engine.qdrant.count(COLLECTION_NAME).count
        except Exception:
            info["total_vectors"] = -1
    return info

# ── GET /search  (debug — raw chunks, no LLM) ────────────────────────────────

@router.get("/search")
async def search(
    query: str = Query(...),
    k:     int = Query(5, ge=1, le=20),
):
    if not _engine.is_ready:
        _guard()

    query_vec = _engine.embed_model.encode(
        normalize_arabic(query), normalize_embeddings=True
    ).tolist()

    hits = _engine.qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=k,
    )

    return [
        {
            "score":    round(h.score, 4),
            "file":     h.payload.get("file_name",   ""),
            "page":     h.payload.get("page_number",  0),
            "article":  h.payload.get("article_ref", ""),
            "text":     h.payload.get("text", "")[:300],
        }
        for h in hits
    ]