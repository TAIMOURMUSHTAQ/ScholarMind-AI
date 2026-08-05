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

        for i, item in enumerate(chunks, start=1):

            chunk = item[0] if isinstance(item, tuple) else item

            parts.append(
                f"""
==========================
Source {i}:
{chunk.title}

Pages:
{chunk.page_start}-{chunk.page_end}

Content:
{chunk.text}
"""
            )

        return "\n".join(parts)