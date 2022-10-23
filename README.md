# vese-autoec2-server

[![Terraform](https://github.com/v3se/vese-autoec2-server/actions/workflows/terraform-cd.yml/badge.svg)](https://github.com/v3se/vese-autoec2-server/actions/workflows/terraform-cd.yml)

This is used to deploy autoec2 server to AWS EC2 using Terraform. Afterwards it can be managed by a Serverless Discord bot running on AWS Lambda. Deployment of the lambda functions are done using Serverless Framework.

## Installation

1. Create Discord [bot]( https://discordpy.readthedocs.io/en/stable/discord.html) and add it to your server
2. Register [slash](https://discord.com/developers/docs/interactions/application-commands#registering-a-command) commands for your bot. TL;DR: 

```
import requests

url = "https://discord.com/api/v8/applications/<application_id>/commands"

# This is an example CHAT_INPUT or Slash Command, with a type of 1
json = {
    "name": "start_autoec2",
    "type": 1,
    "description": "Start autoec2 server"
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot <bot-token>"
}

r = requests.post(url, headers=headers, json=json)
print(r.text)
```
3. Install and configure AWS CLI, Serverless Framework and Terraform
4. Create S3 bucket and IAM user for terraform. Configure your AWS CLI accordingly. Modify main.tf backend config and terraform.tfvars to reflect your config.
5. Deploy with serverless framework
6. Profit

## Environment variables

| Variable           | Description                                                                                                         |
|--------------------|---------------------------------------------------------------------------------------------------------------------|
| DISCORD_PUBLIC_KEY | This can be retrieved from Discord Developer portal. Used for verifying signature in Discord - Lambda communication |
| AWS_REGION         | The AWS region you want to deploy the resources to. E.g. eu-north-1                                                 |
| TF_VAR_ec2_management_source_ip | Source CIDR from where to allow ssh connections from to the server                                     |

# TODO
- Write usage instructions
- Clean up the code
- Create CI/CD pipelines
- Create tests
- Create Ansible for middleware and software installation
- Code feature where multiple instances can be launched with different commands
- DNS

