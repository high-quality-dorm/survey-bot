run-bot:
	uv run -m bot

up:
	docker compose up -d

up-b:
	docker compose up -d --build

down:
	docker compose down

down-v:
	docker compose down --volumes

lint:
	uv run mypy src/
	uv run ruff check src/
	uv run ruff format src/ --check

format:
	uv run ruff check --select I --fix src/
	uv run ruff format src/