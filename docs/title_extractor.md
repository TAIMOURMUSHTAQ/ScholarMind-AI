## Title Extractor

> **Historical note:** early design notes from the original CLI-only prototype. The title heuristic itself lives on in `backend/app/pdf/extractors.py`. See the top-level [README.md](../README.md) for the current architecture.

# Input
PDF Page
# Output
Document Title
Heuristics
Largest font
Near top of page
Ignore empty strings
Ignore "Abstract"
Ignore section headings
# Future Improvements
AI Ranking
Language Detection
Confidence Score