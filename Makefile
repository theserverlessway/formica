.PHONY: build

dependencies:
	python --version
	pip install -U -r build-requirements.txt
	python setup.py develop

test:
	py.test --cov-branch --cov-report html --cov-report term-missing --cov=formica tests/unit

check-code:
	black --check --verbose ./formica
	pyflakes ./formica
	grep -r 'print(' formica; [ "$$?" -gt 0 ]

mutation:
	mutmut run

integration-test:
	py.test -s tests/integration

build-dev:
	docker-compose build formica

shell: build-dev
	touch .bash_history
	docker-compose run formica bash

clean:
	rm -fr dist/* build/* formica_cli.egg-info/* htmlcov/* .pytest-cache/*

release-pypi:
	docker-compose run formica bash -c "make clean && python setup.py sdist bdist_wheel && pandoc --from=markdown --to=rst --output=build/README.rst README.md && twine upload dist/*"

release-docker:
	docker build --no-cache -t flomotlik/formica -f Release.Dockerfile .
	docker push flomotlik/formica

release: release-pypi release-docker

install:
	docker build -t flomotlik/formica:whalebrew -f Whalebrew.Dockerfile .
	whalebrew install -f flomotlik/formica:whalebrew

update-commands-usage:
	ls