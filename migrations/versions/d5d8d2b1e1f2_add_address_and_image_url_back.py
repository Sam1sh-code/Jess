"""add address and image_url back

Revision ID: d5d8d2b1e1f2
Revises: 6d12598ee983
Create Date: 2026-04-16 15:51:25.611273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd5d8d2b1e1f2'
down_revision: Union[str, Sequence[str], None] = '6d12598ee983'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    pass

def downgrade():
    pass