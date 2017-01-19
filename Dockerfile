FROM python:latest

WORKDIR /app
COPY setup.py setup.py
COPY setup.cfg setup.cfg
COPY formica/__init__.py formica/__init__.py
COPY README.md README.md

RUN python setup.py develop
