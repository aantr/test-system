from datetime import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship, backref

from .db_session import SqlAlchemyBase
from .user import User

problem_to_session = sqlalchemy.Table(
    'problem_to_session',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('problem', sqlalchemy.Integer, sqlalchemy.ForeignKey('problem.id')),
    sqlalchemy.Column('session', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('session.id'))
)


class SessionMember(SqlAlchemyBase):
    __tablename__ = 'session_member'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    member_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    member = sqlalchemy.orm.relation('User')
    session_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('session.id'))
    session = sqlalchemy.orm.relation('Session')


class Session(SqlAlchemyBase):
    __tablename__ = 'session'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    join_action_str_id = sqlalchemy.Column(sqlalchemy.String,
                                           sqlalchemy.ForeignKey('action.str_id'),
                                           nullable=True)
    join_action = orm.relation('Action')

    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    started = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)

    problems = orm.relation('Problem',
                            secondary='problem_to_session',
                            backref='problem_session')

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user = orm.relation('User')
