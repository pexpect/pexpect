SHELL = /bin/sh

VERSION= 0.8
#DOCGENERATOR= happydoc
DOCGENERATOR= pydoc -w
MANIFEST_LINES != cat MANIFEST

all: dist examples doc

# *.py README.txt MANIFEST

dist/pexpect-$(VERSION).tar.gz: $(MANIFEST_LINES)
	rm -f *.pyc
	rm -f pexpect-*.tgz
	rm -f dist/pexpect-$(VERSION).tar.gz
	/usr/bin/env python setup.py sdist

install:
	make distutil
	/usr/bin/env python setup.py install

dist: pexpect-current.tgz

pexpect-current.tgz: dist/pexpect-$(VERSION).tar.gz
	rm -f pexpect-current.tgz
	cp dist/pexpect-$(VERSION).tar.gz ./pexpect-current.tgz

doc: doc.tgz

doc.tgz: doc/*
	rm -f doc.tgz
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.html//'` 
	$(DOCGENERATOR) `echo "$(MANIFEST_LINES)" | sed -e "s/\.py//g"`
	mv *.html doc/
	tar zcf doc.tgz doc/

examples: examples.tgz

examples.tgz: examples/*
	rm -f examples.tgz
	tar zcf examples.tgz examples/

clean:
	rm -f *.pyc
	rm -f pexpect-*.tgz
	rm -f dist/pexpect-$(VERSION).tar.gz
	rm -f examples.tgz
	rm -f doc.tgz
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.html//'` 
	rm -f python.core
	rm -f core
	
