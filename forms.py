from flask.ext.wtf import Form
from wtforms import PasswordField, SubmitField, StringField, RadioField, IntegerField, SelectMultipleField, widgets
from wtforms.validators import Required
from wtforms.widgets import html_params, ListWidget, CheckboxInput


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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


class AssignForm(Form):
    #students = MultiCheckboxField('students', choices=[])
    students = SelectMultipleField('students', choices=[], default=[], option_widget=CheckboxInput)

    submit = SubmitField('Submit')