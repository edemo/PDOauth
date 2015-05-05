
tests:
	PYTHONPATH=src python -m unittest discover -s src/test -p '*.py'

testsetup:
	rm -f /tmp/pdoauth.db; touch /tmp/pdoauth.db; make dbupgrade

dbmigrate:
	PYTHONPATH=src:src/test python src/manage.py db migrate

dbupgrade:
	PYTHONPATH=src:src/test python src/manage.py db upgrade

sql:
	sqlite3 /tmp/pdoauth.db
