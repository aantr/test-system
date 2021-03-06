"""rm_test_table

Revision ID: 621677b74e33
Revises: 296b0034f245
Create Date: 2021-09-19 09:49:11.855628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '621677b74e33'
down_revision = '296b0034f245'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_table')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_table',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
