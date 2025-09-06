import faiss
import pickle
from sentence_transformers import SentenceTransformer
from db import SessionLocal
from models import KBDoc

INDEX_PATH = "data/kb.index"
MODEL_NAME = "all-MiniLM-L6-v2"

def build_index():
    session = SessionLocal()
    docs = session.query(KBDoc).all()
    session.close()

    if not docs:
        print("⚠️ No KB docs found. Add some into kb_docs table first.")
        return

    texts = [d.content for d in docs]
    ids = [d.id for d in docs]

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, convert_to_numpy=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # Save both index + mapping
    with open("data/kb_mapping.pkl", "wb") as f:
        pickle.dump(ids, f)
    faiss.write_index(index, INDEX_PATH)

    print(f"✅ KB index built with {len(docs)} docs.")

def query_kb(query: str, top_k=2):
    try:
        # Check if index files exist
        import os
        if not os.path.exists(INDEX_PATH) or not os.path.exists("data/kb_mapping.pkl"):
            print("⚠️ Knowledge base index not found. Building index first...")
            build_index()
            # If build_index returns without creating files, return empty results
            if not os.path.exists(INDEX_PATH):
                print("⚠️ No knowledge base documents available.")
                return []

        model = SentenceTransformer(MODEL_NAME)
        emb = model.encode([query], convert_to_numpy=True)

        index = faiss.read_index(INDEX_PATH)
        with open("data/kb_mapping.pkl", "rb") as f:
            ids = pickle.load(f)

        D, I = index.search(emb, top_k)

        session = SessionLocal()
        results = []
        for idx in I[0]:
            if idx < len(ids):  # Prevent index out of range
                doc = session.query(KBDoc).get(ids[idx])
                if doc:
                    results.append(doc.content)
        session.close()
        return results
    
    except Exception as e:
        print(f"⚠️ Knowledge base query failed: {e}")
        return []
