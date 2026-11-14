import requests
import json
import db
import fetch_tomtom_report as tomtom
import pd_module as pd_mod
#json->db->pd

tomtom.get_reports()

#recap ds, read pandas package overview
#pandas to retain only math?

#---GENERIC DF DEBUG---
#df = pd_mod.initialize_generic_df()
#print(df.duplicated(subset=['snapshot_id']).sum())

#print(df[['start_time','snapshot_id','frm']].head(50))

#---GROUP BY TIMEZONE DEBUG---
df = pd_mod.groupby_timezone(26.0175038516,44.4120262833)
#print(df.head().to_string())
pd_mod.groupby_weekly_bin(df, 'Thu_8') #same ser as group above
db.number_of_records()
