from hashlib import md5
from random import randrange, shuffle

from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, g
from wtforms import RadioField, SubmitField
from wtforms.validators import Required
from flask.ext.wtf import Form
from sqlalchemy.exc import IntegrityError

from course import app, db, login_serializer, lm
from forms import IndexForm, AddUserForm, AddStringTestForm, AddAnswerForm, AssignForm, StudentForm
from models import User, Teacher, Student, Test, Question, Answer, Assigned, Correct, Assigned_Students, Result


@lm.user_loader
def load_user(user_id):
    """Flask-Login user_loader callback.
    The user_loader function asks this function to get a User Object or return
    None based on the user_id.
    The user_id was stored in the session environment by Flask-Login.
    user_loader stores the returned User object in current_user during every
    flask request.
    """
    member = Teacher.query.filter_by(user_id=user_id).first()
    if member is None:
        member = Student.query.filter_by(user_id=user_id).first()
        if member is None:
            g.id = 0
        else:
            g.id = member.id
    return User.query.get(int(user_id))


@lm.token_loader
def load_token(token):
    print "LOAD TOKEN"
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

    # Decrypt the Security Token, data = [username, hashpass]
    data = login_serializer.loads(token, max_age=max_age)
    print data

    # Find the User
    user = User.get(data[0])

    # Check Password and return user or None
    if user and data[1] == user.password:
        return user
    return None


def decode(password):
    m = md5(password)
    return m.hexdigest()


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated():
        return redirect(url_for('test'))
    form = IndexForm()
    if form.validate_on_submit():
        password = decode(form.password.data)
        user = User.query.filter_by(password=password).first()
        if not user:
            flash('error!')
            return redirect(url_for('index'))
        else:
            login_user(user)
        return redirect(url_for('test', password=form.data))

    return render_template('index.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/delete_test/<int:id>', methods=['GET'])
@login_required
def delete_test(id):
    if current_user.is_student():
        return redirect(url_for('index'))
    teacher_id = Teacher.query.filter_by(user_id=current_user.id).first_or_404().id
    test = Test.query.filter_by(id=id).first()
    questions = Question.query.filter_by(test_id=test.id).all()
    if test.teacher_id == teacher_id:
        for a in Assigned.query.filter_by(test_id=test.id).all():
            db.session.delete(a)
        for q in questions:
            delete_question(q.id)
        for r in Result.query.filter_by(test_id=id).all():
            db.session.delete(r)
        db.session.delete(test)
        db.session.commit()
    return redirect(url_for('test'))


@app.route('/delete_question/<int:id>', methods=['GET'])
@login_required
def delete_question(id):
    if current_user.is_student():
        return redirect(url_for('index'))
    teacher_id = Teacher.query.filter_by(user_id=current_user.id).first_or_404().id
    question = Question.query.get(id)
    answers = Answer.query.filter_by(question_id=question.id).all()
    test = Test.query.get(question.test_id)
    if test.teacher_id == teacher_id:
        for c in Correct.query.filter_by(question_id=id).all():
            db.session.delete(c)
        db.session.commit()
        for a in answers:
            db.session.delete(a)
        db.session.commit()
        db.session.delete(question)
        db.session.commit()
    return redirect(url_for('edit_test', id=test.id))


@app.route('/delete_answer/<int:id>', methods=['GET'])
@login_required
def delete_answer(id):
    if current_user.is_student():
        return redirect(url_for('index'))
    teacher_id = Teacher.query.filter_by(user_id=current_user.id).first_or_404().id
    answer = Answer.query.get(id)
    test_id = Question.query.filter_by(id=answer.question_id).first().test_id
    if Test.query.get(test_id).teacher_id == teacher_id:
        db.session.delete(answer)
        db.session.commit()
    return redirect(url_for('edit_test', id=test_id))


@app.route('/results/<int:id>', methods=['GET', 'POST'])
@login_required
def result(id):
    results = []
    for r in Result.query.filter_by(test_id=id).all():
        results.append((User.query.get(r.user_id), r.result))
    return render_template('results.html', results=results)


