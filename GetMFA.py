import boto3, csv

# Get all accounts from the Organization API
def getLinkedAccounts():
    org = boto3.client('organizations')
    accounts = []
    for i in org.list_accounts()['Accounts']:
        if i['Status'] == 'ACTIVE':
            accounts.append(i)
    return accounts

# Construct the role ARN using the account number and role name
def getRoleARN(account):
    role = 'arn:aws:iam::' + account + ':role/' + role_name
    return role

# Assume role to get credentials
def assumeRole(account):
    client = boto3.client('sts').assume_role(RoleArn=getRoleARN(account), RoleSessionName='mfaListSession')
    return client['Credentials']

# Get the current payer account number
def getCurrentAccount():
    return boto3.client('sts').get_caller_identity().get('Account')

# Get MFA status for Accounts
def getMFA(account, credentials):
    # Here we create an IAM client and set the appropriate credentials for the account
    iam_client=boto3.client(
        'iam',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
        )
    # Here we append the account info to a list/array
    mfaList.append({'linkedAccount': account['Id'],
                    'accountName': account['Name'],
                    'accountStatus': account['Status'],
                    'mfaEnabled': iam_client.get_account_summary()['SummaryMap']['AccountMFAEnabled']})

# Write out data to CSV file
def outputCSV(list):
    with open(filePath, 'w') as csvfile:
        fieldnames = ['payerAccount',
                      'linkedAccount',
                      'accountName',
                      'accountStatus',
                      'mfaEnabled']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for x in list:
            writer.writerow({'payerAccount': getCurrentAccount(),
                  'linkedAccount': x['linkedAccount'],
                  'accountName': x['accountName'],
                  'accountStatus': x['accountStatus'],
                  'mfaEnabled': x['mfaEnabled']})


# Set the role name you intend to use across linked accounts. The IAM user
# from the payer account must be able to assume this role.
role_name = 'AwsSecurityAudit'

# Initialize the mfaList variable as an array
mfaList = []

# Set the CSV File name
filePath = 'mfaList.csv'

# Get all accounts from the Organization API (using local access key/secret key to access the API)
accountList = getLinkedAccounts()

# Loop through all accounts and get MFA status
iter=0
for i in accountList:
    iter+=1
    print("Getting MFA status for account " + str(iter) + " of " + str(len(accountList)), end='\r')
    # Get temp credentials for the role you are assuming
    credentials = assumeRole(i['Id'])
    # Get MFA info and append to the list
    getMFA(i, credentials)

# Output data to CSV file
outputCSV(mfaList)

# Done
print("\nCSV written to: ", filePath)
