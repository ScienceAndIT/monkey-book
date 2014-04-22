from datetime import datetime
from flask import render_template, redirect, url_for, current_app, flash,\
    request, Markup
from flask.ext.login import login_required, current_user
from sqlalchemy import func
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Monkey, Follow, BestFriend


@main.route('/')
def index():
    return render_template('index.html',
                           current_time=datetime.utcnow())


# displaying all profiles sorted by names, default option for viewing monkeys
@main.route('/profiles/by-names', defaults={'page': 1})
@main.route('/profiles/by-names/page/<int:page>')
@login_required
def view_profiles(page):
    pagination = Monkey.query.\
        order_by(Monkey.monkeyname.asc()).\
        paginate(page, per_page=current_app.config['MONKEYS_PER_PAGE'],
                 error_out=False)
    profiles = pagination.items
    return render_template('view_profiles_by_names.html',
                           profiles=profiles, pagination=pagination)


# displaying all profiles sorted by number of friends
@main.route('/profiles/by-number-of-friends', defaults={'page': 1})
@main.route('/profiles/by-number-of-friends/page/<int:page>')
@login_required
def view_profiles_by_number_of_friends(page):
    pagination = Monkey.query.\
        outerjoin(Follow, Follow.follower_id == Monkey.id).\
        outerjoin(BestFriend, BestFriend.friend_id == Monkey.id).\
        group_by(Monkey.id).\
        order_by(db.func.count(Follow.follower_id).desc(),
                 db.func.count(BestFriend.friend_id).desc()).\
        paginate(page, per_page=current_app.config['MONKEYS_PER_PAGE'],
                 error_out=False)
    profiles = pagination.items
    return render_template('view_profiles_by_number_of_friends.html',
                           profiles=profiles, pagination=pagination)


# displaying all profiles sorted by name of the best friend
@main.route('/profiles/by-name-of-the-best-friend', defaults={'page': 1})
@main.route('/profiles/by-name-of-the-best-friend/page/<int:page>')
@login_required
def view_profiles_by_name_of_the_best_friend(page):
    pagination = Monkey.query.\
        outerjoin(BestFriend, BestFriend.friend_id == Monkey.id).\
        filter(BestFriend.friend_id == Monkey.id).\
        order_by(BestFriend.best_friend_name.asc()).\
        paginate(page, per_page=current_app.config['MONKEYS_PER_PAGE'],
                 error_out=False)
    profiles = pagination.items
    return render_template('view_profiles_by_name_of_the_best_friend.html',
                           profiles=profiles, pagination=pagination)


# removing monkey
@main.route('/remove/<int:id>', methods=['GET', 'POST'])
@login_required
def remove_monkey(id):
    monkey = Monkey.query.get_or_404(id)
    page = int(request.args.get('page', 1))
    pagination = Monkey.query.order_by(Monkey.monkeyname.asc())\
        .paginate(page, per_page=current_app.config['MONKEYS_PER_PAGE'],
                  error_out=False)
    profiles = pagination.items
    if monkey.is_administrator():
        flash("You can't remove admin monkey!")
    else:
        db.session.delete(monkey)
        flash("The monkey has been removed!")
    return render_template('view_profiles_by_names.html',
                           profiles=profiles, pagination=pagination)


# displaying info about monkey
@main.route('/monkey/<monkeyname>')
def monkey(monkeyname):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first_or_404()
    return render_template('monkey.html',
                           monkey=monkey)


# profile's edition for plain monkey
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.monkeyname = form.monkeyname.data
        current_user.email = form.email.data
        current_user.age = form.age.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.monkey',
                                monkeyname=current_user.monkeyname))
    form.monkeyname.data = current_user.monkeyname
    form.email.data = current_user.email
    form.age.data = current_user.age
    return render_template('edit_profile.html', form=form)


# profile's edition for admin
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    monkey = Monkey.query.get_or_404(id)
    form = EditProfileAdminForm(monkey=monkey)
    if form.validate_on_submit():
        monkey.email = form.email.data
        monkey.monkeyname = form.monkeyname.data
        monkey.age = form.age.data
        monkey.confirmed = form.confirmed.data
        monkey.role = form.role.data
        db.session.add(current_user)
        flash('The profile has been updated.')
        return redirect(url_for('.monkey',
                                monkeyname=monkey.monkeyname))
    form.email.data = monkey.email
    form.monkeyname.data = monkey.monkeyname
    form.confirmed.data = monkey.confirmed
    form.role.data = monkey.role
    return render_template('edit_profile.html',
                           form=form,
                           monkey=monkey)


