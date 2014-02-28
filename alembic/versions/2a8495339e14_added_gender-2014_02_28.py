"""Added gender

Revision ID: 2a8495339e14
Revises: None
Create Date: 2014-02-28 12:01:49.873900

"""

# revision identifiers, used by Alembic.
revision = '2a8495339e14'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('person', sa.Column('gender', sa.UnicodeText(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', 'gender')
    ### end Alembic commands ###
