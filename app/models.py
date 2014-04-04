from . import db
from flask.ext.login import UserMixin

# tables
friends = db.Table('friends',
                   db.Column('monkey_id', db.Integer, db.ForeignKey('monkeys.id')),
                   db.Column('friend_id', db.Integer))

best_friends = db.Table('best_friends',
                        db.Column('monkey_id', db.Integer, db.ForeignKey('monkeys.id'), unique=True),
                        db.Column('friend_id', db.Integer))


# main class
class Monkey(UserMixin, db.Model):
    __tablename__ = 'monkeys'
    id = db.Column(db.Integer, primary_key=True)
    monkeyname = db.Column(db.String(64), unique=True, index=True)
    age = db.Column(db.Integer, default=18)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Monkey %r>' % self.monkeyname