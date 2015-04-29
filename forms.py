from flask.ext.wtf import Form
from wtforms import PasswordField, SubmitField, StringField, RadioField, IntegerField, SelectMultipleField, DateField, \
    FieldList
# from wtforms.fields.html5 import DateField
from wtforms.validators import Required, Email
from wtforms.widgets import CheckboxInput, ListWidget


class IndexForm(Form):
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Submit')


class AddUserForm(Form):
    category = RadioField('category', choices=[('Teacher', 'Teacher'), ('Student', 'Student')], validators=[Required()])
    email = StringField('email', validators=[Required()])
    realname = StringField('realname', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    submit = SubmitField('Submit')


class AddStringTestForm(Form):
    string = StringField('name', validators=[Required()])
    submit = SubmitField('Submit')


class AddAnswerForm(Form):
    string = StringField('name', validators=[Required()])
    question = IntegerField()
    submit = SubmitField('Submit')


class DateForm(Form):
    date = DateField('date', format="%d-%m-%Y")
    submit = SubmitField('Submit')


class AssignForm(Form):
    students = SelectMultipleField('students', choices=[], default=[], widget=ListWidget(),
                                   option_widget=CheckboxInput())
    submit = SubmitField('Submit')


class Question(Form):
    question = RadioField()


class TestForm(Form):
    questions = FieldList(RadioField())
    submit = SubmitField('Submit')


class StudentForm(Form):
    realname = StringField('realname', validators=[Required()])
    category = RadioField('category', choices=[('Teacher', 'Teacher'), ('Student', 'Student')], validators=[Required()])
    email = StringField('email', validators=[Required(), Email()])
    submit = SubmitField('Submit')