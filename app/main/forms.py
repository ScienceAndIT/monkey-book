from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, IntegerField, TextField
from wtforms.validators import Required, Email


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    age = IntegerField('What is your age?', validators=[Required()])
    email = TextField('Email', validators=[Required(), Email()])
    submit = SubmitField('Submit')