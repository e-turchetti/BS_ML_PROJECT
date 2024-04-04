from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import iot_api_client as iot
from iot_api_client.rest import ApiException
from iot_api_client.configuration import Configuration
import datetime
from dateutil.tz import tzutc

def get_properties_id(devices_api, variable_name):

    try:
        resp = devices_api.devices_v2_list()
        device_id= resp[0].id
        thing_id= resp[0].thing.id
        properties=resp[0].thing.properties
        variable_id=[property.id for property in properties if property.variable_name==variable_name][0]
        
    	
    except ApiException as e:
        print("Got an exception: {}".format(e))
        
    return thing_id,variable_id
        

def set_property(properties_api, thing_id,variable_id,value):

    propertyValue={'value': value }

    try:
        resp = properties_api.properties_v2_publish(thing_id,variable_id,propertyValue)
    except ApiException as e:
        print("Got an exception: {}".format(e))
        
    return(resp)
'''
oauth_client = BackendApplicationClient(client_id='pFcckSqU1WFGlm80UjDWSQfpNp1c6X1G')
token_url = "https://api2.arduino.cc/iot/v1/clients/token"

oauth = OAuth2Session(client=oauth_client)
token = oauth.fetch_token(
     token_url=token_url,
     client_id='pFcckSqU1WFGlm80UjDWSQfpNp1c6X1G',
     client_secret='ndYh4cjpPB260TBd6ffC2vrox2PDDY2CNnCih6j94JSNTfIi3h5n0LDDFZNWKh9X',
     include_client_id=True,
     audience="https://api2.arduino.cc/iot",
 )

access_token = token.get("access_token")

print(access_token)

 # configure and instance the API client
client_config = Configuration(host="https://api2.arduino.cc/iot")
client_config.access_token = access_token
client = iot.ApiClient(client_config)

# # as an example, interact with the devices API
devices_api = iot.DevicesV2Api(client)
properties_api=iot.PropertiesV2Api(client)
thing_id,temp_desired_id= get_properties_id(devices_api,"button")
print('thing_id: '+thing_id)
print('temp_desired_id: '+temp_desired_id)


set_property(properties_api,thing_id,temp_desired_id,True)

# print()
'''
