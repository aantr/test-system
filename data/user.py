import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'user'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    solution = orm.relation('Solution', back_populates='user')
    problem = orm.relation('Problem', back_populates='user')
    session = orm.relation('Session', back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
