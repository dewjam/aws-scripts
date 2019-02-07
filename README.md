

## Get all the IPs

##### Prerequisites
1. An account for each master/payer account that can be used to enumerate linked accounts via the Organizations API.

2. A role within each linked account that can be assumed by the master account

##### Steps

1. Get all Accounts via the Organizations API

1. Get all Regions via the EC2 API

1. Check for Public IPs in each Account and within each Region for the following services:
  - apigateway
  - cloudfront
  - ec2
  - elasticsearch
  - elb
  - lightsail
  - rds
  - redshift
1. Write IPs to a CSV file
