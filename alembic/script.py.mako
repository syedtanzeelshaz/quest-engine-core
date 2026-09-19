<%
from tools.git_identity import get_git_identity

git_identity = get_git_identity()
%>
"""${context.get('message', '')}

Revision ID: ${context.get('up_revision')}
Revises: ${context.get('down_revision')}
Create Date: ${context.get('create_date')}

"""
from alembic import op
import sqlalchemy as sa
${context.get('imports', '')}

# revision identifiers
revision = ${repr(context.get('up_revision'))}
down_revision = ${repr(context.get('down_revision'))}
branch_labels = ${repr(context.get('branch_labels'))}
depends_on = ${repr(context.get('depends_on'))}

# author metadata
author_name = ${repr(git_identity.name)}
author_email = ${repr(git_identity.email)}


def upgrade() -> None:
    ${context.get('upgrades', 'pass')}


def downgrade() -> None:
    ${context.get('downgrades', 'pass')}