@app.route('/test', methods=['GET', 'POST'])
@app.route('/test/', methods=['GET', 'POST'])
@login_required
def test():
    user_id = current_user.id
    if current_user.is_teacher() or current_user.is_admin():
        teacher_id = Teacher.query.filter_by(user_id=user_id).first().id
        tests = Test.query.filter_by(teacher_id=teacher_id).all()
        return render_template('test_teacher.html', tests=tests, teacher_id=teacher_id)
    else:
        tests = []
        for a in Assigned.query.filter_by(user_id=user_id).all():
            if a.completed == False:
                tests.append(Test.query.get(a.test_id))
        print tests
        return render_template('test_student.html', tests=tests)


@app.route('/test/<int:id>', methods=['GET', 'POST'])
def run_test(id):
    if current_user.is_teacher() or current_user.is_admin() or not Test.query.get(
            id).running or Assigned.query.filter_by(test_id=id).first().completed:
        return redirect(url_for('test'))

    class F(Form):
        pass

    # form = TestForm()
    for q in Question.query.filter_by(test_id=id).all():
        choices = []
        for a in Answer.query.filter_by(question_id=q.id).all():
            choices.append((a.id, a.text))
        shuffle(choices)
        setattr(F, str(q.id), RadioField(q.text, coerce=int, choices=choices, validators=[Required()]))
    setattr(F, 'submit', SubmitField('submit'))
    form = F()

    if form.validate_on_submit():
        result = 0
        for f in form:
            if not f.name is 'csrf_token' and not f.name is 'submit':
                if Correct.query.filter_by(question_id=f.name).first().correct == decode(str(f.data)):
                    result += 1
                print f.name, f.data
        res = Result(current_user.id, id, result)
        db.session.add(res)
        assigned = Assigned.query.filter_by(user_id=current_user.id, test_id=id).first()
        assigned.completed = True
        db.session.commit()
        return redirect(url_for('test'))
    return render_template('test_student.html', form=form)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    # user = User.query.get(id)
    if current_user.is_teacher() or current_user.is_admin():
        student_form = StudentForm()
        current_teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        assigned_students = Assigned_Students.query.filter_by(teacher_id=current_teacher.id).all()
        students = []
        for student in assigned_students:
            user = User.query.get(Student.query.get(student.id).user_id)
            students.append((user.realname, user.email))
        if student_form.validate_on_submit():
            password = randrange(100000, 999999)  # random password from 100000 to 999999
            try:
                user = User(student_form.email.data, decode(str(password)), student_form.realname.data)
                db.session.add(user)
                db.session.commit()
                if student_form.category.data == 'Teacher':
                    student = Teacher(user.id)
                else:
                    student = Student(user.id)
                db.session.add(student)
                db.session.commit()
                assign = Assigned_Students(current_teacher.id, student.id)
                db.session.add(assign)
                db.session.commit()
                '''with mail.connect() as conn:
                    msg = Message(subject="Registration", recipients=student_form.email.data,
                                  body="You registered. Password: " + password)
                    conn.send(msg)'''
            except IntegrityError:
                db.session.rollback()
                student_form.realname.errors = 'This user already exists'
                return render_template('profile.html', students=students, student_form=student_form)
            except:
                db.session.rollback()
                return redirect(url_for('profile', id=id))
            print password
            return redirect(url_for('profile', id=current_user.id))

        return render_template('profile.html', students=students, student_form=student_form)
    else:  # if student
        tests = Assigned.query.filter_by(user_id=current_user.id, completed=1).all()
        return render_template('profile.html', tests=tests)


@app.route('/about')
@app.route('/about/')
def about():
    return render_template('about.html')


# @app.route('/run_test',methods=['GET','POST'])
@app.route('/run_test/<int:id>', methods=['GET', 'POST'])
@login_required
def run(id):
    if current_user.is_student():
        return redirect(url_for('index'))
    Test.query.get(id).running = True
    db.session.commit()
    return redirect(url_for('test'))


@app.route('/off_test/<int:id>', methods=['GET', 'POST'])
@login_required
def off(id):
    if current_user.is_student():
        return redirect(url_for('index'))
    Test.query.get(id).running = False
    db.session.commit()
    return redirect(url_for('test'))


