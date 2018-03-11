#!/usr/bin/env python

from __future__ import print_function

# Python code to provide a listing of available AWS S3 buckets or if
# passed a command line argument, list the contents of that specific bucket

__author__      = "Michael E. O'Connor"
__copyright__   = "Copyright 2018"

import sys
import boto3
import botocore
import datetime

# Display list of all S3 buckets associated with user credentials

def s3ls_all():

   now = datetime.datetime.now()

   cw = boto3.client('cloudwatch')
   s3 = boto3.client('s3')

   mybuckets = s3.list_buckets()

   # Header Line for the output going to standard out
   print('Bucket'.ljust(36) + 'Size in Bytes'.rjust(24))

   for bucket in mybuckets['Buckets']:
#       date = datetime.datetime.strptime(bucket['CreationDate'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%m/%d/%Y')
#       print ("{1:.32} {0}".format(date, bucket['Name']))
        response = cw.get_metric_statistics(Namespace='AWS/S3',
                   MetricName='BucketSizeBytes',
                   Dimensions=[
                           {'Name': 'BucketName', 'Value': bucket['Name']},
                           {'Name': 'StorageType', 'Value': 'StandardStorage'}
                           ],
                   Statistics=['Average'],
                   Period=3600,
                   StartTime=(now-datetime.timedelta(days=1)).isoformat(),
                   EndTime=now.isoformat()
                   )

        for item in response["Datapoints"]:
             print(bucket["Name"].ljust(36) + str("{:,}".format(int(item["Average"]))).rjust(24))

   return 1

# Display list of file objects associated with provided S3 bucket name

def s3ls_specific (target):

   s3 = boto3.resource('s3')
   bucket = s3.Bucket(target)
   for obj in bucket.objects.all():
       print (obj.key)

   return 1


def main():

    my_session = boto3.session.Session()
#    print ("Current Default Region: [%s]" % my_session.region_name)

    # Check to see if bucket name was provided on command line
    # If not then display a listing of all buckets owned by user

    if len(sys.argv) == 1:
        print ("Listing all S3 Buckets owned by user associated with access keys")
        return (s3ls_all())

    # Since we are looking to list the contents of a specific S3 bucket
    # we need to check to see if the bucket name is valid and readable
    # before proceeding

    if len(sys.argv) == 2:
        arg = sys.argv[1]
    else:
        print ("Sorry, this sad little program only accepts a single command line argument")
        return 0

    s3 = boto3.resource('s3')

    try:
        s3.meta.client.head_bucket(Bucket=arg)

    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        print ("HTTP Error Code [%s]: Bucket name [%s] is not accessible" % (error_code, arg))
        print ("See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes")
        return 0

    # Made it this far so let's print out a list of file objects associated with this bucked name

    print ("Searching for readable s3 buckets matching name: [%s]" % arg)
    return (s3ls_specific(arg))            # All clear so get list of bucket contents

if __name__ == '__main__':
  main()
