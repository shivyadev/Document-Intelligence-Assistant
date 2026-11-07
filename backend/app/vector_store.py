import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

import faiss
import json
import numpy as np
from app.services.embeddings import generate_embeddings, embed_query


class FaissVectorStore:
    def __init__(self, dim=384, path="data/faiss/index.faiss"):
        self.path = path
        self.map_path = path + ".map.json"
        if os.path.exists(path) and os.path.exists(self.map_path):
            self.index = faiss.read_index(path)
            with open(self.map_path) as f:
                self.doc_of = {int(k): v for k, v in json.load(f).items()}
        else:
            self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
            self.doc_of = {}

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        faiss.write_index(self.index, self.path)
        with open(self.map_path, "w") as f:
            json.dump(self.doc_of, f)

    def add(self, chunk_ids, documents_id, vectors):
        ids = np.array(chunk_ids, dtype="int64")
        self.index.add_with_ids(vectors, ids)
        for cid, did in zip(chunk_ids, documents_id):
            self.doc_of[cid] = did

    def search(self, query_vector, k=5, document_ids=None):
        if self.index.ntotal == 0:
            return []
        
        q = query_vector.reshape(1,-1)
        fetch = self.index.ntotal if document_ids else min(k, self.index.ntotal)
        scores, ids = self.index.search(q, fetch)

        allowed = set(document_ids) if document_ids is not None else None
        results = []

        for cid, score in zip(ids[0], scores[0]):
            if cid == -1:
                continue
            if allowed is not None and self.doc_of.get(int(cid)) not in allowed:
                continue
            results.append((int(cid), float(score)))
            if len(results) == k:
                break
        return results

    