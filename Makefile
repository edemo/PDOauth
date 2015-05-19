install: static/qunit-1.18.0.js static/qunit-1.18.0.css static/qunit-reporter-junit.js

checkall: install alltests xmldoc

static/qunit-1.18.0.js:
	curl http://code.jquery.com/qunit/qunit-1.18.0.js -o static/qunit-1.18.0.js

static/qunit-1.18.0.css:
	curl http://code.jquery.com/qunit/qunit-1.18.0.css -o static/qunit-1.18.0.css

static/qunit-reporter-junit.js:
	curl https://raw.githubusercontent.com/JamesMGreene/qunit-reporter-junit/master/qunit-reporter-junit.js -o static/qunit-reporter-junit.js

clean:
	rm -rf doc lib tmp static/qunit-1.18.0.css static/qunit-1.18.0.js static/qunit-reporter-junit.js

alltests: tests integrationtest

onlyintegrationtest: testsetup runserver runemail testsetup
	PYTHONPATH=src python -m unittest discover -s src/integrationtest -p "*.py"

integrationtest: onlyintegrationtest killall

runserver:
	PYTHONPATH=src:src/integrationtest python src/pdoauth/main.py&

killserver:
	ps ax |grep pdoauth/main.py |grep -v grep |awk '{print $$1}' |xargs kill

runemail:
	python -m smtpd -n -c DebuggingServer localhost:1025&

killemail:
	ps ax |grep DebuggingServer |grep -v grep |awk '{print $$1}' |xargs kill

tests: testsetup
	PYTHONPATH=src python -m unittest discover -s src/test -p "*.py"

testsetup:
	rm -f /tmp/pdoauth.db; touch /tmp/pdoauth.db; make dbupgrade ; mkdir -p doc/screenshots

dbmigrate:
	PYTHONPATH=src:src/test python src/manage.py db migrate

dbupgrade:
	PYTHONPATH=src:src/test python src/manage.py db upgrade

handtest: testsetup runemail runserver

sql:
	sqlite3 /tmp/pdoauth.db

killall: killserver killemail

xmldoc: doc/html/documentation.html

doc/xml/doc.xml: doc/xml
	PYTHONPATH=src:src/test pydoctor src --html-writer=doc.MyWriter.MyWriter --html-output=doc/xml

doc/html:
	mkdir -p doc/html

doc/xml:
	mkdir -p doc/xml

tmp/saxon.zip:
	mkdir -p tmp ;curl -L "http://downloads.sourceforge.net/project/saxon/Saxon-HE/9.6/SaxonHE9-6-0-5J.zip" >tmp/saxon.zip

lib/saxon9he.jar: tmp/saxon.zip
	mkdir -p lib;unzip -u -d lib  tmp/saxon.zip saxon9he.jar

doc/xml/intermediate.xml: lib/saxon9he.jar doc/xml/doc.xml doc/screenshots/unittests.xml
	java -jar lib/saxon9he.jar -xsl:src/doc/intermediate.xsl -s:doc/xml/doc.xml >doc/xml/intermediate.xml

doc/html/documentation.docbook: doc/xml/intermediate.xml doc/html
	java -jar lib/saxon9he.jar -xsl:src/doc/todocbook.xsl -s:doc/xml/intermediate.xml >doc/html/documentation.docbook

doc/static/docbook.css: static/docbook.css
	mkdir -p doc/static; cp static/docbook.css doc/static/docbook.css

doc/html/documentation.html: doc/html/documentation.docbook doc/static/docbook.css
	java -jar lib/saxon9he.jar -xsl:src/doc/docbook2html.xslt -s:doc/html/documentation.docbook >doc/html/documentation.html

