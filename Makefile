coverage:
	python -m coverage run tests/run_tests.py -v --junit-xml=test_results/test_results.xml
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

package:
	python setup.py sdist bdist_wheel

per-commit: lint coverage

per-release: publish-pypi publish-docs

publish-coverage:
	coveralls

publish-docs:
	mkdocs gh-deploy

publish-pypi: package
	python3 -m twine upload --verbose --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD} --repository-url https://upload.pypi.org/legacy/ dist/*

publish-pypi-test: package
	python3 -m twine upload --verbose --username ${PYPI_TEST_USERNAME} --password ${PYPI_TEST_PASSWORD} --repository-url https://test.pypi.org/legacy/ dist/*

serve-docs:
	mkdocs serve

test:
	python -m pytest -vv

type-check:
	python -m mypy nrdash/