@app.route('/edit_test', methods=['GET', 'POST'])
@app.route('/edit_test/', methods=['GET', 'POST'])
@app.route('/edit_test/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_test(id=0, question=0):
    if current_user.is_student():
        return redirect(url_for('index'))
    if id == 0:  # test not exist, creating a new one
        teacher_id = Teacher.query.filter_by(user_id=current_user.id).first().id
        new_test = Test(teacher_id, 'new test')
        db.session.add(new_test)
        db.session.commit()
        new_id = new_test.id
        return redirect(url_for('edit_test', id=new_id))
    test = Test.query.filter_by(id=id).first_or_404()
    questions = Question.query.filter_by(test_id=id).all()
    answers = {}
    for q in questions:
        answers[q.id] = Answer.query.filter_by(question_id=q.id).all()
    new_question_form = AddStringTestForm(prefix='question')
    if new_question_form.validate_on_submit():
        q = Question(test.id, new_question_form.string.data)
        db.session.add(q)
        db.session.commit()
        return redirect(url_for('edit_test', id=test.id))
    new_answer_form = AddAnswerForm(prefix='answer')
    if new_answer_form.validate_on_submit():
        answ = Answer(new_answer_form.question.data, new_answer_form.string.data)
        db.session.add(answ)
        db.session.commit()
        return redirect(url_for('edit_test', id=test.id))
    assign_form = AssignForm(prefix='assign')
    if assign_form.is_submitted():
        for a in Assigned.query.filter_by(test_id=test.id).all():
            db.session.delete(a)
        db.session.commit()
        for s in assign_form.students.data:
            assign = Assigned(Student.query.filter_by(id=s).first().user_id, id)
            db.session.add(assign)
        db.session.commit()
        return redirect(url_for('edit_test', id=test.id))
    assign_form.students.choices, assign_form.students.default = [], []
    for s in Student.query.all():
        assign_form.students.choices.append((s.id, User.query.filter_by(id=s.user_id).first().realname))
        if Assigned.query.filter_by(user_id=s.user_id, test_id=id).first():
            assign_form.students.default.append(s.id)
    assign_form.process()
    return render_template('edit_test.html',
                           new_question_form=new_question_form, test=test, questions=questions,
                           answers=answers, new_answer_form=new_answer_form, assign_form=assign_form)


@app.route('/correct/<int:id>', methods=['GET', 'POST'])
@login_required
def correct(id):  # marks answer (ID) as correct
    answer = Answer.query.get(id)
    cor = Correct.query.filter_by(question_id=answer.question_id).first()
    if cor:  # exist correct
        cor.correct = decode(str(answer.id))
    else:
        cor = Correct(answer.question_id, decode(str(answer.id)))
        db.session.add(cor)
    db.session.commit()
    return redirect(url_for('edit_test', id=Question.query.get(answer.question_id).test_id))


@app.route('/edit_test_name/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_name(id):
    if current_user.is_student():
        return redirect(url_for('index'))
    teacher_id = Teacher.query.filter_by(user_id=current_user.id).first_or_404().id
    test = Test.query.get(id)
    if test.teacher_id == teacher_id:
        form = AddStringTestForm()
        if form.validate_on_submit():
            test.name = form.string.data
            db.session.commit()
            return redirect(url_for('edit_test', id=test.id))
        form.string.data = test.name
        return render_template('edit_name.html', form=form)


@app.route('/add_user', methods=['GET', 'POST'])
@app.route('/add_user/', methods=['GET', 'POST'])
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        password = decode(form.password.data)
        if not User.query.filter_by(password=password).first():  # user doesnt exist
            user = User(form.email.data, password, form.realname.data)
            db.session.add(user)
            db.session.commit()
            if form.category.data == 'Teacher':
                teacher = Teacher(user.id)
                db.session.add(teacher)
                db.session.commit()
                return redirect(url_for('index'))
            else:
                student = Student(user.id)
                db.session.add(student)
                db.session.commit()
        else:
            return "net"  # TODO: fix
    return render_template('add_user.html', form=form)