import requests
import json
import db
import fetch_tomtom_report as tomtom
import pd_module as pd_mod

class coordinate:
    def __init__(self, n,s,e,w):
        self.north = n
        self.south = s
        self.east = e
        self.west = w
#json->db->pd

#tomtom.get_reports()

#recap ds, read pandas package overview
#pandas to retain only math?

#db.data_transfer('json_file2404')
df = pd_mod.initialize_generic_dataFrame()
pd_mod.clean_dataFrame(df)
#print(df['end_time'])
#print(df['id'].duplicated())
pd_mod.groupby_coordinates(df,26.25403914745,44.4531995306)
#print(df.head().to_string())

#db.print_events()
#print(db.metadata_obj.tables.keys())

#df = pd_mod.initialize_time_based_dataFrame()
#print(df)

#pd_mod.initialize_time_based_dataFrame()

#problem: we have only one valid id!!!!
#seet = db.get_main_ids()
#print(seet)

#print(db.get_main_ids())
#print(len(db.get_snap_ids()))

#cat_df = pd_mod.initialize_category_count_dataFrame()