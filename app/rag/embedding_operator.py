import asyncio
import dashscope

from app.core.config import settings


async def query_to_vector(query):
    def embedding_sparse(query):
        resp = dashscope.TextEmbedding.call(
            api_key=settings.EMBEDDING_API_KEY,
            model=dashscope.TextEmbedding.Models.text_embedding_v4,
            input=query,
            dimension=1024,
            output_type="dense&sparse",
        )
        if resp.status_code == 200:
            sparse_vector = {item["index"]: item["value"] for item in resp.output["embeddings"][0]["sparse_embedding"]}
            dense_vector = resp.output["embeddings"][0]["embedding"]
            return sparse_vector, dense_vector
        return [], []

    sparse_vector, dense_vector = await asyncio.to_thread(embedding_sparse, query)
    return sparse_vector, dense_vector
