import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

import faiss
import numpy as np
from app.services.embeddings import generate_embeddings, embed_query


class FaissVectorStore:
    def __init__(self, dim=384, path="data/faiss/index.faiss"):
        self.path = path
        if os.path.exists(path):
            self.index = faiss.read_index(path)
        else:
            self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        faiss.write_index(self.index, self.path)

    def add(self, chunk_ids, vectors):
        ids = np.array(chunk_ids, dtype="int64")
        self.index.add_with_ids(vectors, ids)

    def search(self, query_vector, k=5):
        q = query_vector.reshape(1,-1)
        scores, ids = self.index.search(q, k)

        return [
            (int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i != -1
        ]

if __name__ == "__main__":

    texts = [
        "Cats are small furry pets that purr.",
        "The stock market fell sharply on Monday.",
        "Dogs are loyal animals that love walks.",
    ]
    fake_chunks = [{"text": t} for t in texts]
    vectors = generate_embeddings(fake_chunks)

    store = FaissVectorStore()
    store.add([101, 102, 103], vectors)

    results = store.search(embed_query("Which animal is good for walking?"), k=3)
    for chunk_id, score in results:
        print(chunk_id, round(score, 3))
    