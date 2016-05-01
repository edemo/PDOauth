install: static/qunit-1.18.0.js static/qunit-1.18.0.css static/qunit-reporter-junit.js static/blanket.min.js bootstrap-3 jquery

checkall: install alltests xmldoc

realclean:
	rm -rf PDAnchor; git clean -fdx
testenv:
	docker run --rm -p 5900:5900 -p 5432:5432 -v /var/run/postgresql:/var/run/postgresql -v $$(pwd):/PDOauth -it magwas/edemotest:master

static/qunit-1.18.0.js:
	curl http://code.jquery.com/qunit/qunit-1.18.0.js -o static/qunit-1.18.0.js

static/qunit-1.18.0.css:
	curl http://code.jquery.com/qunit/qunit-1.18.0.css -o static/qunit-1.18.0.css

static/qunit-reporter-junit.js:
	curl https://raw.githubusercontent.com/JamesMGreene/qunit-reporter-junit/master/qunit-reporter-junit.js -o static/qunit-reporter-junit.js

static/blanket.min.js:
	curl https://raw.githubusercontent.com/alex-seville/blanket/89266afe70ea733592f5d51f213657d98e19fc0a/dist/qunit/blanket.js -o static/blanket.min.js

bootstrap-3:
	curl https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css -o static/bootstrap.min.css; curl https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js -o static/bootstrap.min.js

jquery:
	curl https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js -o static/jquery.min.js
	
clean:
	rm -rf doc lib tmp static/qunit-1.18.0.css static/qunit-1.18.0.js static/qunit-reporter-junit.js PDAnchor

alltests: tests integrationtests end2endtest

onlyend2endtest: install testsetup runanchor runserver runemail testsetup waitbeforebegin firefoxtest

waitbeforebegin:
	sleep 10

PDAnchor:
	git clone https://github.com/edemo/PDAnchor.git

runanchor: PDAnchor
	make -C PDAnchor runserver

firefoxtest:
	PYTHONPATH=src python -m unittest discover -v -f -s src/end2endtest -p "*Test.py"

chrometest:
	PYTHONPATH=src WEBDRIVER=chrome python -m unittest discover -v -f -s src/end2endtest -p "*Test.py"

end2endtest: onlyend2endtest killall

runserver:
	mkdir -p tmp; apache2 -X -f $$(pwd)/src/end2endtest/apache2.conf&

killserver:
	kill $$(cat tmp/httpd.pid)

runemail:
	mkdir -p tmp; python -m smtpd -n -c DebuggingServer localhost:1025 >tmp/smtpd.log&

killemail:
	ps ax |grep DebuggingServer |grep -v grep |awk '{print $$1}' |xargs kill

integrationtests: testsetup
	PYTHONPATH=src python-coverage run -m unittest discover -v -f -s src/integrationtest -p "*.py"

tests: testsetup
	PYTHONPATH=src python-coverage run -m unittest discover -v -f -s src/test -p "*.py"

testsetup:
	rm -f /tmp/pdoauth.db; touch /tmp/pdoauth.db; make dbupgrade ; mkdir -p doc/screenshots

dbmigrate:
	PYTHONPATH=src:src/test python src/manage.py db migrate

dbupgrade:
	PYTHONPATH=src:src/test python src/manage.py db upgrade

handtest: testsetup runemail runserver

sql:
	sqlite3 /tmp/pdoauth.db

killall: killserver killemail killanchor

killanchor:
	 make -C PDAnchor killserver

xmldoc: doc/html/commitlog.html doc/xml/doc.xml doc/html/documentation.html doc/html/coverage

doc/xml/doc.xml: doc/xml/commitlog.xml doc/xml/buildinfo.xml doc/xml
	PYTHONPATH=src:src/test pydoctor src --html-writer=doc.MyWriter.MyWriter --html-output=doc/xml

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
	python-coverage html -d doc/html/coverage src/pdoauth/*.py src/pdoauth/*/*.py

doc/static/docbook.css: static/docbook.css
	mkdir -p doc/static; cp static/docbook.css doc/static/docbook.css

doc/html/documentation.html: lib/saxon9he.jar doc/html/documentation.docbook doc/static/docbook.css
	java -jar lib/saxon9he.jar -xsl:src/doc/docbook2html.xslt -s:doc/html/documentation.docbook >doc/html/documentation.html

always:

messages.pot: always
	xgettext -L Python -j --package-name=PDOauth -o messages.pot src/pdoauth/Messages.py
	xgettext -L javascript -j --from-code=utf-8 --package-name=PDOauth -o messages.pot static/js/*.js

static/locale/hu.po: messages.pot
	msgmerge -U static/locale/hu.po messages.pot

