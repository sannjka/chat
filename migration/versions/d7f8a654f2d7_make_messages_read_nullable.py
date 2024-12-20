"""Make messages.read nullable

Revision ID: d7f8a654f2d7
Revises: 50531443bc48
Create Date: 2024-11-14 12:44:40.791947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7f8a654f2d7'
down_revision: Union[str, None] = '50531443bc48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('messages', 'read',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('messages', 'read',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###
