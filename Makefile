format:
	python -m black nrdash/ tests/

install:
	python -m pip install -U pip
	python -m pip install -U pipenv
	python -m pipenv sync --dev

lint: type-check
	python -m black --check nrdash/ tests/
	python -m flake8 --max-complexity 10 nrdash/
	python -m pydocstyle nrdash/
	python -m pylint --rcfile nrdash/.pylintrc nrdash/

per-commit: lint test

test:
	python -m pytest -vv

type-check:
	python -m mypy nrdash/
