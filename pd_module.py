import pandas as pd
import json
from datetime import datetime
import db
import sqlalchemy as sa

def clean_dataFrame(df:pd.DataFrame) -> None:
    df.fillna({'delay':0.0}, inplace=True)
    df.fillna({'number_of_reports':0.0}, inplace=True)
    df.fillna({'last_report_time':'no value'}, inplace=True)

    #convert into pandas datetime (see documentation)
    #coerce if datatype is not what expected -> NaT
    df['start_time'] = pd.to_datetime(df['start_time'], errors = 'coerce',  format = 'ISO8601')
    df['end_time'] = pd.to_datetime(df['end_time'],errors = 'coerce', format = 'ISO8601')
    df['last_report_time'] = pd.to_datetime(df['last_report_time'], errors = 'coerce', format='ISO8601')

    df.fillna({'end_time':'None'}, inplace=True)
    #df.dropna(inplace=True) #safety measure, removes no end_date

#retrieve properties from json into lists -> into dictionary, for dataFrame init
def initialize_dataFrame() -> pd.DataFrame:
    engine = db.engine
    with engine.connect() as conn:
        try:
            main_id:list[str] = []
            snapshot_id:list[str] = []
            icon_category:list[int] = []
            magnitude_of_delay:list[str] = []
            start_time:list[str] = []
            end_time:list[str] = []
            frm:list[str] = []
            to:list[str] = []
            length:list[float] = []
            delay:list[float] = []
            number_of_reports:list[int] = []
            last_report_time:list[str] = []

            stmt = sa.select(db.incidents_info)
            for incident_row in conn.execute(stmt):
                snapshot_id.append(incident_row[0])
                main_id.append(incident_row[1])
                icon_category.append(incident_row[2])
                magnitude_of_delay.append(incident_row[3])
                start_time.append(incident_row[4])
                end_time.append(incident_row[5])
                frm.append(incident_row[6])
                to.append(incident_row[7])
                length.append(incident_row[8])
                delay.append(incident_row[9])
                number_of_reports.append(incident_row[10])
                last_report_time.append(incident_row[11])

            df_dictionary = {
                'main_id': main_id,
                'snapshot_id': snapshot_id,
                'icon_category': icon_category,
                'magnitude_of_delay': magnitude_of_delay,
                'start_time': start_time,
                'end_time': end_time,
                'from': frm,
                'to': to,
                'length': length,
                'delay': delay,
                'number_of_reports': number_of_reports,
                'last_report_time': last_report_time
            }

            return pd.DataFrame(df_dictionary)
        except Exception as ex:
            print('Error trying to parse data into dataFrame: ', ex)
        finally:
            conn.close()

