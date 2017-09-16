install:
	pip install -U -r build-requirements.txt
	python setup.py develop

test:
	py.test --cov=formica tests/unit

check-code:
	pycodestyle .
	pyflakes .

integration-test:
	py.test -s tests/integration

start-docker:
	docker-compose build formica
	docker-compose run formica bash

build:
	python setup.py sdist bdist_wheel
	pandoc --from=markdown --to=rst --output=dist/README.rst README.md

release-pypi: clean build
	twine upload dist/* "$@"

clean:
	rm -fr dist

release-docker:
	docker build -t flomotlik/formica:latest -f Dockerfile.release .
	docker push flomotlik/formica:latest

whalebrew:
	docker build -t flomotlik/formica:whalebrew -f Dockerfile.whalebrew .
	whalebrew install -f flomotlik/formica:whalebrew