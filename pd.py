import pandas as pd

#serieses are like a column in a table
#they represent arrays and can hold data of any type
#(they represent namespace, only difference is not suing hasp map, the valuse being alingned)

#if nothing else specified, values are labeled with their index number
#this label can be used to accces elements of the series
a = [2,3,4,'brou']
my_series = pd.Series(a)
#print(my_series[0])

#we can specify our own indexes
my_series_indexed = pd.Series(a, index = ['x','y','z','h'])
#print(my_series_indexed)
#print(my_series_indexed['z'])

#dictionary series
#the keys of the dictionary become labels 
cars = {'bmw':'shit', 'audi':'more shit', 'vw': 80}
my_dict_series = pd.Series(cars)
#print(my_dict_series)

#you can exclude items
new_dict_series = pd.Series(cars, index = ['bmw', 'audi'])
#print(new_dict_series)

#DataFrames
#Serieses represent the column, whiel dataFrames represent the whole 2D table
#(in memory, they bind columns to the actual series)

#create a table from two series:
data = {
    'names': ['Marcel', 'Mircea', 'Aurel'],
    'cars': ['Opel', 'Mercedesi', 'Scania']
}

#load data into a new dataframe object
new_table = pd.DataFrame(data, index = ['bulachi1', 'bulachi2', 'bulachi3'])
#print(new_table,'\n')

#return a single column by index ( first [] what index, second [] indexes)
#the result is a new dataframe
#print(new_table.loc[['bulachi1','bulachi2']], '\n')

#csv usage
#to print the entire data frame, use.to_string()
#df = dataframe

df = pd.read_csv('data.csv')
#print(df.to_string())

#head return the headers + number of rows
#print(df.head(),'\n')

#tail same
#print(df.tail())

print(df.info())










