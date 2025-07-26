## Persona-Driven Document Intelligence (Round 1B)

This solution supports batch processing of PDF collections, each defined by an `input.json` file. Each collection corresponds to one query job for a specific persona and task.

### Workflow

1. For each collection folder:
   - Load `input.json` containing:
     - persona
     - job description
     - document filenames
2. Extract all meaningful text paragraphs from PDFs using `PyMuPDF`.
3. Rank relevance using `MiniLM-L6-v2` transformer model and cosine similarity.
4. Output results in a single JSON per collection in `output/`.

### Constraints Handled

- Runs entirely on CPU (no GPU)
- Works offline
- Uses small model (~80MB)
- Handles 3–10 PDFs per task
