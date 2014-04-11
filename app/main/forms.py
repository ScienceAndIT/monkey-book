from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, BooleanField, TextField, SelectField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Monkey


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    age = IntegerField('What is your age?', validators=[Required()])
    email = TextField('Email', validators=[Required(), Email()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    monkeyname = StringField('New monkey name', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Monkey names must have only letters, '
                                          'numbers, dots or underscores')])
    age = IntegerField('Real age', validators=[Required()])

    #role = IntegerField('Role (0 - user, 1 - admin)', validators=[Required()])
    #confirmed = BooleanField('Confirmed')
    #name = StringField('Real name', validators=[Length(0, 64)])
    #location = StringField('Location', validators=[Length(0, 64)])
    #about_me = TextAreaField('About me')
    submit = SubmitField('Submit changes')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    monkeyname = StringField('New monkey name', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Monkey names must have only letters, '
                                          'numbers, dots or underscores')])
    age = IntegerField('Real age', validators=[Required()])
    role = IntegerField('Role (0 - user, 1 - admin)', validators=[Required()])
    confirmed = BooleanField('Confirmed')

    #name = StringField('Real name', validators=[Length(0, 64)])
    #location = StringField('Location', validators=[Length(0, 64)])
    #about_me = TextAreaField('About me')
    submit = SubmitField('Submit changes')

    def __init__(self, monkey, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        """self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
                             """
        self.monkey = monkey

    def validate_email(self, field):
        if field.data != self.monkey.email and Monkey.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.monkey.monkeyname and Monkey.query.filter_by(monkeyname=field.data).first():
            raise ValidationError('Monkey name already in use.')