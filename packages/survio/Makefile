run:
	uv run python -m src.survio.main

test:
	uv run pytest tests

lint:
	uv run mypy src/survio
	uv run ruff check src/survio
	uv run ruff format src/survio --check

format:
	uv run ruff check --select I --fix src/survio
	uv run ruff format src/survio