"""alter table with datestamp

Revision ID: a76ba70d7bc0
Revises: 
Create Date: 2026-08-12 15:53:42.700404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'a76ba70d7bc0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


#batch_alter_table to migrate to a new table, copy the data and destroy the original 
#alembic made this easier to make all those steps with the batch_alter_table function,
#while also keeping track of the migration like github

def upgrade() -> None:
    with op.batch_alter_table("incident_info") as batch_op:
        batch_op.add_column(sa.Column("info_date", sa.DateTime, default=datetime.now()))

    with op.batch_alter_table("incident_header") as batch_op:
        batch_op.drop_column('type')



def downgrade() -> None:
    with op.batch_alter_table("incidents_info") as batch_op:
        batch_op.drop_column("info_date")

    
