import re
class DocumentStatistics:
    """
    Calculates useful statistics about a parsed paper.
    """
    @staticmethod
    def analyze(paper):
        stats = {}
        # Basic statistics
        stats["title_length"] = len(paper.title)
        stats["author_count"] = len(paper.authors)
        stats["section_count"] = len(paper.sections)
        stats["reference_count"] = len(paper.references)
        stats["citation_count"] = len(paper.citations)
        # Text statistics
        words = paper.full_text.split()
        stats["word_count"] = len(words)
        stats["character_count"] = len(paper.full_text)
        sentences = re.split(
            r"[.!?]+",
            paper.full_text
        )
        sentences = [
            s.strip()
            for s in sentences
            if s.strip()
        ]
        stats["sentence_count"] = len(sentences)
        if sentences:
            stats["average_sentence_length"] = round(
                len(words) / len(sentences),
                2
            )
        else:
            stats["average_sentence_length"] = 0
        return stats