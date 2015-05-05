
tests:
	PYTHONPATH=src python -m unittest discover -s src/test -p '*.py'
dbmigrate:
	PYTHONPATH=src:src/test python src/manage.py db migrate

dbupgrade:
	PYTHONPATH=src:src/test python src/manage.py db upgrade

sql:
	sqlite3 /tmp/pdoauth.db
