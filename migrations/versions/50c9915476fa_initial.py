"""initial

Revision ID: 50c9915476fa
Revises: 
Create Date: 2024-08-04 23:30:34.905686

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "50c9915476fa"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "podcast",
        sa.Column("xml", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("xml"),
    )
    op.create_table(
        "custompodcast",
        sa.Column("dateToPostAt", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("podcast_id", sa.Integer(), nullable=True),
        sa.Column("freq", sa.Integer(), nullable=False),
        sa.Column("interval", sa.Integer(), nullable=False),
        sa.Column("UUID", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["podcast_id"],
            ["podcast.id"],
        ),
        sa.PrimaryKeyConstraint("UUID"),
    )
    op.create_table(
        "episode",
        sa.Column("xml", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("podcast_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["podcast_id"],
            ["podcast.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("episode")
    op.drop_table("custompodcast")
    op.drop_table("podcast")
    # ### end Alembic commands ###
