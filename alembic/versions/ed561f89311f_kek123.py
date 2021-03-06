"""kek123

Revision ID: ed561f89311f
Revises: 621677b74e33
Create Date: 2021-09-20 14:34:10.887560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed561f89311f'
down_revision = '621677b74e33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('action',
    sa.Column('str_id', sa.String(), nullable=False),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('str_id')
    )
    op.create_table('image',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('extension', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('problem_category',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('problem_tests',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('source_code',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_result',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('confirmed_email', sa.Boolean(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username'),
    sa.UniqueConstraint('username')
    )
    op.create_table('group',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('join_action_str_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['join_action_str_id'], ['action.str_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invite',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_to_id', sa.Integer(), nullable=True),
    sa.Column('user_from_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_from_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_to_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('problem',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('problem_tests_id', sa.Integer(), nullable=True),
    sa.Column('task_text', sa.Text(), nullable=True),
    sa.Column('images_ids', sa.String(), nullable=True),
    sa.Column('input_text', sa.Text(), nullable=True),
    sa.Column('output_text', sa.Text(), nullable=True),
    sa.Column('examples', sa.Text(), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('time_limit', sa.Float(), nullable=True),
    sa.Column('memory_limit', sa.BigInteger(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('display_problemset', sa.Boolean(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['problem_tests_id'], ['problem_tests.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('session',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('duration', sa.Time(), nullable=True),
    sa.Column('join_action_str_id', sa.String(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('started', sa.Boolean(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['join_action_str_id'], ['action.str_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('group_member',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('problem_to_category',
    sa.Column('problem', sa.Integer(), nullable=True),
    sa.Column('problem_category', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['problem'], ['problem.id'], ),
    sa.ForeignKeyConstraint(['problem_category'], ['problem_category.id'], )
    )
    op.create_table('problem_to_session',
    sa.Column('problem', sa.Integer(), nullable=True),
    sa.Column('session', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['problem'], ['problem.id'], ),
    sa.ForeignKeyConstraint(['session'], ['session.id'], )
    )
    op.create_table('session_member',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('session_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['member_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['session.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('solution',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('lang_code_name', sa.String(), nullable=True),
    sa.Column('sent_date', sa.DateTime(), nullable=True),
    sa.Column('problem_id', sa.Integer(), nullable=True),
    sa.Column('test_result_id', sa.Integer(), nullable=True),
    sa.Column('source_code_id', sa.Integer(), nullable=True),
    sa.Column('session_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('state_arg', sa.Integer(), nullable=True),
    sa.Column('max_time', sa.Float(), nullable=True),
    sa.Column('max_memory', sa.BigInteger(), nullable=True),
    sa.Column('failed_test', sa.Integer(), nullable=True),
    sa.Column('success', sa.Boolean(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['problem_id'], ['problem.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['session.id'], ),
    sa.ForeignKeyConstraint(['source_code_id'], ['source_code.id'], ),
    sa.ForeignKeyConstraint(['test_result_id'], ['test_result.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('solution')
    op.drop_table('session_member')
    op.drop_table('problem_to_session')
    op.drop_table('problem_to_category')
    op.drop_table('group_member')
    op.drop_table('session')
    op.drop_table('problem')
    op.drop_table('invite')
    op.drop_table('group')
    op.drop_table('user')
    op.drop_table('test_result')
    op.drop_table('source_code')
    op.drop_table('problem_tests')
    op.drop_table('problem_category')
    op.drop_table('image')
    op.drop_table('action')
    # ### end Alembic commands ###
