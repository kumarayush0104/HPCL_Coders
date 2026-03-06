# ==================================================
# HPCL ITEM MASTER — VERSION 2 (STABLE)
# FAISS + Historical Bootstrap + Numeric Guard
# (LAZY INIT FIX — STREAMLIT SAFE)
# ==================================================

import os
import re
import hashlib
from datetime import datetime

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(__file__)

PO_DATASET = os.path.join(BASE_DIR, "..", "synthetic_hpcl_po_data.csv")
ITEM_MASTER_CSV = os.path.join(BASE_DIR, "item_master.csv")
FAISS_INDEX_FILE = os.path.join(BASE_DIR, "item_index.faiss")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.75

# ---------------- TEXT NORMALIZATION ----------------
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)

    replacements = {
        "cs": "carbon steel",
        "ms": "mild steel",
        "ss": "stainless steel",
        "gi": "galvanised iron",
        "galvonised": "galvanised",
        "mm": " millimeter",
        "dia": "diameter",
        "od": "outer diameter"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return re.sub(r"\s+", " ", text).strip()

# ---------------- NUMERIC EXTRACTION ----------------
def extract_numbers(text: str):
    return re.findall(r"\d+(?:\.\d+)?", text)

# ---------------- ITEM CODE GENERATOR ----------------
def generate_item_code(text: str) -> str:
    return "HPCL-ITEM-" + hashlib.md5(text.encode()).hexdigest()[:10].upper()

# ---------------- LOAD EMBEDDING MODEL ----------------
model = SentenceTransformer(EMBEDDING_MODEL)

# ---------------- BOOTSTRAP FROM HISTORICAL PO DATA ----------------
def bootstrap_from_po_data():
    print("Bootstrapping item master from historical PO data...")

    df = pd.read_csv(PO_DATASET)

    if "item_description" not in df.columns:
        raise ValueError("PO dataset must contain 'item_description' column")

    unique_items = (
        df["item_description"]
        .dropna()
        .map(normalize)
        .unique()
        .tolist()
    )

    records = []
    descriptions = []

    for desc in unique_items:
        records.append({
            "item_code": generate_item_code(desc),
            "canonical_description": desc,
            "numbers": ",".join(extract_numbers(desc)),
            "created_at": datetime.now().isoformat()
        })
        descriptions.append(desc)

    embeddings = model.encode(
        descriptions,
        normalize_embeddings=True,
        show_progress_bar=True
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    item_df = pd.DataFrame(records)

    item_df.to_csv(ITEM_MASTER_CSV, index=False)
    faiss.write_index(index, FAISS_INDEX_FILE)

    print(f"Bootstrap completed: {len(item_df)} unique items")

    return item_df, index

# ==================================================
# LAZY INITIALIZATION (CRITICAL FIX)
# ==================================================
item_df = None
index = None

def _ensure_item_master_loaded():
    global item_df, index

    if item_df is not None and index is not None:
        return

    if os.path.exists(ITEM_MASTER_CSV) and os.path.exists(FAISS_INDEX_FILE):
        item_df = pd.read_csv(ITEM_MASTER_CSV)
        index = faiss.read_index(FAISS_INDEX_FILE)
    else:
        item_df, index = bootstrap_from_po_data()

# ---------------- MAIN CLASSIFICATION FUNCTION ----------------
def classify_item(description: str) -> dict:
    """
    Classify item description using:
    - FAISS semantic similarity
    - HARD numeric guard (engineering-safe)
    """

    _ensure_item_master_loaded()

    global item_df, index

    canonical = normalize(description)
    input_numbers = set(extract_numbers(canonical))

    embedding = model.encode(
        [canonical],
        normalize_embeddings=True
    ).astype("float32")

    # ---------- SEARCH TOP-K ----------
    if index.ntotal > 0:
        D, I = index.search(embedding, k=5)

        for score, idx in zip(D[0], I[0]):
            similarity = float(score)
            candidate = item_df.iloc[idx]

            candidate_numbers = set(
                str(candidate["numbers"]).split(",")
                if pd.notna(candidate["numbers"]) else []
            )

            # HARD CONSTRAINT: numeric mismatch → reject
            if input_numbers and candidate_numbers:
                if input_numbers != candidate_numbers:
                    continue

            if similarity >= SIMILARITY_THRESHOLD:
                return {
                    "item_code": candidate["item_code"],
                    "canonical_desc": candidate["canonical_description"],
                    "confidence": round(similarity, 3),
                    "status": "EXISTING"
                }

    # ---------- CREATE NEW ITEM ----------
    item_code = generate_item_code(canonical)

    new_row = {
        "item_code": item_code,
        "canonical_description": canonical,
        "numbers": ",".join(input_numbers),
        "created_at": datetime.now().isoformat()
    }

    item_df = pd.concat([item_df, pd.DataFrame([new_row])], ignore_index=True)
    index.add(embedding)

    # ---------- PERSIST ----------
    item_df.to_csv(ITEM_MASTER_CSV, index=False)
    faiss.write_index(index, FAISS_INDEX_FILE)

    return {
        "item_code": item_code,
        "canonical_desc": canonical,
        "confidence": 1.0,
        "status": "NEW_CREATED"
    }
