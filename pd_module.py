import pandas as pd
import json
from datetime import datetime
import db
import sqlalchemy as sa

#retrieve properties from json into lists -> into dictionary, for dataFrame init
def initialize_dataFrame():
    engine = db.engine
    with engine.connect() as conn:
        try:
            ids:list[str] = []
            info_date:list[datetime] = []
            icon_category:list[int] = []
            start_time:list[str] = []
            end_time:list[str] = []
            frm:list[str] = []
            to:list[str] = []
            length:list[float] = []
            delay:list[float] = []
            number_of_reports:list[int] = []

            #complete when migration is done
            stmt = sa.select(db.incidents_table.c.id)
            for row in conn.execute(stmt):
                id = row[0]
                stmt = sa.select(db.incidents_info).where(db.incidents_info.c.incident_id == id)
                for incident_row in conn.execute(stmt):
                    ids.append(id)
                    info_date.append(incident_row[2])
                    icon_category.append(incident_row[3])
                    start_time.append(incident_row[4])
                    end_time.append(incident_row[5])
                    frm.append(incident_row[6])
                    to.append(incident_row[7])
                    length.append(incident_row[8])
                    delay.append(incident_row[9])
                    number_of_reports.append(incident_row[10])

            df_dictionary = {
                'id': ids,
                'info_dates': info_date,
                'icon_category': icon_category,
                'start_time': start_time,
                'end_time': end_time,
                'from': frm,
                'to': to,
                'length': length,
                'delay': delay,
                'number_of_reports': number_of_reports,
            }

            return pd.DataFrame(df_dictionary)
        except Exception as ex:
            print('Error trying to parse data into dataFrame: ', ex)
        finally:
            conn.close()

def clean_dataFrame(df:pd.DataFrame):
    df.fillna({'delay':0.0}, inplace=True)
    df.fillna({'number_of_reports':0.0}, inplace=True)
    df.fillna({'last_report_time':'no value'}, inplace=True)

    #convert into pandas datetime (see documentation)
    #coerce if datatype is not what expected -> NaT
    df['start_time'] = pd.to_datetime(df['start_time'], errors = 'coerce',  format = 'ISO8601')
    df['end_time'] = pd.to_datetime(df['end_time'],errors = 'coerce', format = 'ISO8601')

    df.fillna({'end_time':'None'}, inplace=True)
    #df.dropna(inplace=True) #safety measure, removes no end_date
