from datetime import datetime
import hashlib
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


# class for friends (followers)
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('monkeys.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('monkeys.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_fake(count=10):
        from random import seed, randint
        import forgery_py
        seed()
        monkey_count = Monkey.query.count()
        for i in range(count):
            m1 = Monkey.query.offset(randint(0, monkey_count - 1)).first()
            m2 = Monkey.query.offset(randint(0, monkey_count - 1)).first()
            f = Follow(follower_id=m1.id, followed_id=m2.id, timestamp=forgery_py.date.date(True))
            db.session.add(f)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


# class for best friends
class BestFriend(db.Model):
    __tablename__ = 'best_friends'
    friend_id = db.Column(db.Integer, db.ForeignKey('monkeys.id'),
                          primary_key=True, unique=True)
    best_friend_name = db.Column(db.String(64), db.ForeignKey('monkeys.monkeyname'))

    @staticmethod
    def generate_fake(count=10):
        from random import seed, randint
        seed()
        monkey_count = Monkey.query.count()
        for i in range(count):
            m1 = Monkey.query.offset(randint(0, monkey_count - 1)).first()
            m2 = Monkey.query.offset(randint(0, monkey_count - 1)).first()
            f = BestFriend(friend_id=m1.id, best_friend_name=m2.monkeyname)
            db.session.add(f)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


# class for creating monkey
class Monkey(UserMixin, db.Model):
    __tablename__ = 'monkeys'
    id = db.Column(db.Integer, primary_key=True)
    monkeyname = db.Column(db.String(64), unique=True, index=True)
    age = db.Column(db.Integer, default=18)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer, default=0)
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    best_friend_followed = db.relationship('BestFriend',
                                           foreign_keys=[BestFriend.friend_id],
                                           backref=db.backref('best_friend_follower', lazy='joined'),
                                           lazy='dynamic',
                                           cascade='all, delete-orphan')
    best_friend_followers = db.relationship('BestFriend',
                                            foreign_keys=[BestFriend.best_friend_name],
                                            backref=db.backref('best_friend_followed', lazy='joined'),
                                            lazy='dynamic',
                                            cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Monkey, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def is_administrator(self):
        return self.role == 1

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    @staticmethod
    def generate_fake(count=10):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            m = Monkey(email=forgery_py.internet.email_address(),
                       monkeyname=forgery_py.internet.user_name(True),
                       password=forgery_py.lorem_ipsum.word(),
                       confirmed=True)
            db.session.add(m)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    # helper functions to handle followings
    def follow(self, monkey):
        if not self.is_following(monkey):
            f = Follow(follower=self, followed=monkey)
            db.session.add(f)

    def unfollow(self, monkey):
        f = self.followed.filter_by(followed_id=monkey.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, monkey):
        return self.followed.filter_by(followed_id=monkey.id).first() is not None

    def is_followed_by(self, monkey):
        return self.followers.filter_by(follower_id=monkey.id).first() is not None

    # helper functions to handle best friends followings
    # bf - best friend
    def bf_follow(self, monkey):
        if not self.bf_is_following(monkey):
            f = BestFriend(best_friend_follower=self, best_friend_followed=monkey)
            db.session.add(f)

    def bf_unfollow(self, monkey):
        f = self.best_friend_followed.filter_by(best_friend_name=monkey.monkeyname).first()
        if f:
            db.session.delete(f)

    def bf_is_following(self, monkey):
        return self.best_friend_followed.filter_by(best_friend_name=monkey.monkeyname).first() is not None

    def bf_is_followed_by(self, monkey):
        return self.best_friend_followers.filter_by(friend_id=monkey.id).first() is not None

    def __repr__(self):
        return '<Monkey %r>' % self.monkeyname

# required by Flask
@login_manager.user_loader
def load_monkey(monkey_id):
    return Monkey.query.get(int(monkey_id))