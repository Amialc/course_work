from flask.ext.wtf import Form
from wtforms import PasswordField, SubmitField,StringField, RadioField, HiddenField, IntegerField
from wtforms.validators import Required

class IndexForm(Form):
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Submit')

class AddUserForm(Form):
    category = RadioField('category',choices=[('Teacher','Teacher'),('Student','Student')],validators=[Required()])
    email = StringField('email',validators=[Required()])
    realname = StringField('realname',validators=[Required()])
    password = PasswordField('password',validators=[Required()])
    submit = SubmitField('Submit')

class AddStringTestForm(Form):
    string = StringField('name', validators=[Required()])
    submit = SubmitField('Submit')

class AddAnswerForm(Form):
    string = StringField('name', validators=[Required()])
    question = IntegerField()
    submit = SubmitField('Submit')