coverage:
	python -m coverage run tests/run_tests.py --junit-xml=test_results/test_results.xml
	python -m coverage report
	python -m coverage html

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

per-commit: lint coverage

test:
	python -m pytest -vv

type-check:
	python -m mypy nrdash/
