#!/usr/bin/env python3 

###############################################################
#### PA Config Cleanup Script (Cleans up SC, RN and resets GP 
#### before decommisioning the tenant
#### Author: Darshna Subashchandran
################################################################


import panapi
#from panapi.config import identity,management,security,network
from time import sleep
import logging
import json
import yaml
import PushConfig
import argparse
import prisma_sase

####################################################
#### Login to the tenant with the client secret
###################################################
def sdk_login_to_controller(filepath):
    with open(filepath) as f:
        client_secret_dict = yaml.safe_load(f)
        client_id = client_secret_dict["client_id"]
        client_secret = client_secret_dict["client_secret"]
        tsg_id_str = client_secret_dict["scope"]
        global tsgid
        tsgid = tsg_id_str.split(":")[1]
        #print(client_id, client_secret, tsgid)
    
    global sdk 
    sdk = prisma_sase.API(controller="https://sase.paloaltonetworks.com/", ssl_verify=False)
    sdk.set_debug(3) 
    sdk.interactive.login_secret(client_id, client_secret, tsgid)
    
    return sdk


####################################################
#### Wrapper to push the config to backend
###################################################
def push_config_to_controller():
    PushConfig.push_candidate_config(["Remote Networks"], "Pushing all config", sdk)
    PushConfig.push_candidate_config(["Service Connections"], "Pushing all config",sdk)
    PushConfig.push_candidate_config(["Mobile Users"], "Pushing all config",sdk)
    sleep(30)

#####################################################
#####  Cleanup routine for Service Connections #####
####################################################
def service_connection_cleanup():
    
    #List and iterate through all the SC
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/service-connections?folder=Service Connections"
    resp = sdk.rest_call(url=url, method="GET")
    #sdk.set_debug(3)
    #print(resp)
    response_payload = resp.json()
    data_list = response_payload["data"]
 
    #Cleanup all the Service Connections
    for data in data_list:
        id = data["id"]
        url = "https://api.sase.paloaltonetworks.com/sse/config/v1/service-connections/"+id+"?folder=Service Connections"
        resp = sdk.rest_call(url=url, method="DELETE")
        #sdk.set_debug(3)
        #print(resp)
    
    #List and iterate through the IPSec tunnels
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/ipsec-tunnels?folder=Service Connections"
    resp = sdk.rest_call(url=url, method="GET")
    #sdk.set_debug(3)
    response_payload = resp.json()
    data_list = response_payload["data"]

    #Cleanup all the IPSec Tunnels
    for data in data_list:
        id = data["id"]
        url = "https://api.sase.paloaltonetworks.com/sse/config/v1/ipsec-tunnels/"+id+"?folder=Service Connections"
        resp = sdk.rest_call(url=url, method="DELETE")
        #sdk.set_debug(3)
  
    #List and iterate IKE GW list
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/ike-gateways?folder=Service Connections"
    resp = sdk.rest_call(url=url, method="GET")
    #sdk.set_debug(3)
    response_payload = resp.json()
    data_list = response_payload["data"]

    #Cleanup all the IKE GWs
    for data in data_list:
        id = data["id"]
        url = "https://api.sase.paloaltonetworks.com/sse/config/v1/ike-gateways/"+id+"?folder=Service Connections"
        resp = sdk.rest_call(url=url, method="DELETE")
        #sdk.set_debug(3)


#####################################################
#####  Cleanup routine for Remote Networks #########
####################################################
def remote_network_cleanup():
    
    #List and iterate through all the RN
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/remote-networks?folder=Remote Networks"
    resp = sdk.rest_call(url=url, method="GET")
    #sdk.set_debug(3)
    response_payload = resp.json()
    data_list = []
    data_list = response_payload["data"]
    print(data_list)     

    #Cleanup all the Remote Networks
    for data in data_list:
        id = data["id"]
        url = "https://api.sase.paloaltonetworks.com/sse/config/v1/remote-networks/"+id+"?folder=Remote Networks"
        resp = sdk.rest_call(url=url, method="DELETE")
        #sdk.set_debug(3)

    #List and iterate through the IPSec tunnels
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/ipsec-tunnels?folder=Remote Networks"
    resp = sdk.rest_call(url=url, method="GET")
    #sdk.set_debug(3)
    response_payload = resp.json()
    data_list = response_payload["data"]

    #Cleanup all the IPSec Tunnels
    for data in data_list:
        id = data["id"]
        url = "https://api.sase.paloaltonetworks.com/sse/config/v1/ipsec-tunnels/"+id+"?folder=Remote Networks"
        resp = sdk.rest_call(url=url, method="DELETE")
        #sdk.set_debug(3)
    
    #List and iterate IKE GW list
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/ike-gateways?folder=Remote Networks"
    resp = sdk.rest_call(url=url, method="GET")
    #sdk.set_debug(3)
    response_payload = resp.json()
    data_list = response_payload["data"]

    #Cleanup all the IKE GWs
    for data in data_list:
        id = data["id"]
        url = "https://api.sase.paloaltonetworks.com/sse/config/v1/ike-gateways/"+id+"?folder=Remote Networks"
        resp = sdk.rest_call(url=url, method="DELETE")
        #sdk.set_debug(3)

#####################################################
#####  Reset GP Infra settings             ##########
#####################################################
def reset_gp_infra_settings():
    
    #Fetch all the GP infra settings
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/mobile-agent/infrastructure-settings?folder=Mobile Users"
    resp = sdk.rest_call(url=url, method="GET")
    #sdk.set_debug(3)
    response_payload = resp.json()
    data_list = []
    try: 
        data_list = response_payload["data"]
    except:
        pass

    #Delete the GP infra listed
    for data in data_list:
        url = "https://api.sase.paloaltonetworks.com/sse/config/v1/mobile-agent/infrastructure-settings?"+data["name"]+"?folder=Mobile Users"
        resp = sdk.rest_call(url=url, method="DELETE")
        #sdk.set_debug(3)
    

if __name__ == "__main__":
    
    #Parsing the arguments to the script
    parser = argparse.ArgumentParser(description='Onboarding the LocalUsers, Service Connection and Security Rules.')
    parser.add_argument('-t1', '--T1Secret', help='Input secret file in .yml format for the tenant(T1) from which the security rules have to be replicated.')  

    args = parser.parse_args()
    T1_secret_filepath = args.T1Secret

    sdk = sdk_login_to_controller(T1_secret_filepath)   
 
    #Service Connection cleanup
    service_connection_cleanup()

    #Remote Network cleanup
    remote_network_cleanup()
    
    #Reset the GP infrastructure settings
    reset_gp_infra_settings()
       
    #Push config to backend
    push_config_to_controller()
        
