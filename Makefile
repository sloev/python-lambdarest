install-python-versions:
	cat .python-version | xargs -tL1 pyenv install -s

install-requirements:
	pip install tox==3.14.3 black==19.10b0

install-requirements-single-version:
	pip install -r dev_requirements.txt
	pip install black==19.10b0

setup-all: install-python-versions install-requirements

setup: install-requirements-single-version
	
fix-lint:
	black .

lint-ci:
	black --check .

test: lint-ci
	pytest

tox: 
	tox

release:
	rm dist/* || true
	python setup.py sdist build
	python -m twine upload dist/*