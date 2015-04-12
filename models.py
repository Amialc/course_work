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

    def get_name(self):
        user = UserProfile.query.filter_by(user_id = self.id).first()
        if user:
            return user.realname
        else:
            return None

    def is_teacher(self):
        if Teacher.query.filter_by(user_id = self.id).first():
            return True
        else:
            return False

    def is_admin(self):
        if self.id == 1:
            return True
        else:
            return False

    def is_student(self):
        if (not self.is_admin()) and (not self.is_teacher()):
            return True
        else:
            return False

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

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
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

    def __init__(self, user_id):
        self.user_id = user_id

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    name = db.Column(db.String(250))
    final_date = db.Column(db.DateTime)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    text = db.Column(db.String(250))
