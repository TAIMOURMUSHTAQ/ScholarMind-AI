# ScholarMind AI End-to-End Documentation

> **Historical note:** this describes the original CLI-only prototype, superseded by the `backend/`/`frontend/` rebuild. See the top-level [README.md](../README.md) for the current architecture.

## Overview

ScholarMind AI is a research-oriented document intelligence assistant built around academic PDFs. The current product base is designed to:

- ingest a scholarly paper,
- extract structured content,
- index the extracted chunks for semantic retrieval,
- answer questions about the paper,
- and export the result into durable research artifacts.

The system is intentionally paper-centric rather than general-web-centric. Its behavior should favor grounded answers, source traceability, and reproducible outputs over open-ended chat.

## Research Use Case

This project is suited for:

- literature review support,
- paper triage and summarization,
- metadata extraction,
- section-level navigation,
- citation and reference inspection,
- and question answering over a single paper or a small paper set.

It is not intended to replace peer review or provide unverified scientific claims. The assistant should always prefer answers grounded in the parsed document and should clearly indicate when the source material does not contain the requested information.

## Architecture

The pipeline is organized as follows:

1. A PDF is opened and parsed.
2. Layout blocks are ordered into a reading sequence.
3. Title, authors, abstract, sections, citations, references, and metadata are extracted.
4. The paper is split into semantic chunks.
5. Chunks are embedded and stored in a FAISS vector index.
6. The retriever returns the most relevant chunks for a question.
7. The prompt builder prepares a research-safe prompt.
8. Gemini is used when configured; otherwise the assistant falls back to paper-grounded responses.
9. The parsed paper is exported to Markdown and JSON for downstream use.

## Main Components

### `main.py`

The command-line entrypoint coordinates the full workflow.

Supported options:

- `--pdf PATH` - analyze a specific PDF.
- `--ask প্রশ্ন` - ask one question and exit.
- `--chat` - start interactive QA mode.
- `--top-k N` - control retrieval depth.
- `--verbose` - print parser diagnostics.

### Parser Layer

The parser turns a PDF into a `Paper` object. The object stores:

- title,
- authors,
- abstract,
- keywords,
- full text,
- sections,
- citations,
- references,
- metadata,
- statistics,
- and semantic chunks.

This separation is important for research workflows because it preserves the paper as a structured object instead of collapsing everything into a single text blob.

### Retrieval Layer

The retrieval path combines embeddings and vector search. Given a question, the system:

- encodes the query,
- searches the FAISS index,
- ranks chunk matches,
- and feeds the best matches into the QA layer.

The system now also reports sources so the answer can be traced back to the parsed paper.

### QA Layer

The QA layer is responsible for:

- building context from retrieved chunks,
- composing a question-specific prompt,
- calling the LLM when available,
- and falling back to paper-aware responses when the model is unavailable.

For research use, this layer should remain conservative. It is better to answer with a traceable “not found in the paper” response than to invent unsupported claims.

### Export Layer

The exporters generate two artifacts:

- Markdown for quick reading and human review.
- JSON for machine use, indexing, or post-processing.

These outputs are useful for research notebooks, report generation, and auditing extraction quality.

## Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

If the key is omitted, ScholarMind AI still supports parsing, exporting, indexing, and paper-grounded fallback answers for simple factual questions.

### Model Notes

The current Gemini client uses the Google Generative AI package available in the repository. A warning may appear indicating that the package is deprecated. The project still runs, but the long-term improvement is to migrate to `google.genai`.

## Setup

1. Install Python 3.13 or the version used by your workspace.
2. Create and activate a virtual environment.
3. Install dependencies from `requirements.txt`.
4. Copy `.env.example` to `.env`.
5. Add `GEMINI_API_KEY` if you want live LLM answers.

## Running the Assistant

### Parse the sample paper

```bash
python main.py
```

### Ask a single question

```bash
python main.py --ask "What is the title of the paper?"
```

### Start interactive QA

```bash
python main.py --chat
```

### Analyze a different PDF

```bash
python main.py --pdf "data/sample_pdfs/your_paper.pdf"
```

## Output Artifacts

- `output/paper.md` - readable paper summary.
- `output/paper.json` - structured export.
- `indexes/paper.index` - vector index for retrieval.

## Research-Focused Design Rules

For this project, the assistant should follow these rules:

- Prefer grounded answers over creative answers.
- Expose source snippets or rankings whenever possible.
- Keep extracted structure visible for inspection.
- Preserve research metadata and paper statistics.
- Make the output reproducible so that results can be rerun on the same paper.

## Validation Checklist

Before shipping a change, verify:

- `python main.py` completes successfully.
- `python main.py --ask "What is the title of the paper?"` returns a grounded answer.
- `output/paper.md` and `output/paper.json` are regenerated.
- The vector index is written to `indexes/paper.index`.
- Chat mode still works when `GEMINI_API_KEY` is available.

## Known Follow-Ups

- Migrate the Gemini client to `google.genai`.
- Replace the remaining debug-style parser prints with logger-based diagnostics.
- Add automated tests for `main.py --ask` and the retrieval/QA layer.
- Consider a batch mode for analyzing multiple papers in one run.

## Suggested Research Extensions

- multi-paper literature comparison,
- citation network analysis,
- table and figure extraction,
- section-level summarization,
- related-work synthesis,
- and claim-to-evidence tracing.
