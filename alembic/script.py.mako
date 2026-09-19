"""${context.get('message', '')}

Revision ID: ${context.get('up_revision')}
Revises: ${context.get('down_revision')}
Create Date: ${context.get('create_date')}

"""
from alembic import op
import sqlalchemy as sa
${context.get('imports', '')}

# revision identifiers, used by Alembic.
revision = ${repr(context.get('up_revision'))}
down_revision = ${repr(context.get('down_revision'))}
branch_labels = ${repr(context.get('branch_labels'))}
depends_on = ${repr(context.get('depends_on'))}


def upgrade() -> None:
    ${context.get('upgrades', 'pass')}


def downgrade() -> None:
    ${context.get('downgrades', 'pass')}