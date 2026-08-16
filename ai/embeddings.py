from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunk: list[str]):
    if not chunk or chunk == "":
        raise ValueError("Please provide a valid chunk")

    result = model.encode(chunk, normalize_embeddings=True)
    embedded_chunk = result.tolist()
    return embedded_chunk

def embed_query(query: str):
    if not query or query.strip() == "":
        raise ValueError("Please provide a valid chunk")

    result = model.encode(query, normalize_embeddings=True)
    embedded_query = result.tolist()
    return embedded_query

