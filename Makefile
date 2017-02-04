
HTML_FILES = user_howto.html\
	index.html\
	login.html\
	about_us.html\
	fiokom.html\
	assurer_howto.html\
	deregistration.html\
	passwordreset.html\
	logout.html

js_files := $(shell find site/js -maxdepth 1 -type f -name '*.js' -printf '%f\n')

js_test_files := $(shell find site/test/end2endTests -maxdepth 1 -type f -name '*.js' -printf '%f\n')

all:
	docker run --cpuset-cpus=0-1 --memory=2G --rm -p 5900:5900 -p 5432:5432 -p 8888:8888 -v /var/run/postgresql:/var/run/postgresql -v $$(pwd):/PDOauth -it magwas/edemotest:master /PDOauth/tools/script_from_outside

%.json: %.po
	./tools/po2json $< >$@

install: static static/locale/hu.json

checkall: uris_ install tests integrationtests end2endtest xmldoc

checkmanual: install alltests xmldoc

alltests: tests integrationtests end2endtest

uris_:
	PYTHONPATH=src/end2endtest python3 ./tools/adauris.py
uris:
	PYTHONPATH=/etc/pdoauth python3 ./tools/adauris.py

static: static-base static-html static-js static-jstest
static-base:
	mkdir -p static/js
	cp -r site/css site/favicon.ico site/docbook.css site/fonts site/docs site/assurers.json site/images site/locale site/test static

static-js:
	for js in $(js_files); do rollup --format=iife --output=static/js/$$js -- site/js/$$js; done

static-jstest:
	for js in $(js_test_files); do rollup --format=iife --output=static/test/end2endTests/$$js -- site/test/end2endTests/$$js; done

static-html:
	for page in $(HTML_FILES); do ./tools/compilehtml $$page; done

realclean:
	rm -rf PDAnchor; git clean -fdx
testenv:
	docker run --cpuset-cpus=0-1 --memory=2G --rm -p 5900:5900 -p 5432:5432 -p 8888:8888 -v /var/run/postgresql:/var/run/postgresql -v $$(pwd):/PDOauth -w /PDOauth -it magwas/edemotest:master

clean:
	rm -rf doc lib tmp static/qunit-1.18.0.css static/qunit-1.18.0.js static/qunit-reporter-junit.js PDAnchor

prepare2e: install testsetup runanchor runserver runemail

onlyend2endtest: prepare2e waitbeforebegin firefoxtest
#chrometest is not running now

waitbeforebegin:
	sleep 10

PDAnchor:
	git clone https://github.com/edemo/PDAnchor.git

runanchor: PDAnchor
	make -C PDAnchor runserver

firefoxtest:
	PYTHONPATH=src python3 -m unittest discover -v -f -s src/end2endtest -p "*Test.py"

chrometest:
	PYTHONPATH=src WEBDRIVER=chrome python3 -m unittest discover -v -f -s src/end2endtest -p "*Test.py"

end2endtest: recording onlyend2endtest killall stoprecording

runserver:
	mkdir -p tmp; apache2 -X -f $$(pwd)/src/end2endtest/apache2.conf&

killserver:
	kill $$(cat tmp/httpd.pid)

runemail:
	mkdir -p tmp; python -m smtpd -n -c DebuggingServer localhost:1025 >tmp/smtpd.log&

killemail:
	ps ax |grep DebuggingServer |grep -v grep |awk '{print $$1}' |xargs kill

integrationtests: testsetup
	PYTHONPATH=src python3-coverage run -m unittest discover -v -f -s src/integrationtest -p "*.py"

tests: testsetup
	PYTHONPATH=src python3-coverage run -m unittest discover -v -f -s src/test -p "*.py"

testsetup:
	psql -d template1 -c "drop database root"
	sudo -u postgres psql -d template1 -c "create database root owner root"
	make dbupgrade ; mkdir -p doc/screenshots

dbmigrate:
	PYTHONPATH=src:src/test python3 src/manage.py db migrate

dbupgrade:
	PYTHONPATH=src:src/test python3 src/manage.py db upgrade

