from typing import Any

from pydantic_ai import Agent
from pydantic_ai.models import Model, infer_model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers import Provider, infer_provider_class
from pydantic_ai.providers.openai import OpenAIProvider


def create_model(model: str, api_key: str, base_url: str | None = None) -> Model:
    if base_url is not None:
        _, _, model_name = model.rpartition(":")
        return OpenAIChatModel(
            model_name, provider=OpenAIProvider(base_url=base_url, api_key=api_key)
        )

    def provider_factory(name: str) -> Provider[Any]:
        provider_class: Any = infer_provider_class(name)
        return provider_class(api_key=api_key)

    return infer_model(model, provider_factory=provider_factory)


def create_agent(model: str, api_key: str, base_url: str | None = None) -> Agent:
    return Agent(model=create_model(model, api_key, base_url))
