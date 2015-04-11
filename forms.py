from flask.ext.wtf import Form
from wtforms import TextField,PasswordField
from wtforms.validators import Required

class IndexForm(Form):
    password = PasswordField('Password', validators=[Required()])