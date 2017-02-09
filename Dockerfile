FROM python:latest

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel
RUN pip install --upgrade pycodestyle pyflakes autopep8 coverage pytest

COPY setup.py setup.py
COPY setup.cfg setup.cfg
COPY formica/__init__.py formica/__init__.py
COPY README.md README.md

RUN python setup.py develop
