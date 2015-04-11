#!/usr/bin/python

from course import db
print "drop_all"
db.drop_all()
print "create_all"
db.create_all()

#os.popen("python db_init.py")