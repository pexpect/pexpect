SHELL = /bin/sh

VERSION=2.0
#DOCGENERATOR= happydoc
DOCGENERATOR= pydoc -w
# This is for GNU Make. This does not work on BSD Make.
MANIFEST_LINES := $(shell cat MANIFEST)
# This is for BSD Make. This does not work on GNU Make.
#MANIFEST_LINES != cat MANIFEST

all: dist examples docs

# *.py README.txt MANIFEST

# I had to add the chmod 644 and 755 because cvs sucks.
# I accidentally checked in some files with the wrong permissions
# and now there is no way to fix those (I don't have CVSROOT access
# becuase I'm using cvs hosted on sourceforge).
dist/pexpect-$(VERSION).tar.gz: $(MANIFEST_LINES)
	rm -f *.pyc
	rm -f pexpect-*.tgz
	rm -f dist/pexpect-$(VERSION).tar.gz
	chmod 644 *.py
	chmod 755 setup.py
	chmod 755 examples/*.py
	/usr/bin/env python setup.py sdist

install: dist
	cd dist;\
	tar zxf pexpect-$(VERSION).tar.gz;\
	cd pexpect-$(VERSION);\
	/usr/bin/env python setup.py install

dist: pexpect-current.tgz

pexpect-current.tgz: dist/pexpect-$(VERSION).tar.gz
	rm -f pexpect-current.tgz
	cp dist/pexpect-$(VERSION).tar.gz ./pexpect-current.tgz
	cp dist/pexpect-$(VERSION).tar.gz ./pexpect-$(VERSION).tgz

docs: pexpect-doc.tgz

pexpect-doc.tgz: doc/*
	rm -f pexpect-doc.tgz
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.html//'` 
	$(DOCGENERATOR) `echo "$(MANIFEST_LINES)" | sed -e "s/\.py//g"`
	mv *.html doc/
	tar zcf pexpect-doc.tgz doc/

examples: pexpect-examples.tgz

pexpect-examples.tgz: examples/*
	rm -f pexpect-examples.tgz
	chmod 755 examples/*.py
	tar zcf pexpect-examples.tgz examples/

clean:
	rm -f *.pyc
	rm -f tests/*.pyc
	rm -f tools/*.pyc
	rm -f *.cover
	rm -f tests/*.cover
	rm -f tools/*.cover
	rm -f dist/pexpect-$(VERSION).tar.gz
	chmod 644 *.py
	chmod 755 setup.py
	chmod 755 examples/*.py
	cd dist;rm -rf pexpect-$(VERSION)/
	rm -f pexpect-$(VERSION).tgz
	rm -f pexpect-current.tgz
	rm -f pexpect-examples.tgz
	rm -f pexpect-doc.tgz
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.html//'` 
	rm -f python.core
	rm -f core
	
