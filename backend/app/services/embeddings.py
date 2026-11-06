from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME, device="cpu")

def generate_embeddings(chunks):
    if not chunks:
        return []

    texts = [chunk['text'] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,
    )

    return embeddings.astype("float32")

def embed_query(question):
    return model.encode(
        question, 
        convert_to_numpy=True,
        normalize_embeddings=True
        ).astype("float32")

