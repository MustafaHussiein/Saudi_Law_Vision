"""
ingest.py  —  Saudi Law RAG · Ingestion Pipeline
=================================================
Supports two input modes (set MODE below):

  "data"     → reads data.txt (raw format, === separators between laws,
                first law starts at top of file with no leading separator)
  "combined" → reads saudi_laws_complete.txt (=== title === format, 83 laws)

Set COLLECTION_NAME accordingly so the two datasets don't mix.
"""

import os, re, gc, time, hashlib, unicodedata
from pathlib import Path
from typing import List, Tuple

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG  ← edit here
# ══════════════════════════════════════════════════════════════════════════════

MODE            = "data"       # "data" or "combined"

# data.txt path
DATA_TXT        = "E:/Previous work/Amad AlOula/Amad AlOula1.2/SaudiLawTxt/data.txt"

# saudi_laws_complete.txt path (used when MODE="combined")
COMBINED_TXT    = "E:/Previous work/Amad AlOula/Amad AlOula1.2/SaudiLawTxt/saudi_laws_complete.txt"

PRIMARY_EMBED   = "Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2"
QDRANT_HOST     = "localhost"
QDRANT_PORT     = 6333

# Use separate collections so the two datasets don't overwrite each other
COLLECTION_NAME = "saudi_law_data"   # for data.txt
# COLLECTION_NAME = "saudi_law"      # for combined (83 laws)

CHUNK_SIZE      = 512
CHUNK_OVERLAP   = 100

# ══════════════════════════════════════════════════════════════════════════════
#  NORMALIZATION
# ══════════════════════════════════════════════════════════════════════════════

_CHAR_MAP = str.maketrans({
    '\u06BE': '\u0647', '\u06C1': '\u0647',
    '\u06CC': '\u064A', '\u0649': '\u064A',
    '\u06A9': '\u0643', '\u0640': '',
})

def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKC', text)
    text = text.translate(_CHAR_MAP)
    return re.sub(r'[\u200b-\u200f\u202a-\u202e\ufeff]', '', text)

# ══════════════════════════════════════════════════════════════════════════════
#  PARSERS
# ══════════════════════════════════════════════════════════════════════════════

def is_sep(line: str) -> bool:
    return line.strip().startswith('=' * 10)

def parse_data_txt(path: str) -> List[Tuple[str, str]]:
    """
    Parse data.txt format:
    - First law starts at top of file (no leading separator)
    - Laws separated by ======= lines
    - Law title = first line matching نظام/اللائحة/تنظيم pattern
    """
    raw   = Path(path).read_text(encoding='utf-8').splitlines()
    lines = [normalize(l) for l in raw]

    # Split into raw chunks on separator lines
    chunks, current = [], []
    for l in lines:
        if is_sep(l):
            if current:
                chunks.append(current)
            current = []
        else:
            current.append(l)
    if current:
        chunks.append(current)

    # Extract title + body from each chunk
    title_re = re.compile(r'^(نظام|اللائحة|تنظيم|قواعد)\s+\S')
    sections = []
    for chunk in chunks:
        non_empty = [l for l in chunk if l.strip()]
        if not non_empty:
            continue
        # Find title
        title = None
        for l in non_empty:
            if title_re.match(l.strip()) and len(l.strip()) < 80:
                title = l.strip()
                break
        if not title:
            # Fallback: use first non-empty line
            title = non_empty[0].strip()
        body = '\n'.join(chunk).strip()
        if body:
            sections.append((title, body))
    return sections


SKIP_TITLES = {'نهاية المجموعة', 'end', 'نهاية'}

