from flask.ext.wtf import Form
from wtforms import PasswordField, SubmitField,StringField, RadioField
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

class AddNameTestForm(Form):
    name = StringField('name', validators=[Required()])
    submit = SubmitField('Submit')

class AddQuestTestForm(Form):
    question = StringField('question', validators=[Required()])
    submit = SubmitField('Submit')