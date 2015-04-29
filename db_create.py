#!/usr/bin/python

from course import db

print "drop_all"
db.drop_all()
print "create_all"
db.create_all()

from models import User, Teacher
from views import decode
from random import randrange

sess = db.session()
password = randrange(100000, 999999)
user = User('admin@admin.ru', decode(str(password)), 'admin')
db.session.add(user)
db.session.commit()
db.session.add(Teacher(user.id))
db.session.commit()

print "Admin password:", password