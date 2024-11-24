"""added title

Revision ID: 05b01228e150
Revises: ec65e43b5719
Create Date: 2024-11-22 02:28:40.422776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from xml.etree import ElementTree as ET

import sqlmodel.sql
import sqlmodel.sql.sqltypes
# revision identifiers, used by Alembic.
revision: str = '05b01228e150'
down_revision: Union[str, None] = 'ec65e43b5719'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    xmls = None

    engine = sa.create_engine("sqlite:///data/db.sqlite")
    with engine.begin() as session:
        xmls = session.exec_driver_sql("SELECT id,xml FROM podcast").all()
    engine.dispose()
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('podcast', sa.Column(
        'title', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default="Garbage"))
    # ### end Alembic commands ###
    op.get_bind().commit()
    for id, xml in xmls:
        item = ET.fromstring(xml)
        channel = item.find("channel")
        title = channel.find("title").text
        op.get_bind().exec_driver_sql(f"UPDATE podcast SET title = '{
            title}' WHERE id = {id};")
        op.get_bind().commit()


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('podcast', 'title')
    # ### end Alembic commands ###