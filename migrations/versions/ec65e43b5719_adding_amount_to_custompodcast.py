"""adding amount to custompodcast

Revision ID: ec65e43b5719
Revises: 50c9915476fa
Create Date: 2024-08-05 00:06:13.199366

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "ec65e43b5719"
down_revision: Union[str, None] = "50c9915476fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "custompodcast",
        sa.Column("amount", sa.Integer(), nullable=False, server_default="1"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("custompodcast", "amount")
    # ### end Alembic commands ###
