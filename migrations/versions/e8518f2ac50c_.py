"""empty message

Revision ID: e8518f2ac50c
Revises: 31f1a3874063
Create Date: 2020-12-09 15:42:03.603373

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8518f2ac50c'
down_revision = '31f1a3874063'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('study_set_term',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_answer_id', sa.Integer(), nullable=True),
    sa.Column('exam_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['exam_id'], ['exam.id'], ),
    sa.ForeignKeyConstraint(['question_answer_id'], ['questionanswer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('follow_exam_topic')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follow_exam_topic',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('exam_topic_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['exam_topic_id'], ['exam_topics.id'], name='follow_exam_topic_exam_topic_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='follow_exam_topic_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='follow_exam_topic_pkey')
    )
    op.drop_table('study_set_term')
    # ### end Alembic commands ###
