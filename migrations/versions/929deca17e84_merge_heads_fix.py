"""merge_heads_fix

Revision ID: 929deca17e84
Revises: 26565b90f9ac, d7aee1c6fa67
Create Date: 2025-12-15 15:24:31.922796

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "929deca17e84"
down_revision: Union[str, Sequence[str], None] = ("26565b90f9ac", "d7aee1c6fa67")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
