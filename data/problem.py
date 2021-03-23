import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

problem_to_category = sqlalchemy.Table(
    'problem_to_category',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('problem', sqlalchemy.Integer, sqlalchemy.ForeignKey('problem.id')),
    sqlalchemy.Column('problem_category', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('problem_category.id'))
)


class Problem(SqlAlchemyBase):
    __tablename__ = 'problem'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    problem_tests_id = sqlalchemy.Column(sqlalchemy.Integer,
                                         sqlalchemy.ForeignKey('problem_tests.id'))
    problem_tests = orm.relation('ProblemTests')

    task_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('task.id'))
    task = orm.relation('Task')

    time_limit = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    memory_limit = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=True)

    solution = orm.relation('Solution', back_populates='problem')

    categories = orm.relation('ProblemCategory',
                              secondary='problem_to_category',
                              backref='problem')

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user = orm.relation('User')
