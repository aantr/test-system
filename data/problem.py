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

    task_text = sqlalchemy.Column(sqlalchemy.Text)
    images_ids = sqlalchemy.Column(sqlalchemy.String)
    input_text = sqlalchemy.Column(sqlalchemy.Text)
    output_text = sqlalchemy.Column(sqlalchemy.Text)
    examples = sqlalchemy.Column(sqlalchemy.Text)
    note = sqlalchemy.Column(sqlalchemy.Text)

    time_limit = sqlalchemy.Column(sqlalchemy.Float)
    memory_limit = sqlalchemy.Column(sqlalchemy.BigInteger)

    solution = orm.relation('Solution', back_populates='problem')

    categories = orm.relation('ProblemCategory',
                              secondary='problem_to_category',
                              backref='problem')

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user = orm.relation('User')

    def get_time_limit(self):
        return f'{self.time_limit} s'

    def get_memory_limit(self):
        return f'{self.memory_limit // 1024} Kb'
