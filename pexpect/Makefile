SHELL = /bin/sh

VERSION= 0.91
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

doc: pexpect-doc.tgz

pexpect-doc.tgz: doc/*
	rm -f pexpect-doc.tgz
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.html//'` 
	$(DOCGENERATOR) `echo "$(MANIFEST_LINES)" | sed -e "s/\.py//g"`
	mv *.html doc/
	tar zcf pexpect-doc.tgz doc/

examples: pexpect-examples.tgz

pexpect-examples.tgz: examples/*
	rm -f pexpect-examples.tgz
	tar zcf pexpect-examples.tgz examples/

clean:
	rm -f *.pyc
	rm -f pexpect-*.tgz
	rm -f dist/pexpect-$(VERSION).tar.gz
	rm -f pexpect-examples.tgz
	rm -f pexpect-doc.tgz
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.html//'` 
	rm -f python.core
	rm -f core
	
