from unittest.mock import patch

from app.rag import enrichment


@patch("app.rag.enrichment.GeminiClient.generate_json")
def test_generate_insight_card_returns_parsed_json(mock_generate_json):
    mock_generate_json.return_value = {
        "problem": "X is hard.",
        "method": "They did Y.",
        "key_results": ["Result 1"],
        "limitations": [],
        "contributions": ["Contribution 1"],
    }

    card = enrichment.generate_insight_card("Title", "Abstract", "Full text " * 2000)

    assert card["problem"] == "X is hard."
    # the excerpt sent to Gemini must be capped, not the whole document
    sent_message = mock_generate_json.call_args.args[1]
    assert len(sent_message) < 8000


@patch("app.rag.enrichment.GeminiClient.generate_json", return_value=["Computer Vision", " NLP ", "robotics"])
def test_generate_tags_normalizes_case_and_whitespace(mock_generate_json):
    tags = enrichment.generate_tags("Title", "Abstract")
    assert tags == ["computer vision", "nlp", "robotics"]


@patch("app.rag.enrichment.GeminiClient.generate_json", side_effect=RuntimeError("rate limited"))
def test_suggest_followups_degrades_to_empty_list_on_failure(mock_generate_json):
    assert enrichment.suggest_followups("Q?", "A.") == []


@patch("app.rag.enrichment.GeminiClient.generate_json", return_value=["Follow up one?", "", "Follow up two?"])
def test_suggest_followups_drops_blank_entries(mock_generate_json):
    assert enrichment.suggest_followups("Q?", "A.") == ["Follow up one?", "Follow up two?"]
