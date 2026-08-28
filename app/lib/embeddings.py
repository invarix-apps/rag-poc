from functools import lru_cache

from pydantic_ai.embeddings import EmbeddingSettings
from pydantic_ai.embeddings.google import GoogleEmbeddingModel
from pydantic_ai.providers.google import GoogleProvider

from app.config import get_settings
from app.errors import MissingEmbeddingApiKeyError


@lru_cache
def get_embedding_model() -> GoogleEmbeddingModel:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise MissingEmbeddingApiKeyError()

    return GoogleEmbeddingModel(
        settings.embedding_model,
        provider=GoogleProvider(api_key=settings.gemini_api_key),
        settings=EmbeddingSettings(dimensions=settings.embedding_dimensions),
    )


async def embed_document(text: str) -> tuple[str, list[float]]:
    model = get_embedding_model()
    result = await model.embed(text, input_type="document")
    return model.model_name, list(result.embeddings[0])
