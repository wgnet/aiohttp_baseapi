unit-test:
	python -m pytest

codestyle-test:
	python -m flake8

build-package:
	python setup.py sdist
