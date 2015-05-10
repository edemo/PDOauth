alltests: tests integrationtest

onlyintegrationtest: testsetup runserver runemail testsetup
	PYTHONPATH=src python -m unittest discover -s integrationtest -p "*.py"

integrationtest: onlyintegrationtest killall

runserver:
	PYTHONPATH=src:integrationtest python src/pdoauth/main.py&

killserver:
	ps ax |grep pdoauth/main.py |grep -v grep |awk '{print $$1}' |xargs kill

runemail:
	python -m smtpd -n -c DebuggingServer localhost:1025&

killemail:
	ps ax |grep DebuggingServer |grep -v grep |awk '{print $$1}' |xargs kill

tests: testsetup
	PYTHONPATH=src python -m unittest discover -s src/test -p "*.py"

testsetup:
	rm -f /tmp/pdoauth.db; touch /tmp/pdoauth.db; make dbupgrade

dbmigrate:
	PYTHONPATH=src:src/test python src/manage.py db migrate

dbupgrade:
	PYTHONPATH=src:src/test python src/manage.py db upgrade

handtest: testsetup runemail runserver

sql:
	sqlite3 /tmp/pdoauth.db

killall: killserver killemail
