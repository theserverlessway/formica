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

coveralls:
	coveralls