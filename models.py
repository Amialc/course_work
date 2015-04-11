from course import db

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    realname = db.Column(db.String(250))

    def __init__(self, user_id, realname = None):
        self.user_id = user_id
        self.realname = realname