# displaying information about friends
@main.route('/friend/<monkeyname>')
@login_required
def follow(monkeyname):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first()
    if monkey is None:
        flash('Invalid monkey.')
        return redirect(url_for('.view_profiles'))
    if current_user.is_following(monkey):
        flash('You are already following this monkey.')
        return redirect(url_for('.monkey', monkeyname=monkeyname))
    current_user.follow(monkey)
    flash('You are now following %s.' % monkeyname)
    return redirect(url_for('.monkey', monkeyname=monkeyname))


@main.route('/unfriend/<monkeyname>')
@login_required
def unfollow(monkeyname):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first()
    if monkey is None:
        flash('Invalid Monkey.')
        return redirect(url_for('.view_profiles'))
    if not current_user.is_following(monkey):
        flash('You are not a friend of this monkey.')
        return redirect(url_for('.monkey', monkeyname=monkeyname))
    current_user.unfollow(monkey)
    flash('You are not a friend of %s anymore.' % monkeyname)
    return redirect(url_for('.monkey', monkeyname=monkeyname))


@main.route('/followers/<monkeyname>', defaults={'page': 1})
@main.route('/followers/<monkeyname>/page/<int:page>')
def followers(monkeyname, page):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first()
    if monkey is None:
        flash('Invalid Monkey.')
        return redirect(url_for('.index'))
    pagination = monkey.followers.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'monkey': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',
                           monkey=monkey, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<monkeyname>', defaults={'page': 1})
@main.route('/followed-by/<monkeyname>/page/<int:page>')
def followed_by(monkeyname, page):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first()
    if monkey is None:
        flash('Invalid monkey.')
        return redirect(url_for('.index'))
    pagination = monkey.followed.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'monkey': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', monkey=monkey,
                           title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


#Four functions below are to display information about best friends
@main.route('/new-best-friend/<monkeyname>')
@login_required
def bf_follow(monkeyname):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first()
    if monkey is None:
        flash('Invalid monkey.')
        return redirect(url_for('.view_profiles'))
    if current_user.best_friend_followed.count() > 0:
        flash('You can only have one best friend!')
        return redirect(url_for('.view_profiles'))
    if current_user.bf_is_following(monkey):
        flash('You are already best friend of this monkey.')
        return redirect(url_for('.monkey', monkeyname=monkeyname))
    current_user.bf_follow(monkey)
    flash('%s is now your best friend.' % monkeyname)
    return redirect(url_for('.monkey', monkeyname=monkeyname))


@main.route('/no-best-friend/<monkeyname>')
@login_required
def bf_unfollow(monkeyname):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first()
    if monkey is None:
        flash('Invalid monkey.')
        return redirect(url_for('.view_profiles'))
    if not current_user.bf_is_following(monkey):
        flash('You are not best friend of this monkey.')
        return redirect(url_for('.monkey', monkeyname=monkeyname))
    current_user.bf_unfollow(monkey)
    flash('%s is not your best friend anymore.' % monkeyname)
    return redirect(url_for('.monkey', monkeyname=monkeyname))


@main.route('/best-friend-follower/<monkeyname>', defaults={'page': 1})
@main.route('/best-friend-follower/<monkeyname>/page/<int:page>')
def bf_follower(monkeyname, page):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first()
    if monkey is None:
        flash('Invalid Monkey.')
        return redirect(url_for('.index'))
    pagination = monkey.best_friend_followers.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False)
    best_friends = [{'monkey': item.best_friend_follower}
                    for item in pagination.items]
    return render_template('bf_followers.html',
                           monkey=monkey, title=" - here is your best friend follower",
                           endpoint='.bf_follower', pagination=pagination,
                           best_friends=best_friends)


@main.route('/best-friend-followed-by/<monkeyname>', defaults={'page': 1})
@main.route('/best-friend-followed-by/<monkeyname>/page/<int:page>')
def bf_followed_by(monkeyname, page):
    monkey = Monkey.query.filter_by(monkeyname=monkeyname).first()
    if monkey is None:
        flash('Invalid monkey.')
        return redirect(url_for('.index'))
    pagination = monkey.best_friend_followed.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False)
    best_friends = [{'monkey': item.best_friend_followed}
               for item in pagination.items]
    return render_template('bf_followers.html', monkey=monkey,
                           title=" - here is your best friend",
                           endpoint='.bf_followed_by', pagination=pagination,
                           best_friends=best_friends)