"""Empty init

Revision ID: bb9547f406c7
Revises: 00ac51e83198
Create Date: 2023-11-16 15:00:00.000000

"""
import sqlalchemy as sa
from adsputils import UTCDateTime, get_date

from alembic import op

# revision identifiers, used by Alembic.
revision = "bb9547f406c7"
down_revision = "00ac51e83198"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "affil_inst",
        sa.Column("inst_key", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("inst_id", sa.String(), nullable=False),
        sa.Column("inst_parents", sa.String(), nullable=True),
        sa.Column("inst_canonical", sa.String(), nullable=False),
        sa.Column("inst_abbreviation", sa.String(), nullable=False),
        sa.Column("inst_location", sa.String(), nullable=True),
        sa.Column("inst_country", sa.String(), nullable=False),
        sa.Column("inst_iso_country", sa.String(), nullable=False),
        sa.Column("inst_rorid", sa.String(), nullable=True),
        sa.Column("inst_notes", sa.Text(), nullable=True),
        sa.Column("created", UTCDateTime, nullable=True, default=get_date),
        sa.Column("updated", UTCDateTime, nullable=True, onupdate=get_date),
        sa.PrimaryKeyConstraint("inst_key"),
        sa.UniqueConstraint("inst_id"),
    )

    op.create_table(
        "affil_data",
        sa.Column("data_key", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("affil_id", sa.String(), index=True, nullable=False),
        sa.Column("affil_string", sa.Text(), nullable=False),
        sa.Column("norm_string", sa.Text(), index=True, nullable=False),
        sa.Column("flagged", sa.Boolean(), nullable=True),
        sa.Column("created", UTCDateTime, nullable=True, default=get_date),
        sa.Column("updated", UTCDateTime, nullable=True, onupdate=get_date),
        # sa.ForeignKeyConstraint(["affil_id"], ["affil_inst.inst_id"]),
        sa.PrimaryKeyConstraint("data_key", "affil_id", "norm_string", name="lookup"),
        sa.UniqueConstraint("affil_string"),
    )

    op.create_index(
        "norm_index",
        "affil_data",
        ["norm_string"],
        unique=False,
        postgresql_using="HASH",
    )

    op.create_table(
        "affil_curation",
        sa.Column("curation_key", sa.Integer(), autoincrement=True,
            nullable=False),
        sa.Column("data_key", sa.Integer(), nullable=False),
        sa.Column("affil_id", sa.String(), nullable=False),
        sa.Column("affil_string", sa.String(), nullable=False),
        sa.Column("norm_string", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=False, default=""),
        sa.Column("created", UTCDateTime, nullable=True, default=get_date),
        sa.PrimaryKeyConstraint("curation_key", "data_key", "affil_id", "norm_string", name="dpairs"),
    )


    # end of Alembic upgrade


def downgrade() -> None:
    op.drop_table("affil_curation")
    op.drop_index("norm_index", table_name="affil_data", postgresql_using="hash")
    op.drop_table("affil_data")
    op.drop_table("affil_inst")

    # end of Alembic downgrade
