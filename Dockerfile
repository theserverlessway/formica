FROM python:latest

WORKDIR /app

RUN apt-get update -y
RUN apt-get install -y groff pandoc gcc libffi-dev libssl-dev openssl musl-dev python-dev bash

RUN pip install -U wheel pygments twine
RUN pip install -U awslogs awscli
COPY build-requirements.txt build-requirements.txt
RUN pip install -U -r build-requirements.txt

COPY setup.py setup.py
COPY setup.cfg setup.cfg
COPY formica/__init__.py formica/__init__.py
COPY README.md README.md

RUN pandoc --from=markdown --to=rst --output=README.rst README.md

RUN python setup.py develop
