import json
import os
import logging
import boto3
from boto3 import client as boto3_client
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
PUBLIC_KEY = os.environ['DISCORD_PUBLIC_KEY'] # found on Discord Application -> General Information page
AWS_REGION = os.environ['AWS_PRIMARY_REGION']
INSTANCE_TAGS = {
  'satisfactory': 'satisfactory-server',
  'valheim': 'valheim-server'
}

def lambda_handler(event, context):
  try:
    logger.info(f"event {event}")
    body = json.loads(event['body'])
        
    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']

    # Verifies the that the POST is from discord using public key

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    message = timestamp + event['body']
    
    try:
      verify_key.verify(message.encode(), signature=bytes.fromhex(signature))
    except BadSignatureError:
      logger.info(message)
      logger.info(PUBLIC_KEY)
      logger.error('invalid request signature')
      return {
        'statusCode': 401,
        'body': json.dumps('invalid request signature')
      }

    t = body['type']

    if t == 1:
      return {
        'statusCode': 200,
        'body': json.dumps({
          'type': 1
        })
      }
    elif t == 2:
      return command_handler(body)
    else:
      return {
        'statusCode': 400,
        'body': json.dumps('unhandled request type')
      }
  except:
    raise

def lambda_child_check_status(body, game_name):
    # Invoke child lambda function for performing backend tasks
    # Discord expects response within 3s. Therefore a follow up message is necessary in this case
    # to report pub ip address
    lambda_client = boto3_client('lambda')
    #Parse interaction token and app id from body
    msg = {"application_id": body["application_id"], "interaction_token": body["token"], "game_name":game_name}
    invoke_response = lambda_client.invoke(FunctionName="autoec2-child-status",
                                           InvocationType='Event',
                                           Payload=json.dumps(msg))
    logger.info(f"Invocation response: {invoke_response}")

def get_cost_usage(game_name):
    client = boto3.client('ce')
    start_date = datetime.today().replace(day=1).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")
    if start_date == end_date:
        #The filter does not work if the start date is the same as the end date. This subracts 1 day from the start date if that's the case"
        start_date = (datetime.today().replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
    cost = client.get_cost_and_usage(
    TimePeriod={
        'Start': start_date,
        'End': end_date
    },
    Filter={
        'Tags': {
            'Key': 'project',
            'Values': [
                'autoec2',
            ],
            'MatchOptions': [
                'EQUALS'
            ]
        }
    },
    Granularity='MONTHLY',
    Metrics=["UnblendedCost"],
    )['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']

    return round(float(cost),2)
    
def start_autoec2_server(body, game_name):
    # Do a dryrun first to verify permissions
    game_name = INSTANCE_TAGS[game_name]
    #cost = get_cost_usage(game_name)
    ec2 = boto3.client('ec2', region_name=AWS_REGION)
    # Gets the instance id by tag
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name', 'Values':[game_name],
            },
        ],
    )
    logger.info(response)
    instance_id = response["Reservations"][0]["Instances"][0]["InstanceId"]
    state = response["Reservations"][0]["Instances"][0]["State"]["Name"]

    if state == "running":
      public_ip = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
      return {
      'statusCode': 200,
      'body': json.dumps({
          'type': 4,
          'data': {
          'content': "Server is already running at: {}".format(public_ip),
          }
      })
      }

    try:
        ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise
    # Dry run succeeded, run start_instances without dryrun
    try:
        response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
        logger.info(response)
        
        parse_id = response["StartingInstances"][0]["InstanceId"]
        lambda_child_check_status(body, game_name)
        return {
        'statusCode': 200,
        'body': json.dumps({
            'type': 4,
            'data': {
            'content': "Yes Sir! Starting {} server for you... Reporting the IP address shortly. Here's the EC2 ID: {}".format(game_name,parse_id),
            }
        })
        }
  
    except ClientError as e:
        logger.info(e)
        return {
        'statusCode': 200,
        'body': json.dumps({
            'type': 4,
            'data': {
            'content': e.response['Error']['Message'],
            }
        })
        }

def command_handler(body):
  command = body['data']['name']

  if command == 'bleb':
    return {
      'statusCode': 200,
      'body': json.dumps({
        'type': 4,
        'data': {
          'content': 'Well hello there my good Sir!',
        }
      })
    }

  if command == 'start_satisfactory':
    return start_autoec2_server(body,'satisfactory')
  if command == 'start_valheim':
    return start_autoec2_server(body,'valheim')


  else:
    return {
      'statusCode': 400,
      'body': json.dumps('unhandled command')
    }
