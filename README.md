# Adobe India Hackathon 2025 - Round 1B Submission

## 🚀 Project Title: Persona-Based Section Retrieval from PDF Documents

This project was submitted for **Round 1B** of the Adobe India Hackathon 2025. It focuses on retrieving the most relevant document sections from a set of PDFs based on a specific **persona** and **task**, using semantic similarity models.

---

## 📌 Problem Statement

Given a persona description and a task to accomplish, identify and extract the top 5 relevant sections across a set of PDF documents. This required identifying TOC headings, recipe-like heading patterns, and fallback paragraphs, then ranking them using sentence embeddings.

---

## 🛠️ Tech Stack

* Python
* PyMuPDF (fitz)
* Sentence Transformers (all-MiniLM-L6-v2)
* Docker (for containerization)

---

## 📁 Directory Structure

```
round1b/
├── collections/                # Contains folders for each test case
│   └── [test_case]/
│       ├── config.json         # Contains persona and task info
│       └── documents/         # PDF documents for this case
├── output/                    # Extracted section JSONs will be saved here
├── main.py                    # Main processing logic
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container setup
```

---

## ⚙️ How to Run

### ▶️ Option 1: Run with Docker

**Build Docker image:**

```bash
docker build -t adobe-round1b .
```

**Run the container:**

```bash
docker run --rm -v $(pwd)/collections:/app/collections -v $(pwd)/output:/app/output adobe-round1b
```

### ▶️ Option 2: Run Locally

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Run the script:**

```bash
python main.py
```

Make sure that the `collections/` folder is present and each test case folder inside it contains a valid `config.json` and `documents/` folder.

---

## ✅ Output Format

Each test case generates a JSON output in the `output/` folder. Example structure:

```json
{
  "metadata": {
    "input_documents": [...],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "section_title": "Relevant Heading",
      "importance_rank": 1,
      "page_number": 3
    },
    ...
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "Full page text...",
      "page_number": 3
    },
    ...
  ]
}
```

---



## 🏁 Final Notes

* Semantic similarity ensures relevance to the persona & task
* Robust fallback strategies when TOC or pattern-based headings are absent
* Docker setup allows for consistent execution across environments
