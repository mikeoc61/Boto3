#!/usr/bin/env python3

import os
import boto3
from aws_regions import aws_regions

def list_all_ec2():

    instances = []

    aws_profile = os.environ["AWS_PROFILE"]
    session = boto3.Session(profile_name=aws_profile)
    print ("Profile set to: {0}".format(aws_profile))
    print ("Scanning all valid AWS regions for EC2 instances...")

    for region in aws_regions:

        ec2 = session.resource('ec2', region_name=region)

        instances = ec2.instances.all()

        for i in instances:
            tags = { t['Key']: t['Value'] for t in i.tags or [] }
            print(', '.join((
                region, i.id, i.instance_type,
                i.placement['AvailabilityZone'],
                i.state['Name'], i.public_dns_name,
                tags.get('Project', '<no tags>')
                )))
    return

def main():
    list_all_ec2()

if __name__ == '__main__':
    main()
