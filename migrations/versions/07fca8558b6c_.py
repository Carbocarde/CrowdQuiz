"""empty message

Revision ID: 07fca8558b6c
Revises: 34402d0e1bc7
Create Date: 2021-01-07 22:26:04.511824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07fca8558b6c'
down_revision = '34402d0e1bc7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('exam_structure_suggestion', sa.Column('section_id', sa.Integer(), nullable=True))
    op.drop_constraint('exam_structure_suggestion_class_id_fkey', 'exam_structure_suggestion', type_='foreignkey')
    op.create_foreign_key(None, 'exam_structure_suggestion', 'section', ['section_id'], ['id'])
    op.drop_column('exam_structure_suggestion', 'class_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('exam_structure_suggestion', sa.Column('class_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'exam_structure_suggestion', type_='foreignkey')
    op.create_foreign_key('exam_structure_suggestion_class_id_fkey', 'exam_structure_suggestion', 'class', ['class_id'], ['id'])
    op.drop_column('exam_structure_suggestion', 'section_id')
    # ### end Alembic commands ###