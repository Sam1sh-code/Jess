"""Update restaurant model

Revision ID: 6d12598ee983
Revises: b317c9229d1f
Create Date: 2026-04-14 21:35:07.020236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6d12598ee983'
down_revision: Union[str, Sequence[str], None] = 'b317c9229d1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Добавляем только наши новые колонки
    #op.add_column('restaurants', sa.Column('owner_id', sa.Integer(), nullable=True))
    #op.add_column('restaurants', sa.Column('address', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('rating', sa.Float(), nullable=True))
    op.add_column('restaurants', sa.Column('delivery_time_mins', sa.Integer(), nullable=True))
    #op.add_column('restaurants', sa.Column('latitude', sa.Float(), nullable=True))
    #op.add_column('restaurants', sa.Column('longitude', sa.Float(), nullable=True))
    
    # Создаем связь (ForeignKey)
    op.create_foreign_key(None, 'restaurants', 'users', ['owner_id'], ['id'])


def downgrade() -> None:
    # Мы идем только вперед, откатывать ничего не будем
    pass