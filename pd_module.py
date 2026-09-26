import pandas as pd #(pandas is built on top of numpy)
import json
from datetime import datetime
import db
import sqlalchemy as sa

def clean_dataFrame(df:pd.DataFrame) -> None:
    df.fillna({'delay':0.0}, inplace=True)
    df.fillna({'number_of_reports':0.0}, inplace=True)
    df.fillna({'last_report_time':'no value'}, inplace=True)

    #convert into pandas datetime (see documentation)
    #format tells pd to not search for the format, we give it
    #coerce if datatype is not what expected -> NaT
    #NaN is the standard marker used in pandas (Non a Number)
    df['start_time'] = pd.to_datetime(df['start_time'], errors = 'coerce',  format = 'ISO8601')
    df['end_time'] = pd.to_datetime(df['end_time'],errors = 'coerce', format = 'ISO8601')
    df['last_report_time'] = pd.to_datetime(df['last_report_time'], errors = 'coerce', format='ISO8601')

    df.fillna({'end_time':'None'}, inplace=True)
    #df.dropna(inplace=True) #safety measure, removes no end_date

#retrieve properties from json into lists -> into dictionary, for dataFrame init
def initialize_generic_dataFrame() -> pd.DataFrame:
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

#incident->duration_main_cause

#name = string or tuple
#group = pd.dataFrame

#after get_grouped the result is a df
#if only group_by group(string/tuple) -> df

#The groups attribute of a GroupBy object is a dictionary that maps each unique group key to the index labels belonging to that group.

def initialize_time_based_dataFrame(category:int = 0) -> pd.DataFrame:
    main_ids:set = db.get_main_ids()

    #name and group loop simultaniously!
    #groupby group the orinigal df into multiple df
    #agg() squashes the rows to perform math/statistics operation/s
    #in this, it looks in the entire start/end times, takes the min/max and saves it into a new column

    #groupby acts initially as a dict, binding names and groupes
    #agg takes every group, performs the actions and glue the results into a single dataframe
    #a agrega = a uni/ a contopi
    #this process is called split-apply-combine!

    #only the reports with a defined end time

    main_df = initialize_generic_dataFrame()
    #clean_dataFrame(main_df)
    grouped_df = main_df.groupby('main_id').agg(
        start_time=('start_time', 'min'),
        end_time=('end_time', 'max'),
        total_snapshots=('snapshot_id', 'count'),
        max_delay=('delay', 'max')
    )
    #if we used clean df, dropna would not have worked couse it would have converted NaN to string/ value
    grouped_df['start_time'] = pd.to_datetime(grouped_df['start_time'], errors = 'coerce',  format = 'ISO8601')
    grouped_df['end_time'] = pd.to_datetime(grouped_df['end_time'],errors = 'coerce', format = 'ISO8601')
    grouped_df.dropna(how='any', inplace=True)

    grouped_df['duration'] = grouped_df['end_time'] - grouped_df['start_time']
    print(grouped_df.to_string())
        
    #for group in grouped_df:
        #print(name)
        #print(group)
         






