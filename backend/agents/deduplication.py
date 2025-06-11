# backend/agents/deduplication.py

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def deduplicate_chunks(chunks: list, threshold=0.92) -> list:
    """
    Deduplicates content chunks based on semantic similarity of their snippets.

    Args:
        chunks (list): List of dicts with a "snippet" key.
        threshold (float): Cosine similarity above which two snippets are considered duplicates.

    Returns:
        list: Filtered list of unique chunks.
    """
    if not chunks:
        return []

    texts = [chunk.get("snippet", "") for chunk in chunks]
    embeddings = model.encode(texts, convert_to_tensor=True)

    unique_chunks = []
    seen = set()

    for i in range(len(chunks)):
        if i in seen:
            continue
        unique_chunks.append(chunks[i])
        for j in range(i + 1, len(chunks)):
            if j not in seen:
                sim = util.cos_sim(embeddings[i], embeddings[j]).item()
                if sim > threshold:
                    seen.add(j)

    return unique_chunks