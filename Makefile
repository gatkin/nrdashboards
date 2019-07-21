format:
	python -m black src/ tests/

lint:
	python -m black --check src/ tests/
	python -m flake8 --max-complexity 10 src/
	python -m pydocstyle src/
	python -m pylint --rcfile src/.pylintrc src/

per-commit: lint type-check test

test:
	python -m pytest -vv

type-check:
	python -m mypy src/
