# ACGS/alembic/script.py.mako
"""merge_constitutional_council_and_principle_enhancements

Revision ID: 03526f673a96
Revises: fb393352ecc7, 006_cc_schema
Create Date: 2025-06-01 07:23:22.688928

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "03526f673a96"
down_revision: str | None = ("fb393352ecc7", "006_cc_schema")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
