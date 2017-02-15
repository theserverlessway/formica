FROM python:2.7

WORKDIR /app

RUN apt-get update -y -qq
RUN apt-get install -y -qq groff pandoc

RUN pip install -U pip setuptools wheel pygments twine
RUN pip install -U pycodestyle pyflakes autopep8 coverage pytest
RUN pip install -U awslogs awscli

COPY setup.py setup.py
COPY setup.cfg setup.cfg
COPY formica/__init__.py formica/__init__.py
COPY README.md README.md

RUN pandoc --from=markdown --to=rst --output=README.rst README.md

RUN python setup.py develop
