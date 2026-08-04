import faiss
import numpy as np
from pathlib import Path


class VectorStore:
    """
    Handles storing and loading vector embeddings.
    """

    def __init__(self):

        self.index = None

    def build(self, chunks):

        embeddings = np.array(
            [chunk.embedding for chunk in chunks],
            dtype="float32"
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.index.add(
            embeddings
        )

        return self.index

    def save(self, folder):

        folder = Path(folder)

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(folder / "paper.index")
        )

    def load(self, folder):

        folder = Path(folder)

        self.index = faiss.read_index(
            str(folder / "paper.index")
        )

        return self.index