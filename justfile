set dotenv-load := true

# lista os comandos
default:
    @just --list

# sobe a api em modo dev (reload automatico)
[group('dev')]
dev:
    uv run fastapi dev app/api.py

# popula o banco com um usuario de teste, documentos, agente e chat
[group('dev')]
seed:
    uv run python -m scripts.seed

# gera uma chave nova pro ENCRYPTION_KEYS (ex: v1:...)
[group('dev')]
encryption-key version="v1":
    @uv run python -c "from app.lib.crypto import generate_key; print('{{version}}:' + generate_key())"

# sobe postgres + pgweb em background
[group('docker')]
up:
    docker compose up -d

# derruba os containers
[group('docker')]
down:
    docker compose down

# derruba os containers e apaga o volume do postgres
[group('docker')]
down-volumes:
    docker compose down -v

# logs dos containers
[group('docker')]
logs:
    docker compose logs -f

# gera migration a partir do diff dos models (ex: just migration-auto "add docs")
[group('migration')]
migration-auto message:
    uv run alembic revision --autogenerate -m "{{message}}"

# cria migration vazia pra escrever na mao (ex: just migration-empty "seed roles")
[group('migration')]
migration-empty message:
    uv run alembic revision -m "{{message}}"

# aplica migrations ate o alvo (padrao: head)
[group('migration')]
migration-up target="head":
    uv run alembic upgrade {{target}}

# desfaz migrations ate o alvo (padrao: uma pra tras)
[group('migration')]
migration-down target="-1":
    uv run alembic downgrade {{target}}

# historico das migrations, marcando a atual
[group('migration')]
migration-history:
    uv run alembic history --indicate-current

# revision aplicada no banco agora
[group('migration')]
migration-current:
    uv run alembic current
