# build_index.py
import os
import json
import numpy as np
import faiss
from docx import Document
from sentence_transformers import SentenceTransformer

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEALS_FOLDER = os.path.join(BASE_DIR, "../Documents")
FAISS_FILE = os.path.join(MEALS_FOLDER, "meals.index")
MEAL_IDS_FILE = os.path.join(MEALS_FOLDER, "meal_ids.json")

MODEL_NAME = "sentence-transformers/LaBSE"


# Read DOCX as text
def read_docx_clean(path: str) -> str:
    """Extract clean semantic text from DOCX without overcleaning."""
    doc = Document(path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not lines:
        return ""

    title = lines[0]
    body = " ".join(lines[1:])

    return f"{title}. {body}"


def load_documents(folder: str):
    texts = []
    ids = []

    for filename in os.listdir(folder):
        if not filename.lower().endswith(".docx"):
            continue

        filepath = os.path.join(folder, filename)
        meal_id = filename.replace(".docx", "")

        text = read_docx_clean(filepath)
        if not text:
            continue

        texts.append(text)
        ids.append(meal_id)

    return texts, ids


# Build Index
def build_index():
    print("====================================")
    print("       Building FAISS Index")
    print("====================================")

    if not os.path.exists(MEALS_FOLDER):
        raise FileNotFoundError("Documents folder not found!")

    print("Loading documents...")
    texts, ids = load_documents(MEALS_FOLDER)

    if not texts:
        raise ValueError("No DOCX files found!")

    print(f"✓ Loaded {len(texts)} meal documents")

    print("Loading LaBSE model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Encoding documents...")
    embeddings = model.encode(texts, batch_size=8, show_progress_bar=True)

    embeddings = np.array(embeddings, dtype="float32")

    # Normalize for cosine similarity
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)

    dim = embeddings.shape[1]
    print(f"Embedding dimension: {dim}")

    print("Creating FAISS IndexFlatIP...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    print(f"✓ Index built with {index.ntotal} vectors")

    # Save FAISS index
    faiss.write_index(index, FAISS_FILE)
    print(f"✓ Saved index → {FAISS_FILE}")

    # Save ID mapping
    with open(MEAL_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved meal ids → {MEAL_IDS_FILE}")

    print("====================================")
    print("Index build completed successfully!")
    print("====================================")


if __name__ == "__main__":
    build_index()