#!/usr/bin/env python

from __future__ import print_function

import os
import boto3
from botocore.exceptions import ProfileNotFound, ClientError

# Import list of valid AWS Regions we want to itterate through

from aws_regions import aws_regions

#-----------------------------------------------------------------------
# function to list all instantiated EC2 instances across all AWS Regions
# Requires that AWS_PROFILE Environment Variable be set so that error
# checking functions properly
#-----------------------------------------------------------------------

def list_all_ec2():

    # Check to see enviroment variable is set. Allow user to enter if not

    try:
        aws_profile = os.environ["AWS_PROFILE"]

    except KeyError:
        aws_profile = input ("AWS_PROFILE is not set. Please enter a valid AWS_Profle: ")
        os.environ["AWS_PROFILE"] = aws_profile

    aws_profile = os.environ["AWS_PROFILE"]

    # Check to see if this profile has credentials recognized by AWS

    try:
        session = boto3.Session(profile_name=aws_profile)

    except ProfileNotFound as e:
        print ("Error: Invalid AWS_PROFILE so can't determine credentials")
        print ("Run 'aws configure --profile <profile name> to set")
        quit()

    # Have valid profile and credentials. Step through regions to list EC2 instances

    print ("AWS_Profile set to: {0}".format(aws_profile))
    print ("Scanning valid AWS regions for EC2 instances...")

    for region in aws_regions:

        ec2 = session.resource('ec2', region_name=region)

        instances = ec2.instances.all()

        firstpass=True          # Required for output formatting

        # Itterating through instances will require valid IAM Policy

        try:
            for i in instances:
                if firstpass:
                    firstpass=False;
                    print ("")
                tags = { t['Key']: t['Value'] for t in i.tags or [] }
                print(', '.join((
                    region, i.id, i.instance_type,
                    i.placement['AvailabilityZone'],
                    i.state['Name'], i.public_dns_name,
                    tags.get('Project', '<no tags>')
                    )))

        except ClientError as e:
            if e.response['Error']['Code'] == "UnauthorizedOperation":
                print ("Error: AWS_PROFILE=[{0}] does not have required permissions".format(aws_profile))
                print ("       Check IAM EC2 Access Policy associates with this user")
            else:
                print (e)
            quit()

        print('.', end='', flush=True)    # Output dots to represent progress

    print ("")

    return

def main():
    list_all_ec2()

if __name__ == '__main__':
    main()
