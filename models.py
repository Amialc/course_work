from course import db, login_serializer

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)

    def __init__(self, email=None, password=None, j=None):
        if j is not None:
            self.__dict__ = j
        else:
            self.email = email
            self.password = password

    def get_auth_token(self):
        """
        Encode a secure token for cookie
        """
        data = [str(self.id), self.password]
        return login_serializer.dumps(data)

    def generate_auth_token(self):
        return login_serializer.dumps({'id': self.id})

    def verify_password(self, password_for_check):
        if self.password == password_for_check:
            return True
        return False

    @staticmethod
    def verify_auth_token(token):
        try:
            data = login_serializer.loads(token)
        except:
            return None  # valid token, but expired
        user = User.query.get(data['id'])
        return user

    @staticmethod
    def get(user_id):
        """
        Static method to search the database and see if userid exists.  If it
        does exist then return a User Object.  If not then return None as
        required by Flask-Login.
        """
        for user in User.query.all():
            if user.id == user_id:
                return User(user.email, user.password)
        return None

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    realname = db.Column(db.String(250))


    def __init__(self, user_id, realname=None):
        self.user_id = user_id
        self.realname = realname

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
