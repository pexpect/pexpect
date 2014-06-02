
#
# PEXPECT LICENSE
#
#     This license is approved by the OSI and FSF as GPL-compatible.
#         http://opensource.org/licenses/isc-license.txt
#
#     Copyright (c) 2012, Noah Spurrier <noah@noah.org>
#     PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
#     PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
#     COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
#     THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#     WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#     MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#     ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#     WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#     ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#     OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

SHELL = /bin/sh

VERSION=2.5
#DOCGENERATOR= happydoc
DOCGENERATOR=pydoc -w
# This is for GNU Make. This does not work on BSD Make.
#MANIFEST_LINES := $(shell cat MANIFEST)
# This is for BSD Make. This does not work on GNU Make.
#MANIFEST_LINES != cat MANIFEST
# I hate Makefiles.

all: merge_templates docs dist

merge_templates:
	python tools/merge_templates.py

docs: doc/index.template.html doc/examples.html doc/clean.css doc/email.png
	make clean_docs
	make merge_templates
	#-rm -f `ls doc/*.html | sed -e 's/doc\/index\.template\.html//' | sed -e 's/doc\/index\.html//'` 
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

clean: clean_docs
	-rm -f MANIFEST
	-rm -rf __pycache__
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
	-rm -f python.core
	-rm -f core
	-rm -f setup.py
	-rm -f doc/index.html

clean_docs:
	-rm -f `ls doc/*.html | sed -e 's/doc\/index\.template\.html//' | sed -e 's/doc\/examples\.html//'`


