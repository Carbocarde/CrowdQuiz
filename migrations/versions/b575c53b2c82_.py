"""empty message

Revision ID: b575c53b2c82
Revises: 33d5e792f130
Create Date: 2020-10-18 03:19:23.802833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b575c53b2c82'
down_revision = '33d5e792f130'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question_eval', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'question_eval', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'question_eval', type_='foreignkey')
    op.drop_column('question_eval', 'user_id')
    # ### end Alembic commands ###
