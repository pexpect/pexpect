SHELL = /bin/sh

VERSION=2.1
#DOCGENERATOR= happydoc
DOCGENERATOR= pydoc -w
# This is for GNU Make. This does not work on BSD Make.
#MANIFEST_LINES := $(shell cat MANIFEST)
# This is for BSD Make. This does not work on GNU Make.
#MANIFEST_LINES != cat MANIFEST

all: merge_templates docs dist

merge_templates:
	python tools/merge_templates.py

docs: doc/*
#	rm -f pexpect-doc-$(VERSION).tar.gz
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.template\.html//' | sed -e 's/doc\/index\.html//'` 
	#$(DOCGENERATOR) `echo "$(MANIFEST_LINES)" | sed -e "s/\.py//g" -e "s/setup *//" -e "s/README *//"`
	#mv *.html doc/
	cd doc;\
	$(DOCGENERATOR) ../pexpect.py ../pxssh.py ../fdpexpect.py ../FSM.py ../screen.py ../ANSI.py;\
	cd ..;\
#	tar zcf pexpect-doc-$(VERSION).tar.gz doc/

dist: dist/pexpect-$(VERSION).tar.gz

# $(MANIFEST_LINES)

dist/pexpect-$(VERSION).tar.gz:
	rm -f *.pyc
	rm -f pexpect-$(VERSION).tar.gz
	rm -f dist/pexpect-$(VERSION).tar.gz
	python setup.py sdist

clean:
	-rm -f MANIFEST
	-rm -f *.pyc
	-rm -f tests/*.pyc
	-rm -f tools/*.pyc
	-rm -f dist/*.pyc
	-rm -f *.cover
	-rm -f tests/*.cover
	-rm -f tools/*.cover
	-rm -f dist/pexpect-$(VERSION).tar.gz
	-cd dist;rm -rf pexpect-$(VERSION)/
	-rm -f pexpect-$(VERSION).tar.gz
	-rm -f pexpect-$(VERSION)-examples.tar.gz
	-rm -f pexpect-$(VERSION)-doc.tar.gz
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.template\.html//'` 
	-rm -f python.core
	-rm -f core
	-rm -f setup.py
	-rm -f doc/index.html
	
