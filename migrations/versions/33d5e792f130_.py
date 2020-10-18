"""empty message

Revision ID: 33d5e792f130
Revises: c946f9300775
Create Date: 2020-10-18 02:55:59.523756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33d5e792f130'
down_revision = 'c946f9300775'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('question_eval',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('fair', sa.Boolean(), nullable=True),
    sa.Column('skipped', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('contributionPoints', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'contributionPoints')
    op.drop_table('question_eval')
    # ### end Alembic commands ###