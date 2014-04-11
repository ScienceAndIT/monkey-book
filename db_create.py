import os
from app import db
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
db.create_all()