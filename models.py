from course import db, login_serializer
from datetime import date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    realname = db.Column(db.String(250))

    def __init__(self, email, password, realname):
        self.email = email
        self.password = password
        self.realname = realname

    def is_teacher(self):
        if Teacher.query.filter_by(user_id=self.id).first():
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
                return User(user.email, user.password, user.realname)
        return None


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user_id):
        self.user_id = user_id


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user_id):
        self.user_id = user_id


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    name = db.Column(db.String(250))
    running = db.Column(db.Boolean, default=False)
    final_date = db.Column(db.Date)


    def __init__(self, teacher_id, name, final_date=None):
        self.teacher_id = teacher_id
        self.name = name
        if final_date is None:
            self.final_date = date.today()


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    text = db.Column(db.String(250))

    def __init__(self, test_id, text):
        self.test_id = test_id
        self.text = text


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    text = db.Column(db.String(250))

    def __init__(self, question_id, text):
        self.question_id = question_id
        self.text = text


class Assigned(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    completed = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, test_id):
        self.user_id = user_id
        self.test_id = test_id

class Assigned_Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def __init__(self, teacher_id, student_id):
        self.teacher_id = teacher_id
        self.student_id = student_id

class Correct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    correct = db.Column(db.String(250))

    def __init__(self, question_id, correct):
        self.question_id = question_id
        self.correct = correct

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    result = db.Column(db.Integer)

    def __init__(self, user_id, test_id, result):
        self.user_id = user_id
        self.test_id = test_id
        self.result = result