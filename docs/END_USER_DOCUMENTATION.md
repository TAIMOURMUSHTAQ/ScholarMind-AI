ScholarMind AI — End User Documentation

Overview
--------
ScholarMind AI parses academic PDF papers, extracts structure (title, authors, abstract, sections, references), generates semantic chunks with embeddings, supports a simple semantic search and a chat interface that answers questions from the supplied paper context.

This repository is intended as a local research assistant pipeline. The code attempts to be resilient when optional heavy dependencies (FAISS for indexing, SentenceTransformers, or the Gemini LLM client) are not available.

Key features
------------
- Parse PDF papers to structured Paper objects (title, authors, sections, references).
- Split document into semantic chunks and compute embeddings.
- Build a vector index (faiss when available; numpy fallback otherwise).
- Semantic search over chunks.
- Chat interface that uses retrieved context and an LLM (optional).
- Export parsed results as JSON and Markdown.

Quick start
-----------
1. Ensure Python 3.9+ is installed.
2. (Optional) Create and activate a virtual environment:
   python -m venv .venv
   .\\.venv\\Scripts\\activate

3. Install dependencies (use the provided requirements file; names may vary):
   pip install -r requirments.txt

   Note: The project contains optional integrations. If you want the full features:
   - Install faiss (for example: pip install faiss-cpu) to use a fast index.
   - Install sentence-transformers: pip install sentence-transformers
   - Install google.generativeai and set GEMINI_API_KEY for Gemini LLM integration.

4. Place your PDF file into data/sample_pdfs/ and name it sample_conference_paper.pdf or update main.py paths accordingly.

5. Run the application:
   python main.py

   The script will parse the PDF, build the index (or fallback), print extracted information to the console, export JSON/Markdown into the output/ folder, and present a chat prompt.

Environment variables
---------------------
- GEMINI_API_KEY (optional): If set and the google.generativeai package is installed, the chat engine will send prompts to Gemini. If not set, the app will continue in offline mode and provide a helpful message instead of crashing.

Files and modules of interest
-----------------------------
- main.py: example command-line entrypoint that demonstrates the whole pipeline.
- src/parser/paper_parser.py: orchestrates PDF parsing and downstream processing.
- src/embeddings/embedding_generator.py: wraps SentenceTransformer embedding generation.
- src/vectorstore/vector_store.py: index interface with faiss + numpy fallback.
- src/search/semantic_search.py: performs query encoding and uses the vector store for search.
- src/retrieval/retriever.py: normalizes search results into Chunk objects.
- src/chat/chat_engine.py: builds prompts and queries an LLM (optional) to answer user questions.
- src/exporters: JSON and Markdown exporters.

Troubleshooting & notes
-----------------------
- If the program fails with import errors, ensure the optional packages are installed as needed. The code is designed to fail gracefully in many places, but installing sentence-transformers is recommended for embedding generation.

- If no PDF is found, main.py currently lists files found in the sample_pdfs folder and exits.

- If you plan to use an LLM other than Gemini, update src/llm/gemini_client.py or implement a different client class and pass it into ChatEngine.

Contributing
------------
This project follows a modular structure. When making changes:
- Keep logic in small, well-documented functions.
- Update or add unit tests in the tests/ folder where appropriate.

License
-------
See LICENSE at the repository root.

Contact
-------
Repository: TAIMOURMUSHTAQ/ScholarMind-AI
