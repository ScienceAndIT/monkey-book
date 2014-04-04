from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import Monkey
from ..email import send_email
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        monkey = Monkey.query.filter_by(monkeyname=form.name.data).first()
        if monkey is None:
            monkey = Monkey(monkeyname=form.name.data, age=form.age.data, email=form.email.data)
            db.session.add(monkey)
            session['known'] = False
            send_email(current_app.config['MONKEYBOOK_ADMIN'], 'New User', 'mail/new_user', monkey=monkey)
            #if app.config['MONKEYBOOK_ADMIN']:
                #send_email(app.config['MONKEYBOOK_ADMIN'], 'New User',
                           #'mail/new_user', monkey=monkey)

        else:
            session['known'] = True
            session['name'] = form.name.data
            form.name.data = ''
            session['age'] = form.age.data
            form.age.data = ''
            session['email'] = form.email.data
            form.email.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html', form=form,
                           name=session.get('name'),
                           known=session.get('known', False)) # age=session.get('age'), email=session.get('email'),