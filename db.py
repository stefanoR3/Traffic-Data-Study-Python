from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, ForeignKey, insert, select, DateTime, delete
from typing import List, Optional
import json
import datetime

#engine for connection and exectuion, metadata for tables namespace
#it does create a new sqlite database in the current directory
engine = create_engine("sqlite+pysqlite:///data.db") #echo = True

#convention used to
convention = {
    "ix": "ix_%(column_0_label)s", #for indexes
    "uq": "uq_%(table_name)s_%(column_0_name)s", #for unique constraints
    "ck": "ck_%(table_name)s_%(constraint_name)s", #for ceck constraints
    "fk": "fk_%(table_name)s_%(column_0_name)s", #for foreign keys
    "pk": "pk_%(table_name)s" #for primary keys
}

#we inject this rule inside the metadata_obj
metadata_obj = MetaData(naming_convention=convention)

#tables declaration
#database metadata = tables and columns
#metadata = kind of python dict binding table objects (py) to their string name

#main id = prefix
incidents_table = Table(
    "incident_header",
    metadata_obj, #assings itself to the metadata collection
    Column("main_id", String, primary_key=True), #represent a column in a db table, and assings itself to the table object 
)

#snapshot_id = suffix
incidents_info = Table(
    "incident_info",
    metadata_obj,
    Column("snapshot_id", Integer, primary_key=True, autoincrement=True),
    Column("main_id", ForeignKey("incident_header.main_id"), nullable=False),
    Column("icon_category", Integer),
    Column("magnitude_of_delay", Integer), #alembic
    Column("start_time", String(21)),
    Column("end_time", String(21)),
    Column("frm",String(20)),
    Column("too",String(20)),
    Column("length", String(10)),
    Column("delay", String),
    Column("number_of_reports", Integer),
    Column("last_report_time", String(21))
    )

incident_events = Table(
    "incident_event",
    metadata_obj,
    Column("event_id",Integer, primary_key=True, autoincrement=True),
    Column("snapshot_id", ForeignKey("incident_header.main_id"), nullable=False),
    Column("code", Integer),
    Column("description", String(15)),
    Column("icon_category", Integer)
)

#created all tables present in the actual metadata namespace
#if tables exists, it will pass
#it can be used once, if tables are modifed, we have to use alembic
#deleting the db.py means losing all the data!
metadata_obj.create_all(engine)

#dict and set are hash tables

def clean_records():
    with engine.connect() as conn:
        stmt = delete(incidents_table)
        conn.execute(stmt)
        stmt = delete(incidents_info)
        conn.execute(stmt)
        stmt = delete(incident_events)
        conn.execute(stmt)
        conn.commit()

#row is a sinle element tuple!
def get_ids():
    with engine.connect() as conn:
        stmt = select(incidents_table.c.id)
        id_set: set[str] = {0,1}
        for row in conn.execute(stmt):
            id_set.add(row[0])
        return id_set

#from json to sqlite db
def data_transfer(json_string):
    with engine.connect() as conn:
        id_set = get_ids()
        with open(json_string, 'r') as f:
            json_file = json.load(f)
            try:
                for json_report in json_file['incidents']:
                    properties = json_report['properties']
                    report_id = properties['id']
                    stable_event_id = report_id[0:40]
                    snapshot_id = report_id[41:]

                    #ceck if the id already had been inserted, or if the report is the same(same id with same payload)
                    if report_id not in id_set: #O(1)
                        stmt = insert(incidents_table).values(id=report_id) 
                        conn.execute(stmt)
                    else:
                        stmt = select(incidents_info.c.start_time, incidents_info.c.end_time).where(incidents_info.c.id==report_id) # O(n)
                        for row in conn.execute(stmt):
                            previous_start_time = row[0]
                            previous_end_time = row[1]
                            if(properties['startTime']==previous_start_time and properties['endTime']==previous_end_time):
                                continue

                    #to include : update if exist, else insert (upsert) 
                    #same id's can have different information (future updates)
                    stmt = insert(incidents_info).values(incident_id=report_id, icon_category=properties['iconCategory'],
                        start_time = properties['startTime'], end_time = properties['endTime'], frm = properties['from'], too = properties['to'],
                        length = properties['length'], delay = properties['delay'], number_of_reports = properties['numberOfReports'])
                    conn.execute(stmt)

                    for event in properties['events']:
                        stmt = insert(incident_events).values(incident_id=report_id, code=event['code'], description=event['description'], icon_category = 
                            event['iconCategory'])
                        conn.execute(stmt)

                    #further to study transactions to deeply understeand commit
                    conn.commit()

            except Exception as ex:
                print('error trying to insert the following report:')
                #print(f"id:{report_id}\n")
                print(ex.args)

#print data
#row is a tuple bc we can retrieve multiple columns from one record(row), resulting in a tuple
#use conn.scalars for direct values
def data_fetch():
    with engine.connect() as conn:
        stmt = select(incidents_info.c.info_date)
        count = 0
        for row in conn.execute(stmt):
            print(row[0])
            count+=1
        print("number of id's: ", count)

def ret_times():
    with engine.connect() as conn:
        stmt = select(incidents_info.c.incident_id)
        for row in conn.execute(stmt):
            print(row)

def print_events():
    with engine.connect() as conn:
        stmt = select(incident_events)
        for row in conn.execute(stmt):
            print(row)


        
