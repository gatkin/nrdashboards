format:
	python -m black src/ tests/

install:
	python -m pip install -U pip
	python -m pip install -U pipenv
	python -m pipenv install --dev

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
