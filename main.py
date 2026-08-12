import requests
import json
import db
import pandas as pd

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

def get_reports():
    #POST request with ID's
    scheme = 'http'
    domain = 'api.tomtom.com'
    path = '/traffic/services/5/incidentDetails'
    key = 'key=ptHPCU6tTJyLLvW6nhVa8aChAyVz5KsL'
    bbox = '&bbox=4.8854592519716675,52.36934334773164,4.897883244144765,52.37496348620152'
    fields = '&fields={incidents{type,geometry{type,coordinates},properties{id,iconCategory,magnitudeOfDelay,events{description,code,iconCategory},' \
    'startTime,endTime,from,to,length,delay,roadNumbers,timeValidity,probabilityOfOccurrence,numberOfReports,lastReportTime,tmc{countryCode,tableNumber,' \
    'tableVersion,direction,points{location,offset}}}}}'
    language = '&language=en-GB&t=1111'
    filter = '&timeValidityFilter=present'
    req_url = scheme + '://' + domain + path + '?' + key + bbox + fields + language + filter
    print(req_url)
    response = requests.get(req_url)
    json_response = response.json()
    response.raise_for_status()
    with open('json_file.json', 'w') as f:
        json.dump(json_response,f, indent=2)

#get_reports()
with open('json_file.json', 'r') as f:
    reports = json.load(f)

#get_reports()
#db.data_transfer()
#db.data_fetch()

#next: pandas

#retrieve properties from json into lists -> into dictionary, for dataFrame init
def initialize_dataFrame():
    with open('json_file.json', 'r') as f:
        try:
            reports = json.load(f)
            reports = reports['incidents']
            id:list[str] = []
            icon_category:list[int] = []
            magnitude_of_delay:list[int] = []
            start_time:list[str] = []
            end_time:list[str] = []
            frm:list[str] = []
            to:list[str] = []
            length:list[float] = []
            delay:list[float] = []
            probability:list[str] = []
            number_of_reports:list[int] = []
            last_report_time:list[str] = []
            events:list[dict] = []
            coordinates:list[list] = []

            for report in reports:
                id.append(report['properties'].get('id'))
                icon_category.append(report['properties'].get('iconCategory'))
                magnitude_of_delay.append(report['properties'].get('magnitudeOfDelay'))
                start_time.append(report['properties'].get('startTime'))
                end_time.append(report['properties'].get('endTime'))
                frm.append(report['properties'].get('from'))
                to.append(report['properties'].get('to'))
                length.append(report['properties'].get('length'))
                delay.append(report['properties'].get('delay'))
                probability.append(report['properties'].get('probabilityOfOccurrence'))
                number_of_reports.append(report['properties'].get('numberOfReports'))
                last_report_time.append(report['properties'].get('lastReportTime'))
                events.append(report['properties'].get('events'))
                coordinates.append(report['geometry'].get('coordinates'))

            df_dictionary = {
                'id': id,
                'icon_category': icon_category,
                'magnitude_of_delay': magnitude_of_delay,
                'start_time': start_time,
                'end_time': end_time,
                'from': frm,
                'to': to,
                'length': length,
                'delay': delay,
                'probability': probability,
                'number_of_reports': number_of_reports,
                'last_report_time': last_report_time,
                'events': events,
                'coordinates': coordinates
            }

        except Exception as ex:
            print('Error trying to parse data into dataFrame: ', ex)
        finally:
            f.close()
    return pd.DataFrame(df_dictionary)

#functions receive references
#it depends on the object being mutable or non-mutable

#dataframe is a mutable objects so it modifies the actual value
#(duplicates are managed by primary key constraint in the db section)
def clean_dataFrame(df:pd.DataFrame):
    df.fillna({'delay':0.0}, inplace=True)
    df.fillna({'number_of_reports':0.0}, inplace=True)
    df.fillna({'last_report_time':'no value'}, inplace=True)

    #convert into pandas datetime (see documentation)
    df['start_time'] = pd.to_datetime(df['start_time'], errors = 'coerce',  format = 'ISO8601')
    df['end_time'] = pd.to_datetime(df['end_time'],errors = 'coerce', format = 'ISO8601')
    #df.dropna(inplace=True) #safety measure, removes no end_date

df = initialize_dataFrame()
clean_dataFrame(df)
#print(df['end_time'])
#print(df['id'].duplicated())
print(df.info())

#recap ds, read pandas package overview

get_reports()
db.data_transfer()
db.data_fetch()






