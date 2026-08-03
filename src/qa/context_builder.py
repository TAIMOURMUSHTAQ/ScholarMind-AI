from src.models.chunks import Chunk


class ContextBuilder:
    """
    Builds a prompt context from retrieved chunks.
    """

    @staticmethod
    def build(chunks):
        """
        Convert a list of Chunk objects into one context string.
        """

        if not chunks:
            return ""

        parts = []

        for chunk in chunks:

            parts.append(
                f"""
==========================
Section:
{chunk.title}

Content:
{chunk.text}
"""
            )

        return "\n".join(parts)