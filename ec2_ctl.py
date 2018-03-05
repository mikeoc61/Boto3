#!/usr/bin/env python

'''

Learning project to explore AWS CLI control of EC2 instances

Dependencies:

 - uses boto3 & botocore modules from AWS
 - uses click module for input argument processing
    - please see: http://click.pocoo.org/5/

Configuring

 - ec2_ctl requires that aws be configured with a valid user profile in ~/.aws/config
   and that the environment variable AWS_PROFILE be set and exported

 > aws configure --profile <user account>
 > export AWS_PROFILE=<user account>

Running

  > ec2_ctl <COMMAND> <SUBCOMMAND> <--project=PROJECT>

  *COMMAND* is instances, volumes,or snapshots
  *SUBCOMMAND* depends on command
  *PROJECT* is optional (looks for Tags)

'''

__author__      = "Michael E. O'Connor"
__copyright__   = "Copyright 2018"

import os
import sys
import boto3
import botocore
import click

# Assume we will run command with specific set of user credentials authorized
# to perform EC2 functions. Verify that AWS_PROFILE has been set.

try:
    user_name = os.environ["AWS_PROFILE"]
    print ("Found AWS_PROFILE set to {0}".format(user_name))
except KeyError:
    print ("Please set environment variable: AWS_PROFILE e.g. export AWS_PROFILE=<user account>")
    sys.exit(1)

session = boto3.Session(profile_name=user_name)
ec2 = session.resource('ec2')

# Incase we want to operate on a subset of resources identified by a Project tag

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

# Click is used to process & parse command line arguments

@click.group()
def cli():
    """Ec2_ctl manages snapshots"""

# Snapshot specific operations

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")

def list_snapshots(project):
    "List snapshots by volume"

    instances = filter_instances(project)

    print("Listing snapshots...")
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                s.id, v.id, i.id, s.state, s.progress,
                s.start_time.strftime("%c")
                )))

                if s.state == 'completed': break
    return

# EC2 Volume related Commands

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")

def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    print("Listing EC2 Volumes...")
    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id, i.id, v.state, str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

# EC2 Instance related Commands

@cli.group('instances')
def instances():
    """Commands for EC2 instances"""

@instances.command('snapshot')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")

def create_snapshots(project):
    "Create snapshots for EC2 attached volumes"

    instances = filter_instances(project)

    print("Creating snapshots...")
    for i in instances:

        i.stop()
        print("Stopping EC2 instance: {0}...".format(i.id))
        i.wait_until_stopped()

        for v in i.volumes.all():
            print("  Creating snapshot of Volume: {0}...".format(v.id))
            v.create_snapshot(Description="Created by SnapShotAnalyzer 3000")

        i.start()
        print("Now restarting EC2 instance: {0}...".format(i.id))
        i.wait_until_running()

    return

@instances.command('stop')
@click.option('--project', default=None,
    help="Only instances for project")

def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    print("Stopping EC2 Instances...")
    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Oops: can't stop {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project")

def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    print("Starting EC2 Instances...")
    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Oops: can't start {0}. ".format(i.id) + str(e))

    return

@instances.command('list')
@click.option('--project', default=None,
    help="only instances for project (tag Project:<name>)")

def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    print("Listing EC2 Instances...")
    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id, i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'], i.public_dns_name,
            tags.get('Project', '<no project>')
            )))

    return

# Main function

def main():
    cli()

# If invoked as command line script

if __name__ == '__main__':
    main()
