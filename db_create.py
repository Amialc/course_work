#!/usr/bin/python

from course import db
print "drop_all"
db.drop_all()
print "create_all"
db.create_all()

from models import User, Teacher
from views import decode

sess = db.session()
user = User('admin@admin.ru', decode('123'), 'admin')
sess.add(user)
sess.commit()
teacher = Teacher(user.id)
sess.add(teacher)
sess.commit()

#os.popen("python db_init.py")