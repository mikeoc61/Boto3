#!/usr/bin/env python

# Python code to create an S3 bucket that matches name specified on the command line

__author__      = "Michael E. O'Connor"
__copyright__   = "Copyright 2018"

import sys
import boto3
import botocore

def main():

    my_session = boto3.session.Session()
    my_region = my_session.region_name
#    print ("Current Region: [%s]" % my_region)

    if len(sys.argv) == 2: 
        bucket_name = sys.argv[1]
    else:
        print ("Sorry, please provide the name of a single S3 bucket to create in region: [%s]" % my_region)
        print ("Usage: %s <bucket_name>" % sys.argv[0])
        return 0

    # Create an S3 client

    s3 = boto3.resource('s3')

    # Rather than simply trying to create the bucket, first check to see if we can 
    # access any meta data associate with this same bucket name.
    # If try produces anything other than a 404 error_code, we have a problem!

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)

    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 403:
            print("Sorry, this S3 bucket name already exists globally and is private!")
            return False
        elif error_code == 404:
            print("Creating bucket name: [%s] in region: [%s]" % (bucket_name, my_region))
            s3 = boto3.client('s3')
            s3.create_bucket(Bucket=bucket_name)
            return True
        else:
            print ("Error attempting to validate bucket name: [%s] in region: [%s]" % (bucket_name, my_region))
            print ("HTTP Error Code [%s]" % error_code)
            print ("See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes")
            return False

     # Our try didn't throw an exception which means our bucket name already exists and is accessable

    print ("Sorry, bucket name: [%s] already exists! Create aborted. Returning to regularly scheduled programming" % bucket_name)
    return False

if __name__ == '__main__':
  main()
