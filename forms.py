from flask.ext.wtf import Form
from wtforms import PasswordField, SubmitField
from wtforms.validators import Required

class IndexForm(Form):
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Submit')