import sys, json, os
from sentence_transformers import SentenceTransformer
import chromadb

MODEL = SentenceTransformer('all-MiniLM-L6-v2')
DB_PATH = os.path.expanduser("~/pi-cwd-20260526/notebooklm_data/chroma_db")

def embed_and_store(notebook_id, source_id, filename, chunks):
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(f"notebook_{notebook_id}")

    texts = [c["text"] for c in chunks]
    embeddings = MODEL.encode(texts).tolist()

    collection.add(
        ids=[f"{source_id}_chunk_{i}" for i in range(len(chunks))],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "source_id": source_id,
            "filename": filename,
            "pages": json.dumps(c["pages"]),
            "chunk_index": c["index"]
        } for c in chunks]
    )
    return {"status": "ok", "chunks_stored": len(chunks)}

def search(notebook_id, query, top_k=5, threshold=0.3):
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(f"notebook_{notebook_id}")

    query_embed = MODEL.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embed,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    output = []
    for i in range(len(results["documents"][0])):
        dist = results["distances"][0][i]
        if dist < threshold:
            output.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": dist
            })
    return output

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "store":
        result = embed_and_store(sys.argv[2], sys.argv[3], sys.argv[4], json.loads(sys.argv[5]))
    elif action == "search":
        result = search(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 5)
    print(json.dumps(result, ensure_ascii=False))