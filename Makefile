LAST_VER=0.1.0
NEXT_VER=0.1.1
.phony: package clean

all:
	python setup.py build

install:
	pip install -r requirements
	python setup.py install --install-scripts=/usr/bin/

develop:
	python setup.py develop

clean:
	-find . -name __pycache__ -exec rm -r -- {} +
	-find . -name *.pyc -exec rm -r -- {} +

package:
	-rm doc/*~
	python setup.py sdist

man:
	nroff -man doc/nester.1 | less

rel:
	python setup.py bdist sdist upload -s

update-ver:
	for i in doc/*{1,5} setup.py bin/nester; do sed -e 's/${LAST_VER}/${NEXT_VER}/' -i '' $$i; done
