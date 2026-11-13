import pandas as pd #(pandas is built on top of numpy)
import json
from datetime import datetime
import db
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError

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

def initialize_generic_df():
    with db.engine.connect() as conn:
        stmt = sa.select(db.snapshots_table)
        result = conn.execute(stmt)
        #_asdict(): nametuple -> dict
        data = [row._asdict() for row in result]
        df = pd.DataFrame(data)
        clean_dataFrame(df)
        #safety worning for duplicates
        if df.duplicated(subset=['snapshot_id']).sum()>0:
            print('\n WARNING: a duplicate has been found in snapshots table! \n')
        return df

#incident->duration_main_cause

#name = string or tuple
#group = pd.dataFrame
#after get_grouped the result is a df
#if only group_by group(string/tuple) -> df
#The groups attribute of a GroupBy object is a dictionary that maps each unique group key to the index labels belonging to that group.

def initialize_time_based_dataFrame() -> pd.DataFrame:
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

    main_df = initialize_generic_df()
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
    return grouped_df

def initialize_category_count_dataFrame() -> pd.DataFrame:
    main_df = initialize_generic_df()
    number_of_reports = main_df['main_id'].count()
    category_count_df = pd.DataFrame(main_df['icon_category'].value_counts())
    category_count_df['ratio'] = category_count_df['count']/number_of_reports #cat_count_df is a series, returns a series
    categories = category_count_df.index
    for category in categories:
        group = main_df.groupby('icon_category').get_group(category)['delay']
        print(group)
        #continue to calculate mean
    
    return category_count_df

def weekly_bin(date_value:datetime.date):
    #function that assigns weekly_bin series to df
    day:str = date_value.strftime("%A")
    hour = date_value.hour
    return f"{str(day)}_{str(hour)}"

def groupby_timezone(lat:float, lon:float, offset:float = 0.001) -> pd.DataFrame:
    #offset of 0.001 ~ 100 meters
    min_lon = lon - offset;
    max_lon = lon + offset;
    min_lat = lat - offset;
    max_lat = lat + offset;
    try:
        with db.engine.connect() as conn:
            stmt = sa.select(db.snapshots_table).join(db.snapshot_coordinates).where(
                db.snapshot_coordinates.c.center_latitude >= min_lat,
                db.snapshot_coordinates.c.center_latitude <= max_lat,
                db.snapshot_coordinates.c.center_longitude >= min_lon,
                db.snapshot_coordinates.c.center_longitude <= max_lon
            )
            result = conn.execute(stmt) #result = cursor(iterator) pointing to the next row
            #convert all rows into a dictionary inside a list
            data = [row._asdict() for row in result] #list comprehension
            print(data)
            df = pd.DataFrame(data)
            clean_dataFrame(df)
            #hour(0-23), dow(1-7), combined = 168 combinations
            df['weekly_bin'] = df['start_time'].apply(weekly_bin)
            if df.duplicated(subset=['snapshot_id']).sum()>0:
                print('\n WARNING: a duplicate has been found in snapshots table! \n')
            return df.drop_duplicates()
    except SQLAlchemyError as sql_ex:
        print(f"An error occured during database fetching, {sql_ex.args}")
    except Exception as ex:
        print(f"An error occured while converting data, {ex.args}")

def groupby_weekly_bin(df: pd.DataFrame, w_bin) -> pd.DataFrame:
    #--- conditional probability parameter 
    accidents = df[df['weekly_bin']==w_bin]
    time_window = accidents['start_time'].max() - accidents['start_time'].min()
    time_window = time_window.total_seconds()/604800 #total seconds in a week
    time_slot_count = accidents.count()/time_window
    print(time_slot_count)


    


#def incident_probability_index(place:coordinate):
    
#def initialize_impac_radius_dataFrame() -> pd.dataFrame:



         






