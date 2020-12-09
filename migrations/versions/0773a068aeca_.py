"""empty message

Revision ID: 0773a068aeca
Revises: 09ef7744788f
Create Date: 2020-12-09 12:08:06.876128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0773a068aeca'
down_revision = '09ef7744788f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###
