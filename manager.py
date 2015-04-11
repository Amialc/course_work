from course import db, app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

#migrations
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
#manager.add_command('run', app.app.run(debug=True))

if __name__ == '__main__':
    manager.run()
#app.app.run(debug=True)