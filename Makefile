.PHONY: build

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

clean:
	rm -fr dist

build: clean
	python setup.py sdist bdist_wheel
	pandoc --from=markdown --to=rst --output=build/README.rst README.md

release-pypi: build
	twine upload dist/*

release-test-pypi: build
	twine upload dist/* --repository-url https://testpypi.python.org/pypi -r https://testpypi.python.org/pypi

release-docker:
	docker build --no-cache -t flomotlik/formica -f Dockerfile.release .
	docker push flomotlik/formica

whalebrew:
	docker build -t flomotlik/formica:whalebrew -f Dockerfile.whalebrew .
	whalebrew install -f flomotlik/formica:whalebrew