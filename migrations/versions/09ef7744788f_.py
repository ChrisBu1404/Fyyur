"""empty message

Revision ID: 09ef7744788f
Revises: 7ea8942fedea
Create Date: 2020-12-09 12:07:43.927098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09ef7744788f'
down_revision = '7ea8942fedea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###