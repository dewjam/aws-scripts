#!/bin/python3

import boto3

# Set the role name you intend to use across linked accounts
role_name = 'AwsSecurityAudit'

# Initialize the ipList variable as an array
ipList = []

# Get all accounts from the Organization API
def getAccounts():
    org = boto3.client('organizations')
    accounts = []
    for i in org.list_accounts()['Accounts']:
        accounts.append(i['Id'])
    return accounts

# List all regions for which a service is available
def getRegions(service):
    regions = boto3.session.Session().get_available_regions(service)
    return regions

# Construct the role ARN using the account number and role name
def getRoleARN(account):
    role = 'arn:aws:iam::' + account + ':role/' + role_name
    return role

# Assume role to get credentials
def assumeRole(account):
    client = boto3.client('sts').assume_role(RoleArn=getRoleARN(account), RoleSessionName='ipListSession')
    return client['Credentials']

# Get all ENIs from the account and append them to the ipList array
def getENIs(account):
    regions = getRegions('ec2')
    # Loop through available regions and get all ENIs
    for r in regions:
        # Get temp credentials for the role you are assuming
        credentials = assumeRole(account)
        # Here we create a client for the appropriate region and set the Credentials we are using
        ec2_resource=boto3.client(
            'ec2',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=r
            )
        # Here we get the actual ENI details using the client we created
        interfaces = ec2_resource.describe_network_interfaces()
        # Here we're just filtering out ENIs which don't have public IP associated
        if 'NetworkInterfaces' in interfaces:
            for i in interfaces['NetworkInterfaces']:
                if 'Association' in i:
                    ipList.append(i['Association']['PublicIp'])


# Get all accounts from the Organization API (using local access key/secret key to access the API)
accountList = getAccounts()

# Loop through all accounts and get IPs associated with resources
for i in accountList:
    getENIs(i)

print(ipList)
