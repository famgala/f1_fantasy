"""Add user visibility and pending invites

Revision ID: add_user_visibility
Revises: previous_revision
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_user_visibility'
down_revision = '772a8434f699'
branch_labels = None
depends_on = None

def upgrade():
    # Add visibility column
    op.add_column('users', sa.Column('visibility', sa.String(20), nullable=False, server_default='public'))
    
    # Add pending_invites column
    op.add_column('users', sa.Column('pending_invites', sa.JSON(), nullable=False, server_default='[]'))

def downgrade():
    op.drop_column('users', 'pending_invites')
    op.drop_column('users', 'visibility') 