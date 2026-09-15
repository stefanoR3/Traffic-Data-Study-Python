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
    Column("main_id", String, primary_key=True, unique = True), #represent a column in a db table, and assings itself to the table object 
)

#snapshot_id = suffix
incidents_info = Table(
    "incident_info",
    metadata_obj,
    Column("snapshot_id", String, primary_key=True, unique = True),
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

def clean_records() -> None:
    with engine.connect() as conn:
        stmt = delete(incidents_table)
        conn.execute(stmt)
        stmt = delete(incidents_info)
        conn.execute(stmt)
        stmt = delete(incident_events)
        conn.execute(stmt)
        conn.commit()

#row is a sinle element tuple!
def get_main_ids() -> set:
    with engine.connect() as conn:
        stmt = select(incidents_table.c.main_id)
        #manage how to avoid void but still work
        id_set: set[str] = {0,1}
        for row in conn.execute(stmt):
            #we check only the main id
            id_set.add(row[0])
        return id_set

def get_snap_ids(main_id:str) -> set:
    with engine.connect() as conn:
        stmt = select(incidents_info.c.snapshot_id).where(incidents_info.c.main_id==main_id)
        id_set: set[str] = {0,1}
        for row in conn.execute(stmt):
            id_set.add(row[0])
        return id_set

#from json to sqlite db
def data_transfer(json_string) -> None:
    with engine.connect() as conn:
        main_ids = get_main_ids()
        with open(json_string, 'r') as f:
            #improvement at json file opening
            json_file = json.load(f)
            try:
                for json_report in json_file['incidents']:
                    properties = json_report['properties']
                    report_id = properties['id']
                    m_id = report_id[0:40]
                    snap_id = report_id[41:]

                    #ceck if the id already had been inserted, or if the report is the same(same id with same payload)
                    if m_id not in main_ids: #O(1)
                        stmt = insert(incidents_table).values(main_id=m_id) 
                        conn.execute(stmt)
                        main_ids.add(m_id) #! would have cecked only with the old values
                    if snap_id not in get_snap_ids(m_id):  
                        stmt = insert(incidents_info).values(main_id=m_id, snapshot_id=snap_id, icon_category=properties['iconCategory'],
                            start_time = properties['startTime'], end_time = properties['endTime'], frm = properties['from'], too = properties['to'],
                            length = properties['length'], delay = properties['delay'], number_of_reports = properties['numberOfReports'], last_report_time=properties['lastReportTime'])
                        conn.execute(stmt)

                    for event in properties['events']:
                        stmt = insert(incident_events).values(snapshot_id=snap_id, code=event['code'], description=event['description'], icon_category = event['iconCategory'])
                        conn.execute(stmt)

                    #further to study transactions to deeply understeand commit
                    conn.commit()

            except Exception as ex:
                print('error trying to insert report')
                print(ex.args)

#print data
#row is a tuple bc we can retrieve multiple columns from one record(row), resulting in a tuple
#use conn.scalars for direct values
def data_fetch() -> None:
    with engine.connect() as conn:
        stmt = select(incidents_info.c.info_date)
        count = 0
        for row in conn.execute(stmt):
            print(row[0])
            count+=1
        print("number of id's: ", count)

def ret_times() -> None:
    with engine.connect() as conn:
        stmt = select(incidents_info.c.incident_id)
        for row in conn.execute(stmt):
            print(row)

def print_events() -> None:
    with engine.connect() as conn:
        stmt = select(incident_events)
        for row in conn.execute(stmt):
            print(row)


    
        

        
