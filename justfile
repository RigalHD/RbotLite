set windows-powershell := true

dev:
    just down
    docker compose -f compose.dev.yaml up --build

down:
    docker compose -f compose.dev.yaml down

clear:
    docker compose -f compose.dev.yaml down -v

lint:
    ruff format
    ruff check --fix
    mypy

migration MESSAGE:
    uv run rbot migrations create "{{MESSAGE}}"

prod:
    just prod-down
    docker compose -f compose.prod.yaml up --build -d

prod-down:
    docker compose -f compose.prod.yaml down

prod-clear:
    docker compose -f compose.prod.yaml down -v
