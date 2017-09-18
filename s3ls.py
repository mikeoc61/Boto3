#!/usr/bin/env python

# Python2 code to provide a listing of available AWS S3 buckets or if
# passed a command line argument, list the contents of that specific bucket

__author__      = "Michael E. O'Connor"
__copyright__   = "Copyright 2017"

import sys
import boto3
import botocore

def s3ls (target):

    if target == "ALL":
        s3 = boto3.client('s3')
        # Call S3 to list current buckets
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
#        print("Bucket List: %s" % buckets)
        for bucket in response['Buckets']:
            print bucket['Name']
    else:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(target)
        for obj in bucket.objects.all():
            print obj.key

    return 1


def main():

    my_session = boto3.session.Session()

    if len(sys.argv) >= 2:          # User provided an S3 bucket name
        arg = sys.argv[1]
    else:                           # Provide listing of all available buckets
        arg = "ALL"
        print ("Listing S3 Buckets in Region: [%s]" % my_session.region_name)
        return (s3ls(arg))

    # Since we are looking to list the contents of a specific S3 bucket
    # we need to check to see if the bucket name is valid and readable
    # before proceeding

    s3 = boto3.resource('s3')
    success = True

    try:
        s3.meta.client.head_bucket(Bucket=arg)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        success = False

    if success:
        return (s3ls(arg))            # All clear so get list of bucket contents
    else:
        print ("Error Code [%s]: Bucket name [%s] is not accessible" % (error_code, arg))
        print ("See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes")
        return 0

if __name__ == '__main__':
  main()
