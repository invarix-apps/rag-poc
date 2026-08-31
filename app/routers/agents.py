import uuid

from fastapi import APIRouter, status

from app.dependencies import AgentServiceDep
from app.schemas import AgentCreate, AgentResponse, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: AgentCreate, service: AgentServiceDep
) -> AgentResponse:
    agent = await service.create(
        name=payload.name,
        model=payload.model,
        api_key_id=payload.api_key_id,
        instructions=payload.instructions,
        tools=payload.tools,
    )
    return AgentResponse.model_validate(agent)


@router.get("")
async def list_agents(service: AgentServiceDep) -> list[AgentResponse]:
    return [AgentResponse.model_validate(a) for a in await service.list()]


@router.get("/{agent_id}")
async def get_agent(agent_id: uuid.UUID, service: AgentServiceDep) -> AgentResponse:
    return AgentResponse.model_validate(await service.get(agent_id))


@router.patch("/{agent_id}")
async def update_agent(
    agent_id: uuid.UUID, payload: AgentUpdate, service: AgentServiceDep
) -> AgentResponse:
    agent = await service.update(
        agent_id,
        name=payload.name,
        model=payload.model,
        api_key_id=payload.api_key_id,
        instructions=payload.instructions,
        tools=payload.tools,
    )
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: uuid.UUID, service: AgentServiceDep) -> None:
    await service.delete(agent_id)
