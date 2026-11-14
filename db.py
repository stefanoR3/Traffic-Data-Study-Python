from sqlalchemy import create_engine, text, Table, Column, Integer, Float, String, MetaData, ForeignKey, insert, select, DateTime, delete
from typing import List, Optional
import json
import datetime
import sys

#engine for connection and exectuion, metadata for tables namespace
#it does create a new sqlite database in the current directory
engine = create_engine("sqlite+pysqlite:///data.db") #echo = True
metadata_obj = MetaData()

#tables declaration
#database metadata = tables and columns
#metadata = kind of python dict binding table objects (py) to their string name
#unique used as safety net

#main id = prefix
incidents_table = Table(
    "incident_header",
    metadata_obj, #assings itself to the metadata collection
    Column("main_id", String, primary_key=True, nullable=False) #represent a column in a db table, and assings itself to the table object 
)

#snapshot_id = suffix
snapshots_table = Table(
    "incident_snapshot",
    metadata_obj,
    Column("snapshot_id", String, primary_key=True, nullable=False),
    Column("main_id", ForeignKey("incident_header.main_id"), nullable=False),
    Column("icon_category", Integer),
    Column("magnitude_of_delay", Integer), #alembic
    Column("start_time", String(20)),
    Column("end_time", String(20)),
    Column("frm",String(100)),
    Column("too",String(100)),
    Column("length", Float),
    Column("delay", Integer),
    Column("number_of_reports", Integer),
    Column("last_report_time", String(20))
    )

snapshot_events = Table(
    "incident_event",
    metadata_obj,
    Column("event_id",Integer, primary_key=True, autoincrement=True),
    Column("snapshot_id", ForeignKey("incident_snapshot.snapshot_id"), nullable=False),
    Column("code", Integer),
    Column("description", String(100))
)

#to manage multiple coordinates
snapshot_coordinates = Table(
    "incident_coordinates",
    metadata_obj,
    Column("snapshot_id", ForeignKey("incident_snapshot.snapshot_id"), primary_key=True,
         nullable=False),
    Column("north", Float),
    Column("south", Float),
    Column("east", Float),
    Column("west", Float),
    Column("center_latitude", Float),
    Column("center_longitude", Float)
)

#created all tables present in the actual metadata namespace
#if tables exists, it will pass
#it can be used once, if tables are modifed, we have to use alembic
#deleting the data.db means losing all the data!
#dict and set are hash tables
metadata_obj.create_all(engine)

#row is a sinle element tuple!
def get_main_ids() -> set:
    with engine.connect() as conn:
        stmt = select(incidents_table.c.main_id)
        #manage how to avoid void but still work
        id_set: set[str] = set()
        for row in conn.execute(stmt):
            #we check only the main id
            id_set.add(row[0])
        return id_set

def get_snap_ids() -> set:
    with engine.connect() as conn:
        stmt = select(snapshots_table.c.snapshot_id)
        id_set: set[str] = set()
        for row in conn.execute(stmt):
            id_set.add(row[0])
        return id_set

#if try except raise an error not managed, the except goes to the outher except trying to find another except
#row is a tuple bc we can retrieve multiple columns from one record(row), resulting in a tuple
#use conn.scalars for direct values


#from json to sqlite db
def data_transfer(json_string) -> None:
    with engine.connect() as conn:
        with open(json_string, 'r') as f:
            json_file = json.load(f)
            main_ids = get_main_ids()
            snap_ids = get_snap_ids()
            try:
                for json_report in json_file['incidents']:
                    properties = json_report['properties']
                    report_id = properties['id']
                    coordinates = json_report['geometry']['coordinates']
                    lon, lat = 0,0 #lon,lat = 0 would raise an error!
                    try:
                        if isinstance(coordinates[0], list):
                            lon = coordinates[0][0]
                            lat = coordinates[0][1]
                        else:
                            lon = coordinates[0]
                            lat = coordinates[1]
                    except Exception as ex:
                        print(f'error at id: {properties['id']}')
                        print(ex.args)
                        return
                    
                    snap_id = str(lon) + '-' + str(lat) + '-' + str(properties['startTime'])
                    m_id = str(report_id[41:])

                    #ceck if the id already had been inserted, or if the report is the same(same id with same payload)
                    try:
                        if m_id not in main_ids: #O(1)
                            stmt = insert(incidents_table).values(main_id=m_id) 
                            conn.execute(stmt)
                            main_ids.add(m_id) #! would have cecked only with the old values
                    except Exception as ex:
                        print(f"error at main id: {ex.args}")
                        return

                    #fromisoformat to convert from ISO 8601 (international) to py datetime

                    try:
                        if (snap_id) not in snap_ids:   #O(1)
                            stmt = insert(snapshots_table).values(snapshot_id=snap_id, main_id=m_id, icon_category=properties['iconCategory'],
                                start_time=properties['startTime'], end_time=properties['endTime'], frm=properties['from'], too=properties['to'],
                                length=properties['length'], delay=properties['delay'], number_of_reports=properties['numberOfReports'],
                                last_report_time=properties['lastReportTime']).prefix_with('OR IGNORE') #to pass duplicates
                            conn.execute(stmt)
                    except Exception as ex:
                        print(f"error at snap id: {ex.args}")
                        return

                    try:
                        for event in properties['events']:
                            stmt = insert(snapshot_events).values(snapshot_id=str(snap_id), code=event['code'],
                                description=event['description']).prefix_with('OR IGNORE')
                            conn.execute(stmt)
                    except Exception as ex:
                        print(f"error at events: {ex.args}")
                        return

                    try:
                        latitudes: list[float] = []
                        longitudes: list[float] = []
                        if isinstance(coordinates[0], list):
                            for coords in coordinates:
                                latitudes.append(coords[0])
                                longitudes.append(coords[1])
                        else:
                            latitudes.append(coordinates[0])
                            longitudes.append(coordinates[1])
                        n = max(latitudes)
                        s = min(latitudes)
                        e = max(longitudes)
                        w = max(longitudes)
                        #formula works even for one point geometry
                        center_lat = (n+s)/2
                        center_lon = (e+w)/2
                        stmt = insert(snapshot_coordinates).values(snapshot_id=snap_id, north=n, south=s, east=e, west=w,
                        center_latitude=center_lat,center_longitude=center_lon).prefix_with('OR IGNORE') #for duplicates
                        conn.execute(stmt)
                    except Exception as ex:
                        print(f"error at coordinates: {ex.args}")
                        return
                            
                #further to study transactions to deeply understeand commit
                #only one commit ensures that no data gets introduced if an error occure
                conn.commit()

            except Exception as ex:
                print("error trying to insert report")
                print(ex.args)
                return

def number_of_records():
    with engine.connect() as conn:
        stmt = select(incidents_table)
        result = conn.execute(stmt)
        data = len([row for row in result])
        print(data)
        


    
        

        
