from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required,\
    current_user
from . import auth
from .. import db
from ..models import Monkey
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm


# if monkey isn't confirmed
@auth.before_app_request
def before_request():
    if current_user.is_authenticated() \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))


# if monkey is unconfirmed
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect('main.index')
    return render_template('auth/unconfirmed.html')


# logging in
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        monkey = Monkey.query.filter_by(email=form.email.data).first()
        if monkey is not None and monkey.verify_password(form.password.data):
            login_user(monkey, form.remember_me.data)
            return redirect(request.args.get('next') or
                            url_for('main.view_profiles'))
        flash('Invalid monkey name or password.')
    return render_template('auth/login.html', form=form)


# logging out
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


# registration of new monkey and sending confirmation email
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        monkey = Monkey(monkeyname=form.monkeyname.data,
                        age=form.age.data,
                        email=form.email.data,
                        password=form.password.data)
        db.session.add(monkey)
        db.session.commit()
        token = monkey.generate_confirmation_token()
        send_email(monkey.email, 'Confirm Your Account',
                   'auth/email/confirm', monkey=monkey, token=token)
        flash('A confirmation email has been sent to you by email!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


# support after clicking into links with confirmation
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired!')
    return redirect(url_for('main.index'))


# sending another confirmation email
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', monkey=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


# changing password
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)
