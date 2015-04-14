from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from pdoauth.app import app, db
from pdoauth.models.Application import Application  # @UnusedImport to have database schema

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()