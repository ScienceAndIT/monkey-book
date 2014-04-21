import time
import pytest
from app import create_app, db
from app.models import Monkey

app = create_app('default')


class TestMonkeyModel():

    def test_password_setter(self):
        m = Monkey(password='cat')
        assert (m.password_hash is not None)

    def test_no_password_getter(self):
        m = Monkey(password='cat')
        with pytest.raises(AttributeError):
            m.password

    def test_password_verification(self):
        m = Monkey(password='cat')
        assert (m.verify_password('cat'))
        assert not (m.verify_password('dog'))

    def test_password_salts_are_random(self):
        m = Monkey(password='cat')
        m2 = Monkey(password='cat')
        assert (m.password_hash != m2.password_hash)

    def test_valid_confirmation_token(self):
        with app.app_context():
            m = Monkey(password='cat')
            db.session.add(m)
            db.session.commit()
            token = m.generate_confirmation_token()
            assert (m.confirm(token))

    def test_invalid_confirmation_token(self):
        with app.app_context():
            m1 = Monkey(password='cat')
            m2 = Monkey(password='dog')
            db.session.add(m1)
            db.session.add(m2)
            db.session.commit()
            token = m1.generate_confirmation_token()
            assert not (m2.confirm(token))

    def test_expired_confirmation_token(self):
        with app.app_context():
            m = Monkey(password='cat')
            db.session.add(m)
            db.session.commit()
            token = m.generate_confirmation_token(1)
            time.sleep(2)
            assert not(m.confirm(token))
