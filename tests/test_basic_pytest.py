from flask import current_app


class TestBasics():
    def test_app_exists(self):
        assert not (current_app is None)
