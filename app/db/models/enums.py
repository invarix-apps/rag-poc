from enum import StrEnum


def enum_values(enum: type[StrEnum]) -> list[str]:
    return [member.value for member in enum]


class UserPlan(StrEnum):
    NO_AI = "no_ai"
    SYSTEM_AI = "system_ai"
    OWN_AI = "own_ai"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class AgentTool(StrEnum):
    WEB_SEARCH = "web_search"
    SEARCH_ADRS = "search_adrs"
    SEARCH_STORIES = "search_stories"
