lint:
	mypy src/
	ruff check src/
	ruff format src/ --check

format:
	ruff check --select I --fix src/
	ruff format src/