handtest: testsetup runemail runserver

sql:
	sqlite3 /tmp/pdoauth.db

killall: killserver killemail killanchor

killanchor:
	 make -C PDAnchor killserver

xmldoc: doc/html/commitlog.html doc/xml/doc.xml doc/html/documentation.html doc/html/coverage

doc/xml/doc.xml: doc/xml/commitlog.xml doc/xml/buildinfo.xml doc/xml
	PYTHONPATH=src:src/test:src/doc pydoctor src --html-writer=MyWriter.MyWriter --html-output=doc/xml

doc/xml/commitlog.xml: doc/xml
	(echo "<commitlog>";git log --pretty=format:'<commit id="%h" author="%an" date="%ad">%f</commit>'|cat;echo "</commitlog>")|sed 's/-/ /g' >doc/xml/commitlog.xml

doc/xml/buildinfo.xml: doc/xml
	 echo "<buildinfo><branch>${TRAVIS_BRANCH}</branch><commit>${TRAVIS_COMMIT}</commit><build>${TRAVIS_BUILD_ID}</build></buildinfo>" >doc/xml/buildinfo.xml

doc/html:
	mkdir -p doc/html

doc/xml:
	mkdir -p doc/xml

tmp/saxon.zip:
	mkdir -p tmp ;curl -L "http://downloads.sourceforge.net/project/saxon/Saxon-HE/9.6/SaxonHE9-6-0-5J.zip" >tmp/saxon.zip

lib/saxon9he.jar: tmp/saxon.zip
	mkdir -p lib;unzip -u -d lib  tmp/saxon.zip saxon9he.jar

doc/xml/intermediate.xml: lib/saxon9he.jar doc/xml/doc.xml #doc/screenshots/unittests.xml
	java -jar lib/saxon9he.jar -xsl:src/doc/intermediate.xsl -s:doc/xml/doc.xml >doc/xml/intermediate.xml

doc/html/commitlog.docbook: lib/saxon9he.jar doc/xml/commitlog.xml doc/html
	java -jar lib/saxon9he.jar -xsl:src/doc/commitlog.xsl -s:doc/xml/commitlog.xml >doc/html/commitlog.docbook

doc/html/commitlog.html: lib/saxon9he.jar doc/html/commitlog.docbook doc/static/docbook.css
	java -jar lib/saxon9he.jar -xsl:src/doc/docbook2html.xslt -s:doc/html/commitlog.docbook >doc/html/commitlog.html

doc/html/documentation.docbook: lib/saxon9he.jar doc/xml/intermediate.xml doc/html
	java -jar lib/saxon9he.jar -xsl:src/doc/todocbook.xsl -s:doc/xml/intermediate.xml >doc/html/documentation.docbook

doc/html/coverage:
	python3-coverage html -d doc/html/coverage src/pdoauth/*.py src/pdoauth/*/*.py

doc/static/docbook.css: static/docbook.css
	mkdir -p doc/static; cp static/docbook.css doc/static/docbook.css

doc/html/documentation.html: lib/saxon9he.jar doc/html/documentation.docbook doc/static/docbook.css
	java -jar lib/saxon9he.jar -xsl:src/doc/docbook2html.xslt -s:doc/html/documentation.docbook >doc/html/documentation.html

always:

messages.pot: always
	rm -f messages.pot
	touch messages.pot
	xgettext -L Python -j --package-name=PDOauth -o messages.pot src/pdoauth/Messages.py
	xgettext -L javascript -j --from-code=utf-8 --package-name=PDOauth -o messages.pot static/js/*.js

static/locale/hu.po: messages.pot
	msgmerge -U static/locale/hu.po messages.pot

recording:
	start-stop-daemon --start --background --oknodo --name flvrec --make-pidfile --pidfile /tmp/flvrec.pid --startas /usr/bin/python -- /usr/local/bin/flvrec.py -o /tmp/record.flv :0

stoprecording:
	-start-stop-daemon --stop --pidfile /tmp/flvrec.pid

