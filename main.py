import requests
import json
import db
import fetch_tomtom_report as tomtom
import pd_module as pd_mod

#tom tom gives json, any language can parse it (java, python etc!)

class incident:
    def __init__(self, type:str, properties:dict, events:dict, tmc: dict, geometry:dict):
       self.type: str = type
       self.id: str = properties.get('id')
       self.icon_category: int = properties.get('iconCategory')
       self.magnitude_of_delay: int = properties.get('magnitudeOfDelay')
       self.start_time: int = properties.get('startTime')
       self.end_time: int = properties.get('endTime')
       self.frm: str = properties.get('from')
       self.to: str = properties.get('to')
       self.length: str = properties.get('length')
       self.delay: str = properties.get('delay')
       self.road_numbers: str = properties.get('roadNumbers')
       self.time_validity: str = properties.get('timeValidity')
       self.probability_of_occurance:str = properties.get('probabilityOfOccurance')
       self.number_of_reports: int = properties.get('numberOfReports')
       self.last_report_time: int = properties.get('lastReportTime')
       self.events: list = events
       self.tmc: dict = tmc
       self.geometry: dict = geometry

    def display_report(self):
        print (f"type:{self.type}, id: {self.id}")
        print('incident type:')
        match self.icon_category:
            case 0:
                print('Unknown')
            case 1:
                print('Accident')
            case 2:
                print('Fog')
            case 3:
                print('Dangerous Conditions')
            case 4:
                print('Rain')
            case 5:
                print('Ice')
            case 6:
                print('Jam')
            case 7:
                print('Lane Closed')
            case 8:
                print('Road Closed')
            case 9:
                print('Road Works')
            case 10:
                print('Wind')
            case 11:
                print('Flooding')
            case 14:
                print('Broken Down Vehicle')
        print('magnitude:')
        match self.magnitude_of_delay:
            case 0:
                print('Unknown')
            case 1:
                print('Minor')
            case 2:
                print('Moderate')
            case 3:
                print('Major')
            case 4:
                print('Undefinied')

        print(f"from: {self.frm}, to: {self.to},length: {self.length}, delay: {self.delay}, road numbers: {self.road_numbers}")
        print(f"time validity: {self.time_validity}, probability of occurance: {self.probability_of_occurance}, number of reports: {self.number_of_reports}")
        print(f"last report time: {self.last_report_time}\n")


#json->db->pd

#tomtom.get_reports()
#db.data_fetch()

#recap ds, read pandas package overview
#pandas to retain only math?

#df = pd_mod.initialize_dataFrame()
#pd_mod.clean_dataFrame(df)
#print(df['end_time'])
#print(df['id'].duplicated())
#print(df)

#db.print_events()
#print(db.metadata_obj.tables.keys())

#db.ceck_duplicates()


