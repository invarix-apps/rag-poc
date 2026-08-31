from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from typing import Annotated, Any

from pydantic import Field
from pydantic_ai import Tool
from pydantic_ai.capabilities import AgentCapability, WebSearch

from app.db.models import AgentTool
from app.errors import UnknownAgentToolError
from app.services.document_search_service import MAX_RESULTS, DocumentSearchService

DEFAULT_RESULTS = 5

Limit = Annotated[int, Field(ge=1, le=MAX_RESULTS)]


@dataclass(frozen=True, kw_only=True)
class AgentToolkit:
    tools: list[Tool[None]] = field(default_factory=list)
    capabilities: list[AgentCapability[None]] = field(default_factory=list)


def build_toolkit(names: Sequence[str], search: DocumentSearchService) -> AgentToolkit:
    tools: list[Tool[None]] = []
    capabilities: list[AgentCapability[None]] = []

    for name in dict.fromkeys(names):
        tool = parse_tool(name)
        if tool is AgentTool.WEB_SEARCH:
            capabilities.append(WebSearch())
        else:
            tools.append(FUNCTION_TOOLS[tool](search))

    return AgentToolkit(tools=tools, capabilities=capabilities)


def parse_tool(name: str) -> AgentTool:
    try:
        return AgentTool(name)
    except ValueError as exc:
        raise UnknownAgentToolError(
            f"Ferramenta desconhecida: {name}",
            details={"allowed": [t.value for t in AgentTool]},
        ) from exc


def build_adr_search(search: DocumentSearchService) -> Tool[None]:
    async def search_adrs(
        query: str, limit: Limit = DEFAULT_RESULTS
    ) -> list[dict[str, Any]]:
        return __serialize(await search.search_adrs(query, limit))

    return Tool(
        search_adrs,
        name=AgentTool.SEARCH_ADRS.value,
        description=(
            "Busca nos ADRs do usuario por similaridade semantica. Devolve ate "
            f"{MAX_RESULTS} resultados rankeados, do mais para o menos relevante, "
            "com o conteudo completo de cada ADR. Use para decisoes de arquitetura "
            "ja registradas."
        ),
    )


def build_story_search(search: DocumentSearchService) -> Tool[None]:
    async def search_stories(
        query: str, limit: Limit = DEFAULT_RESULTS
    ) -> list[dict[str, Any]]:
        return __serialize(await search.search_stories(query, limit))

    return Tool(
        search_stories,
        name=AgentTool.SEARCH_STORIES.value,
        description=(
            "Busca nas stories do usuario por similaridade semantica. Devolve ate "
            f"{MAX_RESULTS} resultados rankeados, do mais para o menos relevante, "
            "com o conteudo completo de cada story. Use para requisitos e escopo "
            "ja registrados."
        ),
    )


def __serialize(matches: Sequence[Any]) -> list[dict[str, Any]]:
    return [{**asdict(match), "id": str(match.id)} for match in matches]


FUNCTION_TOOLS: dict[AgentTool, Callable[[DocumentSearchService], Tool[None]]] = {
    AgentTool.SEARCH_ADRS: build_adr_search,
    AgentTool.SEARCH_STORIES: build_story_search,
}
