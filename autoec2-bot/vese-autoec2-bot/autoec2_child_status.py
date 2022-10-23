import requests
import time
import os
from boto3 import client as boto3_client

# This function is called from the parent function
AWS_REGION = os.environ['AWS_PRIMARY_REGION']

def lambda_handler(event, context):
    print(event)
    base_url = "https://discord.com/api/v9/webhooks"

    headers = {
        "Content-Type": "application/json"
    }
    
    # Check if the public address is allocated to the started instance. Repeat 10 times.
    for i in range(10):
        ec2 = boto3_client('ec2', region_name=AWS_REGION)
        try:
            response = ec2.describe_instances(
                Filters=[
                    {
                        'Name': 'tag:Name', 'Values':['autoec2-server'],
                    },
                ],
            )          
            ip_addr = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
            print("Pub Address found: " + ip_addr)
            break

        except KeyError as e:
            print("Waiting instance to become active. Trying to get pub ip again in 2 seconds...")
            time.sleep(2)

    # Send payload back to discord using a webhook, app id and interaction token for auth
    payload = {"content": "Here's the IP Address of the server: " +  ip_addr + ". Happy gaming!"}
    url = base_url + "/" + event["application_id"] + "/" + event["interaction_token"]
    r = requests.post(url, headers=headers, json=payload)
    print(r.text)