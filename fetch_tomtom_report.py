import requests
import json
import db
import os

#tomtom refresh rate is roughly 1 minute
#some reports will be the same (long lasting) with other suffix

def get_reports():
    #POST request with ID's
    scheme = 'http'
    domain = 'api.tomtom.com'
    path = '/traffic/services/5/incidentDetails'
    key = 'key=ptHPCU6tTJyLLvW6nhVa8aChAyVz5KsL'
    bbox = '&bbox=25.9220,44.3315,26.2425,44.5510'
    fields = '&fields={incidents{type,geometry{type,coordinates},properties{id,iconCategory,magnitudeOfDelay,events{description,code,iconCategory},' \
    'startTime,endTime,from,to,length,delay,roadNumbers,timeValidity,probabilityOfOccurrence,numberOfReports,lastReportTime,tmc{countryCode,tableNumber,' \
    'tableVersion,direction,points{location,offset}}}}}'
    language = '&language=en-GB&t=-1'
    filter = '&timeValidityFilter=present'
    req_url = scheme + '://' + domain + path + '?' + key + bbox + fields + language + filter
    print(req_url)
    response = requests.get(req_url)
    json_response = response.json()
    response.raise_for_status()

    #to resolve duplicates problem with json_name
    import datetime
    data_of_fetch = datetime.datetime.now()
    json_string = 'json_file' + data_of_fetch.strftime('%M%S')
    with open(json_string, 'w') as f:
        json.dump(json_response,f, indent=2)

    #moved here to automatically transfer data after fetch
    db.data_transfer(json_string)

    #automatically removes the json file after data transfer
    #os.remove('json_string')

    #next: solve duplicates
    #delete and update sqlalchemy
