"""
inspect_db.py — Inspect what's stored in the Qdrant server.
Run from your project root:
    python inspect_db.py
    python inspect_db.py --query "عقوبة الرشوة"
    python inspect_db.py --sample 5
"""
import argparse
from qdrant_client import QdrantClient

QDRANT_HOST     = "localhost"
QDRANT_PORT     = 6333
COLLECTION_NAME = "saudi_law"

def inspect(query=None, sample=3):
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # ── Collection stats ──────────────────────────────────────────────────────
    col   = client.get_collection(COLLECTION_NAME)
    total = client.count(COLLECTION_NAME).count
    dim   = col.config.params.vectors.size

    print(f"\n{'═'*60}")
    print(f"  Collection : {COLLECTION_NAME}")
    print(f"  Vectors    : {total:,}")
    print(f"  Dimensions : {dim}")
    print(f"{'═'*60}\n")

    # ── File breakdown ────────────────────────────────────────────────────────
    print("📂  Scanning files stored...")
    files = {}
    scroll_offset = None
    while True:
        results, scroll_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=500,
            offset=scroll_offset,
            with_vectors=False,
            with_payload=True,
        )
        if not results:
            break
        for p in results:
            fname = p.payload.get("file_name", "unknown")
            files[fname] = files.get(fname, 0) + 1
        if scroll_offset is None:
            break

    print(f"\n  {len(files)} files indexed:\n")
    for fname, count in sorted(files.items(), key=lambda x: -x[1]):
        print(f"  {count:>5} chunks  │  {fname[:70]}")

    # ── Sample random chunks ──────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  Sample of {sample} stored chunks:")
    print(f"{'─'*60}")
    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=sample,
        with_vectors=False,
        with_payload=True,
    )
    for i, p in enumerate(results, 1):
        pay = p.payload
        print(f"\n  [{i}] File    : {pay.get('file_name','?')}")
        print(f"       Page    : {pay.get('page_number','?')}")
        print(f"       Article : {pay.get('article_ref','—')}")
        print(f"       Text    : {pay.get('text','')[:200]}")

    # ── Optional: test a search query ─────────────────────────────────────────
    if query:
        print(f"\n{'─'*60}")
        print(f"  Search test: '{query}'")
        print(f"{'─'*60}")

        from sentence_transformers import SentenceTransformer
        print("  Loading model (this may take a moment)...")
        model = SentenceTransformer(
            "Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2",
            trust_remote_code=True,
        )
        vec = model.encode(query, normalize_embeddings=True).tolist()
        hits = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vec,
            limit=5,
        )
        print(f"\n  Top 5 results:\n")
        for i, h in enumerate(hits, 1):
            p = h.payload
            print(f"  [{i}] score={h.score:.4f}")
            print(f"       File : {p.get('file_name','?')}")
            print(f"       Art  : {p.get('article_ref','—')}")
            print(f"       Text : {p.get('text','')[:200]}")
            print()

    print(f"{'═'*60}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query",  default=None, help="Test search query in Arabic")
    parser.add_argument("--sample", default=3,    type=int, help="Number of sample chunks to show")
    args = parser.parse_args()
    inspect(query=args.query, sample=args.sample)