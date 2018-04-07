#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Post, Follow, Permission, Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.fake import users, posts


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def init_db():
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    users()
    posts()


def make_shell_context():
    return dict(app=app, db=db, User=User, Follow=Follow, Role=Role,
                Permission=Permission, Post=Post, Comment=Comment,
                users=users, posts=posts, init_db=init_db)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
