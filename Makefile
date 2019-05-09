.PHONY: build

dependencies:
	python --version
	pip install -U -r build-requirements.txt
	python setup.py develop

test:
	py.test --cov-branch --cov-report html --cov-report term-missing --cov=formica tests/unit

check-code:
	pycodestyle ./formica
	pyflakes ./formica
	grep -r 'print(' formica; [ "$$?" -gt 0 ]

integration-test:
	py.test -s tests/integration

build-dev:
	docker-compose build formica

shell: build-dev
	docker-compose run formica bash

clean:
	rm -fr dist build formica_cli.egg-info htmlcov .pytest-cache

build: clean build-dev
	docker-compose run formica python setup.py sdist bdist_wheel
	docker-compose run formica pandoc --from=markdown --to=rst --output=build/README.rst README.md

release-pypi: clean build-dev build
	docker-compose run formica twine upload dist/*

release-docker:
	docker build --no-cache -t flomotlik/formica -f Release.Dockerfile .
	docker push flomotlik/formica

release: release-pypi release-docker

install:
	docker build -t flomotlik/formica:whalebrew -f Whalebrew.Dockerfile .
	whalebrew install -f flomotlik/formica:whalebrew
