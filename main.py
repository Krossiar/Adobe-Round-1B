import os
import json
import re
from datetime import datetime
import fitz  # PyMuPDF
from collections import Counter
from sentence_transformers import SentenceTransformer, util

# ─── CONFIG ──────────────────────────────────────────────────────────
COLLECTIONS_DIR = "collections"    # top‐level folder containing one folder per test case
OUTPUT_DIR      = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── MODEL ───────────────────────────────────────────────────────────
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ─── HELPERS ─────────────────────────────────────────────────────────
def extract_toc(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc() or []
    doc.close()
    # return only levels 1–3
    return [(lvl, title.strip(), page) for lvl, title, page in toc
            if 1 <= lvl <= 3 and title.strip()]

def extract_recipe_headings(pdf_path):
    """Look for lines immediately before an “• Ingredients:” bullet."""
    doc = fitz.open(pdf_path)
    found = []
    for pno in range(len(doc)):
        text = doc.load_page(pno).get_text("text").splitlines()
        for i, line in enumerate(text[:-1]):
            line_str = line.strip()
            nxt = text[i+1].lstrip()
            if line_str and not line_str.startswith("•") and "Ingredients:" in nxt:
                found.append((1, line_str, pno+1))
    doc.close()
    return found

def extract_paragraphs(pdf_path, max_per=8):
    """Grab up to `max_per` text‐blocks of ≥12 words from the start of each PDF."""
    doc = fitz.open(pdf_path)
    paras = []
    for pno in range(len(doc)):
        for block in doc.load_page(pno).get_text("blocks"):
            txt = block[4].strip().replace("\n", " ")
            if len(txt.split()) >= 12:
                paras.append((txt, pno+1))
                if len(paras) >= max_per:
                    break
        if len(paras) >= max_per:
            break
    doc.close()
    return paras

def clean(s: str):
    s = s.replace("\u2022", "-")            # normalize bullets
    return re.sub(r"\s+", " ", s).strip()   # collapse whitespace

def rank_items(texts, query, top_k=20):
    emb = model.encode(texts, convert_to_tensor=True)
    qemb = model.encode([query], convert_to_tensor=True)[0]
    sims = util.cos_sim(qemb, emb)[0]
    idxs = sorted(range(len(texts)), key=lambda i: sims[i], reverse=True)
    return idxs[:top_k]

# ─── PROCESS ONE COLLECTION ──────────────────────────────────────────
def process_collection(coll_dir):
    cfg_path = os.path.join(coll_dir, "config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    persona = cfg["persona"]["role"]
    task    = cfg["job_to_be_done"]["task"]
    docs    = cfg["documents"]
    docs_dir= os.path.join(coll_dir, "documents")

    # gather all (lvl,title,page,docname)
    candidates = []
    for d in docs:
        fn = d["filename"]
        path = os.path.join(docs_dir, fn)
        if not os.path.isfile(path):
            continue
        # 1) TOC
        for lvl, t, pg in extract_toc(path):
            candidates.append((t, fn, pg))
        # 2) Recipe headings
        for lvl, t, pg in extract_recipe_headings(path):
            candidates.append((t, fn, pg))

    # 3) fallback paragraphs if still nothing
    if not candidates:
        for d in docs:
            fn = d["filename"]
            path = os.path.join(docs_dir, fn)
            if not os.path.isfile(path):
                continue
            for txt, pg in extract_paragraphs(path):
                candidates.append((txt, fn, pg))

    # build output skeleton
    out = {
        "metadata": {
            "input_documents": [d["filename"] for d in docs],
            "persona": persona,
            "job_to_be_done": task,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    if candidates:
        texts = [c[0] for c in candidates]
        query = f"{persona}. Task: {task}"
        ranked = rank_items(texts, query)

        used = Counter()
        picked = []
        for idx in ranked:
            doc = candidates[idx][1]
            if used[doc] < 2:
                picked.append(idx)
                used[doc] += 1
            if len(picked) >= 5:
                break

        for rank, idx in enumerate(picked, start=1):
            txt, fn, pg = candidates[idx]
            # open page, extract full text
            pdf = fitz.open(os.path.join(docs_dir, fn))
            page = pdf.load_page(pg-1)
            full = clean(page.get_text("text"))
            pdf.close()

            # truncate heading if too long
            h = txt if len(txt.split())<=10 else " ".join(txt.split()[:10])+"..."

            out["extracted_sections"].append({
                "document": fn,
                "section_title": h,
                "importance_rank": rank,
                "page_number": pg
            })
            out["subsection_analysis"].append({
                "document": fn,
                "refined_text": full,
                "page_number": pg
            })

    # write
    cid = cfg["challenge_info"]["challenge_id"]
    tnm = cfg["challenge_info"]["test_case_name"]
    ofn = f"{cid}_{tnm}.json"
    with open(os.path.join(OUTPUT_DIR, ofn), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved → {ofn}")

# ─── RUN ALL ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    for coll in sorted(os.listdir(COLLECTIONS_DIR)):
        cpath = os.path.join(COLLECTIONS_DIR, coll)
        if os.path.isdir(cpath):
            print(f"\nProcessing collection: {coll}")
            process_collection(cpath)
