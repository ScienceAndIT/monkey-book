from datetime import datetime
from app import create_app, db
from app.models import Monkey, Follow

app = create_app('default')


class Test_Models():

    def test_valid_reset_token(self):
        with app.app_context():
            m = Monkey(password='cat')
            db.session.add(m)
            db.session.commit()
            token = m.generate_reset_token()
            assert (m.reset_password(token, 'dog'))
            assert (m.verify_password('dog'))

    def test_invalid_reset_token(self):
        with app.app_context():
            m1 = Monkey(password='cat')
            m2 = Monkey(password='dog')
            db.session.add(m1)
            db.session.add(m2)
            db.session.commit()
            token = m1.generate_reset_token()
            assert not(m2.reset_password(token, 'horse'))
            assert (m2.verify_password('dog'))

    def test_valid_email_change_token(self):
        with app.app_context():
            m = Monkey(email='artur@test.com', password='cat')
            db.session.add(m)
            db.session.commit()
            token = m.generate_email_change_token('asia@example.org')
            assert (m.change_email(token))
            assert (m.email == 'asia@example.org')

    def test_invalid_email_change_token(self):
        with app.app_context():
            m1 = Monkey(email='artur2@test.com', password='cat')
            m2 = Monkey(email='susan@test.org', password='dog')
            db.session.add(m1)
            db.session.add(m2)
            db.session.commit()
            token = m1.generate_email_change_token('david@example.net')
            assert not (m2.change_email(token))
            assert (m2.email == 'susan@test.org')

    def test_duplicate_email_change_token(self):
        with app.app_context():
            m1 = Monkey(email='john@test.com', password='cat')
            m2 = Monkey(email='doris@test.org', password='dog')
            db.session.add(m1)
            db.session.add(m2)
            db.session.commit()
            token = m2.generate_email_change_token('john@test.com')
            assert not (m2.change_email(token))
            assert (m2.email == 'doris@test.org')

    def test_roles(self):
        m = Monkey(email='john@test.com', password='cat')
        assert not (m.is_administrator())

    def test_gravatar(self):
        with app.app_context():
            m = Monkey(email='john@example.com', password='cat')
            with app.test_request_context('/'):
                gravatar = m.gravatar()
                gravatar_256 = m.gravatar(size=256)
                gravatar_pg = m.gravatar(rating='pg')
                gravatar_retro = m.gravatar(default='retro')
            with app.test_request_context('/', base_url='https://example.com'):
                gravatar_ssl = m.gravatar()
            assert ('http://www.gravatar.com/avatar/' +
                    'd4c74594d841139328695756648b6bd6'in gravatar)
            assert ('s=256' in gravatar_256)
            assert ('r=pg' in gravatar_pg)
            assert ('d=retro' in gravatar_retro)
            assert ('https://secure.gravatar.com/avatar/' +
                    'd4c74594d841139328695756648b6bd6' in gravatar_ssl)

    def test_follows(self):
        with app.app_context():
            m1 = Monkey(email='monkey1@example.com', password='cat')
            m2 = Monkey(email='monkey2@example.org', password='dog')
            db.session.add(m1)
            db.session.add(m2)
            db.session.commit()
            assert not (m1.is_following(m2))
            assert not (m1.is_followed_by(m2))
            timestamp_before = datetime.utcnow()
            m1.follow(m2)
            db.session.add(m1)
            db.session.commit()
            timestamp_after = datetime.utcnow()
            assert (m1.is_following(m2))
            assert not (m1.is_followed_by(m2))
            assert (m2.is_followed_by(m1))
            assert (m1.followed.count() == 1)
            assert (m2.followers.count() == 1)
            f = m1.followed.all()[-1]
            assert (f.followed == m2)
            assert (timestamp_before <= f.timestamp <= timestamp_after)
            f = m2.followers.all()[-1]
            assert (f.follower == m1)
