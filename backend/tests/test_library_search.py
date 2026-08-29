from unittest.mock import patch

from app.rag.library_search import search_library


def _paper(id_, title, status="ready"):
    return {"id": id_, "title": title, "filename": f"{id_}.pdf", "status": status}


@patch("app.rag.library_search.EmbeddingGenerator.embed_query", return_value=[0.1, 0.2, 0.3])
@patch("app.rag.library_search.PaperStore.list_all")
@patch("app.rag.library_search.VectorStore.query")
def test_search_merges_and_ranks_results_across_papers(mock_query, mock_list_all, mock_embed):
    mock_list_all.return_value = [_paper("p1", "Paper One"), _paper("p2", "Paper Two")]

    def fake_query(paper_id, embedding, top_k):
        if paper_id == "p1":
            return [{"text": "low relevance", "section_title": "Intro", "page_start": 0, "page_end": 0, "score": 0.2}]
        return [{"text": "high relevance", "section_title": "Results", "page_start": 3, "page_end": 3, "score": 0.9}]

    mock_query.side_effect = fake_query

    results = search_library("some query", limit=10)

    assert results[0]["paper_id"] == "p2"
    assert results[0]["paper_title"] == "Paper Two"
    assert results[0]["score"] == 0.9
    assert results[1]["paper_id"] == "p1"


@patch("app.rag.library_search.EmbeddingGenerator.embed_query", return_value=[0.1, 0.2, 0.3])
@patch("app.rag.library_search.PaperStore.list_all")
@patch("app.rag.library_search.VectorStore.query")
def test_search_skips_papers_that_are_not_ready(mock_query, mock_list_all, mock_embed):
    mock_list_all.return_value = [_paper("p1", "Processing paper", status="processing")]

    results = search_library("query")

    mock_query.assert_not_called()
    assert results == []


def test_search_with_blank_query_returns_no_results():
    assert search_library("   ") == []