def parse_combined_txt(path: str) -> List[Tuple[str, str]]:
    """Parse saudi_laws_complete.txt: === title === body format."""
    raw   = Path(path).read_text(encoding='utf-8').splitlines()
    lines = [normalize(l) for l in raw]
    n     = len(lines)
    sections, i = [], 0
    while i < n:
        if not is_sep(lines[i]):
            i += 1; continue
        if i+1 >= n or not lines[i+1].strip():
            i += 1; continue
        title   = lines[i+1].strip()
        closing = None
        for delta in range(2, 5):
            if i+delta < n and is_sep(lines[i+delta]):
                closing = i+delta; break
        if closing is None:
            i += 1; continue
        if title in SKIP_TITLES:
            i = closing+1; continue
        body_lines, j = [], closing+1
        while j < n:
            if is_sep(lines[j]): break
            body_lines.append(lines[j]); j += 1
        body = '\n'.join(body_lines).strip()
        if body:
            sections.append((title, body))
        i = j
    return sections

# ══════════════════════════════════════════════════════════════════════════════
#  CHUNKING & METADATA
# ══════════════════════════════════════════════════════════════════════════════

def get_article_ref(text: str) -> str:
    m = re.search(
        r'(المادة|الباب|الفصل)\s+([\u0600-\u06ff\s\d\(\)/]{1,40})',
        text[:300]
    )
    return m.group(0).strip() if m else ''

def chunk_text(text: str) -> List[str]:
    chunks, step = [], CHUNK_SIZE - CHUNK_OVERLAP
    for i in range(0, len(text), step):
        chunk = text[i : i + CHUNK_SIZE].strip()
        if len(chunk) >= 60:
            chunks.append(chunk)
    return chunks

def stable_id(text: str, law_name: str, idx: int) -> int:
    raw = f'{law_name}::{idx}::{text[:80]}'
    return int(hashlib.md5(raw.encode()).hexdigest()[:15], 16)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main_ingest():
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
    from sentence_transformers import SentenceTransformer

    if MODE == "data":
        print(f"[DATA MODE] Reading: {DATA_TXT}")
        sections = parse_data_txt(DATA_TXT)
    else:
        print(f"[COMBINED MODE] Reading: {COMBINED_TXT}")
        sections = parse_combined_txt(COMBINED_TXT)

    print(f"Parsed: {len(sections)} laws\n")
    for name, body in sections:
        print(f"  - {name[:70]}  ({len(body):,} chars)")

    if not sections:
        raise ValueError("No laws parsed — check your input file.")

    print('\nLoading embedding model...')
    t0    = time.time()
    model = SentenceTransformer(PRIMARY_EMBED, trust_remote_code=True)
    print(f'Model ready in {time.time()-t0:.1f}s\n')

    client   = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        print(f"Deleting old '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)
    client.create_collection(
        COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    print(f"Created fresh collection '{COLLECTION_NAME}'\n")

    total_chunks = 0
    for idx, (law_name, body) in enumerate(sections, 1):
        t_start = time.time()
        label   = law_name[:55] + ('…' if len(law_name) > 55 else '')
        print(f'[{idx:02d}/{len(sections):02d}] {label}', end=' ', flush=True)

        chunks = chunk_text(body)
        if not chunks:
            print('→ NO CHUNKS'); continue

        points = [
            PointStruct(
                id     = stable_id(chunk, law_name, i),
                vector = model.encode(chunk, normalize_embeddings=True).tolist(),
                payload={
                    'text':        chunk,
                    'file_name':   law_name,
                    'page_number': 0,
                    'article_ref': get_article_ref(chunk),
                },
            )
            for i, chunk in enumerate(chunks)
        ]
        client.upsert(COLLECTION_NAME, points=points)
        total_chunks += len(points)
        print(f'→ {len(points):4d} chunks  ({time.time()-t_start:.1f}s)')
        gc.collect()

    final_count = client.count(COLLECTION_NAME).count
    print(f"\n{'='*60}")
    print(f"  Laws ingested  : {len(sections)}")
    print(f"  Chunks added   : {total_chunks:,}")
    print(f"  Total vectors  : {final_count:,}")
    print(f"  Collection     : {COLLECTION_NAME}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main_ingest()