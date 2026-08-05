from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, ForeignKey, insert, select
from typing import List, Optional
import json

#engine for connection and exectuion, metadata for tables namespace
#it does create a new sqlite database in the current directory
engine = create_engine("sqlite+pysqlite:///data.db") #echo = True
metadata_obj = MetaData()

#tables declaration

incidents_table = Table(
    "incident_header",
    metadata_obj, #assings itself to the metadata collection
    Column("id", String, primary_key=True), #represent a column in a db table, and ssings itself to the table object 
    Column("type", String(30)),# the column contains: a string name and a type object
)
        
incidents_info = Table(
    "incident_info",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("incident_id", Integer, ForeignKey("incident_header.id"), nullable=False),
    Column("icon_category", Integer),
    Column("start_time", String(21)),
    Column("end_time", String(21)),
    Column("frm",String(20)),
    Column("too",String(20)),
    Column("length", String(10)),
    Column("delay", String),
    Column("number_of_reports", Integer),   
    )


#created all tables present in the actual metadata namespace
#if tables exists, it will pass
metadata_obj.create_all(engine)

def data_transfer():
    with engine.connect() as conn:
        with open('json_file.json', 'r') as f:
            reports = json.load(f)
            try:
                for json_report in reports['incidents']:
                    properties = json_report['properties']
                    stmt_table = insert(incidents_table).values(id=properties['id'], type=json_report['type'])
                    conn.execute(stmt_table)
                    stmt_info = insert(incidents_info).values(incident_id=properties['id'], icon_category=properties['iconCategory'],
                        start_time = properties['startTime'], end_time = properties['endTime'], frm = properties['from'], too = properties['to'],
                            length = properties['length'], delay = properties['delay'], number_of_reports = properties['numberOfReports'])
                    conn.execute(stmt_info)
                    conn.commit()
            except Exception as ex:
                print(ex.args)

def data_fetch():
    with engine.connect() as conn:
        stmt = select(incidents_table).where(incidents_table.c.type == "Feature")
        for row in conn.execute(stmt):
            print(row)