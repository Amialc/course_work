#!/usr/bin/python

from course import db
print "drop_all"
db.drop_all()
print "create_all"
db.create_all()

from models import User, Teacher, UserProfile
from views import decode

sess = db.session()
user = User('admin@admin.ru', decode('123'))
sess.add(user)
sess.commit()
teacher = Teacher(user.id)
userprofile = UserProfile(user.id, 'admin')
sess.add(userprofile)
sess.add(teacher)
sess.commit()

#os.popen("python db_init.py")