"""Added university type column

Revision ID: 508d25d35176
Revises: 1f1c4f97df13
Create Date: 2014-03-03 16:25:16.258003

"""

# revision identifiers, used by Alembic.
revision = '508d25d35176'
down_revision = '4eb0d0716ca0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('university', sa.Column('private', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('university', 'private')
