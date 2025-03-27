"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create plugins table
    op.create_table(
        'plugins',
        sa.Column('id', sa.String(24), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('manifest', sa.Text, nullable=False),
        sa.Column('image_name', sa.String(255), nullable=False),
        sa.Column('registry_url', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('true'))
    )

    # Add plugin_id to deployments table
    op.add_column(
        'deployments',
        sa.Column('plugin_id', sa.String(24), sa.ForeignKey('plugins.id'))
    )


def downgrade() -> None:
    op.drop_column('deployments', 'plugin_id')
    op.drop_table('plugins') 