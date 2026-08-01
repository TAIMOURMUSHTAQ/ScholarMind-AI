from src.models.chunks import Chunk


class ChunkGenerator:
    """
    Generates semantic chunks from paper sections.
    """

    MAX_WORDS = 300

    @staticmethod
    def generate(sections):

        chunks = []

        chunk_id = 1

        for section in sections:

            words = section.content.split()

            current_words = []

            for word in words:

                current_words.append(word)

                if len(current_words) >= ChunkGenerator.MAX_WORDS:

                    chunks.append(

                        Chunk(
                            id=chunk_id,
                            title=section.title,
                            text=" ".join(current_words),
                            page_start=0,
                            page_end=0,
                            word_count=len(current_words)
                        )

                    )

                    chunk_id += 1

                    current_words = []

            if current_words:

                chunks.append(

                    Chunk(
                        id=chunk_id,
                        title=section.title,
                        text=" ".join(current_words),
                        page_start=0,
                        page_end=0,
                        word_count=len(current_words)
                    )

                )

                chunk_id += 1

        return chunks