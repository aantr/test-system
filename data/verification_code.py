import sqlalchemy
from .db_session import SqlAlchemyBase


class VerificationCode(SqlAlchemyBase):
    __tablename__ = 'verification_code'

    str_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    token = sqlalchemy.Column(sqlalchemy.String, nullable=False)
