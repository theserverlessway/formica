.PHONY: build

dependencies:
	pip install -U -r build-requirements.txt
	python setup.py develop

test:
	py.test --cov-branch --cov-report html --cov-report term-missing --cov=formica tests/unit

check-code:
	pycodestyle .
	pyflakes .

integration-test:
	py.test -s tests/integration

build-dev:
	docker-compose build formica

shell: build-dev
	docker-compose run formica bash

clean:
	rm -fr dist

build: clean build-dev
	docker-compose run formica python setup.py sdist bdist_wheel
	docker-compose run formica pandoc --from=markdown --to=rst --output=build/README.rst README.md

release-pypi: clean build-dev build 
	docker-compose run formica twine upload dist/*

release-docker:
	docker build --no-cache -t flomotlik/formica -f Dockerfile.release .
	docker push flomotlik/formica

release: release-pypi release-docker

install:
	docker build -t flomotlik/formica:whalebrew -f Dockerfile.whalebrew .
	whalebrew install -f flomotlik/formica:whalebrew
