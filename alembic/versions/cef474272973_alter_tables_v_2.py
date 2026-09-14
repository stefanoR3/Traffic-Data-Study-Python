"""alter tables v.2

Revision ID: cef474272973
Revises: a76ba70d7bc0
Create Date: 2026-09-12 12:54:10.159378

"""
from typing import Sequence, Union

from alembic import op #op = operations
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cef474272973'
down_revision: Union[str, Sequence[str], None] = 'a76ba70d7bc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    #auxiliary table used to move data in batch operation
    #it can presist in data.db if an error while batch
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_incident_header")
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_incident_info")
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_incident_event")

    #with statement ensure a connection to perform the batch operations!
    #to use a with statement, the functions needs instructions inside metadata (__enter__ & __exit__)

    #sa.column -> column information
    #op.add_column -> push it inside transaction (waiting list)
    #with -> when closing, looks inside alembic context

    #sql automatically gives a random name to the constraint (sqlite give None)
    #for alembic and sqlalchemy to modify a constraint, it needs that name
    #thehrefore, we need to specify the name in the table sqlalchemy creation explicitelly, to not look inside the db
    #we can use a convection dictionary to automatically assing names to constraints etc.

    #eflect = True used to inspect and modify with metadata rules before batching
    with op.batch_alter_table("incident_header", reflect=True) as batch_op:
        batch_op.alter_column('id', new_column_name='main_id', existing_type=sa.String)

    with op.batch_alter_table("incident_info", reflect=True) as batch_op:
        batch_op.alter_column('id', new_column_name='snapshot_id', existing_type=sa.String)
        batch_op.alter_column('incident_id', new_column_name='main_id', existing_type=sa.String)
        batch_op.add_column(sa.Column('magnitude_of_delay', sa.Integer))
        batch_op.add_column(sa.Column('last_report_time', sa.String(21)))
        batch_op.drop_column('info_date')

    with op.batch_alter_table("incident_event", reflect=True) as batch_op:
        batch_op.alter_column('id', new_column_name='event_id', existing_type=sa.String)
        batch_op.drop_column('incident_id')
        batch_op.add_column(sa.Column('snapshot_id', sa.ForeignKey("incident_info.snapshot_id"), nullable=False))

#downgrade needs to be overhead

def downgrade() -> None:
    with op.batch_alter_table("incident_event", reflect=True) as batch_op:
        batch_op.alter_column('event_id', new_column_name='id', existing_type=sa.String)
        batch_op.drop_column('snapshot_id')
        batch_op.add_column(sa.Column('incident_id', sa.ForeignKey("incident_info.id"), nullable=False))

    with op.batch_alter_table("incident_info", reflect=True) as batch_op:
        batch_op.alter_column('snapshot_id', new_column_name='id', existing_type=sa.String)
        batch_op.alter_column('main_id', new_column_name='incident_id', existing_type=sa.String)
        batch_op.drop_column('magnitude_of_delay')
        batch_op.drop_column('last_report_time')
        batch_op.add_column(sa.Column('info_date', sa.DateTime))

    with op.batch_alter_table('incident_header', reflect=True) as batch_op:
        batch_op.alter_column('main_id', new_column_name='id', existing_type=sa.String)

