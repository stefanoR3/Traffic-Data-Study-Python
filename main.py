import requests
import json

request_url = 'https://api.tomtom.com/traffic/services/5/incidentDetails?key=ptHPCU6tTJyLLvW6nhVa8aChAyVz5KsL&bbox=4.8854592519716675,52.36934334773164,4.897883244144765,52.37496348620152&fields={incidents{type,geometry{type,coordinates},properties{iconCategory}}}&language=en-GB&t=1111&timeValidityFilter=present'
response = requests.get(request_url)
json_response = response.json()
response.raise_for_status()

with open('json_file.json', 'w') as file:
    json.dump(json_response, file, indent = 2)
     