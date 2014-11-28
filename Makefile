PYTHON=python3


all: install test

install:
	$(PYTHON) setup.py install

test:
	$(PYTHON) -m unittest