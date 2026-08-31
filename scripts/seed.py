import asyncio
import uuid

from sqlalchemy import select

from app.config import get_settings
from app.db.models import AgentTool, User, UserPlan
from app.db.session import create_engine, create_session_factory
from app.lib.security import hash_password
from app.services import (
    AgentService,
    ChatService,
    ProviderService,
    create_adr_service,
    create_story_service,
)
from app.services.provider_service import ApiKeyInput

EMAIL = "dev@invarix.local"
PASSWORD = "senha12345"

ADRS = [
    (
        "ADR-001 Banco de dados e busca vetorial",
        (
            "Usamos PostgreSQL com a extensao pgvector em vez de subir um Qdrant "
            "ou Weaviate separado. O volume esperado nao justifica outro servico "
            "para operar, e manter documento e embedding no mesmo banco permite "
            "filtrar por dono na mesma query da busca por similaridade."
        ),
    ),
    (
        "ADR-002 Autenticacao sem IdP",
        (
            "JWT HS256 assinado pela propria API, com senhas em argon2. Nao usamos "
            "Keycloak nem IdP hospedado porque o projeto precisa subir a partir de "
            "um clone mais docker compose, sem cadastro em servico externo."
        ),
    ),
    (
        "ADR-003 Chaves de API dos clientes",
        (
            "As chaves de provider dos clientes ficam cifradas em AES-256-GCM, com "
            "o AAD amarrado a provider_id mais api_key_id, para que um blob nao "
            "possa ser movido de linha. A chave de cifra vive fora do banco."
        ),
    ),
    (
        "ADR-004 Streaming de chat por websocket",
        (
            "O chat responde por websocket com eventos delta e done, em vez de SSE, "
            "porque o cliente tambem precisa enviar mensagens pela mesma conexao. "
            "O historico e remontado do banco a cada conexao."
        ),
    ),
]

STORIES = [
    (
        "STORY-001 Entrar na plataforma",
        (
            "Como usuario quero entrar com email e senha para acessar meus chats e "
            "meus documentos, e continuar logado por um dia sem repetir o login."
        ),
    ),
    (
        "STORY-002 Conversar com um agente",
        (
            "Como usuario quero abrir um chat com um agente configurado por mim e "
            "receber a resposta em streaming, vendo o texto aparecer aos poucos."
        ),
    ),
    (
        "STORY-003 Consultar decisoes antigas",
        (
            "Como tech lead quero que o agente busque nos ADRs que eu cadastrei "
            "antes de responder sobre arquitetura, citando qual decisao usou."
        ),
    ),
]


async def main() -> None:
    settings = get_settings()
    engine = create_engine()
    factory = create_session_factory(engine)

    async with factory() as session:
        existing = (
            await session.execute(select(User).where(User.email == EMAIL))
        ).scalar_one_or_none()
        if existing is not None:
            await session.delete(existing)
            await session.commit()
            print(f"usuario {EMAIL} anterior removido")

        user = User(
            id=uuid.uuid7(),
            name="Dev",
            email=EMAIL,
            password_hash=hash_password(PASSWORD),
            plan=UserPlan.OWN_AI,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"usuario   {user.email} / {PASSWORD} (plano {user.plan})")

        adrs = create_adr_service(session, user)
        for name, content in ADRS:
            await adrs.create(name=name, content=content)
        stories = create_story_service(session, user)
        for name, content in STORIES:
            await stories.create(name=name, content=content)
        print(f"documentos {len(ADRS)} ADRs e {len(STORIES)} stories com embeddings")

        if not settings.open_router_api_key:
            print("OPEN_ROUTER_API_KEY ausente: provider, agente e chat nao criados")
            await engine.dispose()
            return

        provider = await ProviderService(session, user).create(
            name="OpenRouter",
            kind="openrouter",
            api_keys=[ApiKeyInput(name="dev", secret=settings.open_router_api_key)],
        )
        api_key = provider.api_keys[0]
        print(f"provider  {provider.name} | chave dev ...{api_key.last4} (cifrada)")

        agent = await AgentService(session, user).create(
            name="Arquiteto",
            model="openrouter:deepseek/deepseek-v4-pro-0813",
            api_key_id=api_key.id,
            instructions=(
                "Voce e um assistente de arquitetura. Consulte os ADRs e as "
                "stories antes de responder e cite qual documento usou. Seja "
                "direto, no maximo tres frases."
            ),
            tools=[
                AgentTool.SEARCH_ADRS,
                AgentTool.SEARCH_STORIES,
                AgentTool.WEB_SEARCH,
            ],
        )
        print(f"agente    {agent.name} | tools {agent.tools}")

        chat = await ChatService(session, user).create(
            agent_id=agent.id, title="Primeiro chat"
        )
        print(f"chat      {chat.title} | ws /chats/{chat.id}/ws?token=<jwt>")

    await engine.dispose()


asyncio.run(main())
