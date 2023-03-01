import boto3
from datetime import datetime, timedelta

def get_cost_usage(game_name):
    client = boto3.client('ce')
    start_date = datetime.today().replace(day=1).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")
    if start_date == end_date:
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

    print(round(float(cost),2))
get_cost_usage("autoec2")