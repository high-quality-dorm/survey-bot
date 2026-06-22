run:
	uv run -m bot

lint:
	uv run mypy src/
	uv run ruff check src/
	uv run ruff format src/ --check

format:
	uv run ruff check --select I --fix src/
	uv run ruff format src/