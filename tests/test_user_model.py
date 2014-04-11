import unittest
from app.models import Monkey


class MonkeyModelTestCase(unittest.TestCase):

    def test_password_setter(self):
        m = Monkey(password='cat')
        self.assertTrme(m.password_hash is not None)

    def test_no_password_getter(self):
        m = Monkey(password='cat')
        with self.assertRaises(AttributeError):
            m.password

    def test_password_verification(self):
        m = Monkey(password='cat')
        self.assertTrme(m.verify_password('cat'))
        self.assertFalse(m.verify_password('dog'))

    def test_password_salts_are_random(self):
        m = Monkey(password='cat')
        m2 = Monkey(password='cat')
        self.assertTrue(m.password_hash != m2.password_hash)

    def test_valid_confirmation_token(self):
        m = Monkey(password='cat')
        db.session.add(m)
        db.session.commit()
        token = m.generate_confirmation_token()
        self.assertTrue(m.confirm(token))

    def test_invalid_confirmation_token(self):
        m1 = Monkey(password='cat')
        m2 = Monkey(password='dog')
        db.session.add(m1)
        db.session.add(m2)
        db.session.commit()
        token = m1.generate_confirmation_token()
        self.assertFalse(m2.confirm(token))

    def test_expired_confirmation_token(self):
        m = Monkey(password='cat')
        db.session.add(m)
        db.session.commit()
        token = m.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(m.confirm(token))