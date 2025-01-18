"""Empty init

Revision ID: 8f662cf50a2f
Revises: c54d158658da
Create Date: 2024-12-13 16:00:00.000000

"""
import sqlalchemy as sa
from adsputils import UTCDateTime, get_date

from alembic import op

# revision identifiers, used by Alembic.
revision = "8f662cf50a2f"
down_revision = "c54d158658da"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "solr_data",
        sa.Column("solr_data_key", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bibcode", sa.String(), nullable=False),
        sa.Column("collections", sa.String(), nullable=False),
        sa.Column("refereed", sa.Boolean(), nullable=False),
        sa.Column("affil_data", sa.JSON(), nullable=True)
        sa.PrimaryKeyConstraint("solr_data_key"),
        sa.UniqueConstraint("bibcode"),
    )

    # end of Alembic upgrade


def downgrade() -> None:
    op.drop_table("solr_data")

    # end of Alembic downgrade
