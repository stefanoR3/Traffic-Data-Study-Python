from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, ForeignKey, insert, select, DateTime
from typing import List, Optional
import json
import datetime

#engine for connection and exectuion, metadata for tables namespace
#it does create a new sqlite database in the current directory
engine = create_engine("sqlite+pysqlite:///data.db") #echo = True
metadata_obj = MetaData()

#tables declaration


incidents_table = Table(
    "incident_header",
    metadata_obj, #assings itself to the metadata collection
    Column("id", String, primary_key=True), #represent a column in a db table, and ssings itself to the table object 
)
        
incidents_info = Table(
    "incident_info",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("incident_id", ForeignKey("incident_header.id"), nullable=False),
    Column("info_date", DateTime, default = datetime.datetime.now()),
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
#it can be used once, if tables are modifed, we have to use alembic
#deleting the db.py means losing all the data!
metadata_obj.create_all(engine)

#dict and set are hash tables

#row is a sinle element tuple!
def get_ids():
    with engine.connect() as conn:
        stmt = select(incidents_table.c.id)
        id_set: set[str] = {0,1}
        for row in conn.execute(stmt):
            id_set.add(row[0])
        print (id_set)

#from json to sqlite db
def data_transfer():
    with engine.connect() as conn:
        id_set = get_ids()
        with open('json_file.json', 'r') as f:
            reports = json.load(f)
            try:
                for json_report in reports['incidents']:
                    report_id = properties['id']

                    #ceck if the id already had been inserted 
                    if(report_id not in id_set):
                        stmt_table = insert(incidents_table).values(id=report_id)
                        conn.execute(stmt_table)

                    #same id's can have different information (future updates)
                    properties = json_report['properties']
                    stmt_info = insert(incidents_info).values(incident_id=report_id, icon_category=properties['iconCategory'],
                        start_time = properties['startTime'], end_time = properties['endTime'], frm = properties['from'], too = properties['to'],
                        length = properties['length'], delay = properties['delay'], number_of_reports = properties['numberOfReports'])
                    conn.execute(stmt_info)
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

#data_transfer()
#ret_times()

#data_fetch()

#next: alembic 

        
