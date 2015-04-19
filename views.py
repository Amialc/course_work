from hashlib import md5

from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, g

from course import app, db, login_serializer, lm
from forms import IndexForm, AddUserForm, AddStringTestForm, AddAnswerForm, AssignForm, DateForm
from models import User, Teacher, Student, Test, Question, Answer, Assigned
from datetime import date
import time


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
    if test.teacher_id == teacher_id:
        sess = db.session()
        sess.delete(test)
        sess.commit()
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


@app.route('/test', methods=['GET', 'POST'])
@app.route('/test/', methods=['GET', 'POST'])
@login_required
def test():
    user_id = current_user.id
    if current_user.is_teacher() or current_user.is_admin():
        teacher_id = Teacher.query.filter_by(user_id=user_id).first().id
        tests = Test.query.filter_by(teacher_id=teacher_id).all()
        return render_template('test_teacher.html', tests=tests)
    else:
        tests = []
        for a in Assigned.query.filter_by(user_id=user_id).all():
            tests.append(a)
        return render_template('test_student.html', tests=tests)

#@app.route('/run_test',methods=['GET','POST'])
@app.route('/run_test/<int:id>', methods=['GET','POST'])
def run(id):
    if current_user.is_student():
        return redirect(url_for('index'))
    Test.query.get(id).running = True
    db.session.commit()
    return redirect(url_for('test'))

@app.route('/off_test/<int:id>', methods=['GET','POST'])
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
    date_form = DateForm()
    date_error = None
    if date_form.validate_on_submit():
        print date_form.data
        if date_form.date.data < date.today(): #if date is less today
            date_error = "Date must be not less than today"
        else:
            test.final_date = date_form.date.data
            db.session.commit()
        return redirect(url_for('edit_test', id=test.id))
    date_form.date.data = test.final_date
    return render_template('edit_test.html',
                           new_question_form=new_question_form, test=test, questions=questions,
                           answers=answers, new_answer_form=new_answer_form, assign_form=assign_form,
                           date_form=date_form, date_error = date_error)


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