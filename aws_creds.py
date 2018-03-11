#!/usr/bin/env python3

'''
aws_creds.py

AWS CLI and Boto rely on configuration information typically defined in
the user's $HOME/.aws/config and credentials files and or by shell
environment valiables such as $AWS_PROFILE.

This program verifies that the initial configuration has been setup
correctly, reports current settings to the user and allows the user
to make changes.

Finally, the program lists out all EC2 instances associated with the
user selected profile and region

'''

__author__      = "Michael E. O'Connor"
__copyright__   = "Copyright 2018"

import os
from getpass import getpass
from aws_regions import aws_regions
from botocore.exceptions import ProfileNotFound, ClientError
import botocore
import boto3

#-------------------------------------------------
# Check and set AWS_PROFILE Environment variable
#-------------------------------------------------

def check_profile_env():

    try:
        aws_profile = os.environ["AWS_PROFILE"]
        resp = input ("AWS_PROFILE set to [{0}]. Press enter to confirm or specify new: ".format(aws_profile))
        if bool(resp.strip()):
            print ("Profile changed to [{0}]".format(resp))
            aws_profile = resp

    except KeyError:
        aws_profile = input ("AWS_PROFILE is not set. Please enter a valid AWS_Profle: ")

    os.environ["AWS_PROFILE"] = aws_profile

    return aws_profile

#-------------------------------------------------------
# Confirm Keys are properly set in ~/.aws/credentials
#-------------------------------------------------------

def check_credentials(session):

    try:
        credentials = session.get_credentials()
        print ("Access Key = {0}{1}".format('*'*16, credentials.access_key[-4:]))
        print ("Secret Key = {0}{1}".format('*'*36, credentials.secret_key[-4:]))
        return (credentials)

    except ProfileNotFound:
        print ("Error: AWS_PROFILE not defined so can't determine credentials")
        print ("Run 'aws configure --profile <profile name> to set")
        return False

#-------------------------------------------------
# Ensure we have a valid region specified
#-------------------------------------------------

def check_region(session):

    try:
        region = session.get_config_variable('region')
        resp = input ("Region set to [{0}]. Press enter to confirm or provide new region: ".format(region))
        if bool(resp.strip()):
            region = resp
            print ("Region changed to [{0}]".format(region))

    except ProfileNotFound:
        region = input ("Please enter a valid AWS Region: ")

    while region not in aws_regions:
        print ("Error: [{0}] is not a valid AWS region".format(region))
        print ("Valid choices are...")
        for key in aws_regions:
            print ("[{0}] located in {1}".format(key, aws_regions[key]))
        region = input ("Please enter a valid AWS Region: ")

    return region

#--------------------------------------
# Display all EC2 instances
#--------------------------------------

def list_ec2_instances(profile, region):

    session = boto3.Session(profile_name=profile)
    ec2 = session.resource('ec2', region_name=region)
    instances = ec2.instances.all()

    try:
        for i in instances:
            tags = { t['Key']: t['Value'] for t in i.tags or [] }
            print(', '.join((
                region, i.id, i.instance_type,
                i.placement['AvailabilityZone'],
                i.state['Name'], i.public_dns_name,
                tags.get('Project', '<no tags>')
                )))

    except ClientError as e:
        if e.response['Error']['Code'] == "UnauthorizedOperation":
            print ("Error: AWS_PROFILE=[{0}] does not have required permissions".format(profile))
            print ("       Check IAM EC2 Access Policy associates with this user")
        else:
            print (e)
        quit()

    return

#-----------------------------------------
# Main routine
#-----------------------------------------

def main():

    # Check to see if AWS_PROFILE environment variable set. Allow user to set or change

    aws_profile = check_profile_env()

    # At this point, AWS_PROFILE has been set so establish session with AWS

    session = botocore.session.get_session()

    # Confirm profile is valid by getting credentials from boto. If not, bail

    if check_credentials(session) == False:
        quit()

    # See if user wants (or needs) to change target Region

    region = check_region(session)

    # At this point, everything should be copacetic so carry on...

    # For the specified credentials and region, list EC2 instances

    list_ec2_instances(aws_profile, region)

if __name__ == '__main__':
    main()
