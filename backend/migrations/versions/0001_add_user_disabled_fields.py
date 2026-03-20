"""add user disabled fields

Revision ID: 0001_add_user_disabled_fields
Revises: 
Create Date: 2025-12-24

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_add_user_disabled_fields"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use inspector to check if columns exist before adding them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("users")]
    
    if "disabled_reason" not in columns:
        op.add_column("users", sa.Column("disabled_reason", sa.Text(), nullable=True))
    if "disabled_at" not in columns:
        op.add_column("users", sa.Column("disabled_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "disabled_at")
    op.drop_column("users", "disabled_reason")
