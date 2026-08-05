# ScholarMind AI

ScholarMind AI is a research-focused PDF intelligence assistant. It parses scholarly papers, extracts structured metadata, generates semantic chunks and embeddings, exports results to Markdown and JSON, and supports question answering over a parsed paper.

## What it does

- Parses academic PDFs into a structured `Paper` object.
- Extracts title, authors, abstract, sections, citations, references, and metadata.
- Generates chunks and embeddings for semantic retrieval.
- Exports parsed results to `output/paper.md` and `output/paper.json`.
- Supports one-shot questions with `--ask` and interactive chat with `--chat`.
- Falls back to paper-aware answers for common facts when Gemini is unavailable.

## Project Structure

- `main.py` - command-line entrypoint.
- `src/parser/` - PDF-to-paper pipeline.
- `src/extractors/` - title, author, abstract, section, citation, reference, and metadata extractors.
- `src/chunking/` and `src/embeddings/` - chunk generation and embedding creation.
- `src/vectorstore/` and `src/search/` - semantic retrieval.
- `src/chat/` and `src/qa/` - question answering, context building, and prompt construction.
- `src/exporters/` - Markdown and JSON export.
- `docs/` - research-oriented documentation.

## Quick Start

1. Create a virtual environment and install dependencies from `requirements.txt`.
2. Copy `.env.example` to `.env`.
3. Add your Gemini API key to `.env` if you want live LLM responses.
4. Run the sample paper workflow:

```bash
python main.py
```

5. Ask a question directly:

```bash
python main.py --ask "What is the title of the paper?"
```

6. Start interactive chat:

```bash
python main.py --chat
```

## Configuration

The assistant reads `GEMINI_API_KEY` from `.env`.

```env
GEMINI_API_KEY=your_api_key_here
```

If the key is missing, ScholarMind AI still runs and answers common paper facts from the parsed document.

## Outputs

- `output/paper.md` - human-readable parsed summary.
- `output/paper.json` - structured machine-readable export.
- `indexes/paper.index` - FAISS vector index for semantic search.

## Documentation

For the full end-to-end guide, see [docs/end_to_end_documentation.md](docs/end_to_end_documentation.md).

For architecture background, see [docs/architecture_v1.md](docs/architecture_v1.md).