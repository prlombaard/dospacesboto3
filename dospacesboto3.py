"""Module is a boto3 module wrapper which is used to access Digital Ocean Spaces (almost like AWS S3)"""

import boto3
import os
import time
from prettyprinter import cpprint

# TODO: Refactor script into a module
# TODO: Add py.test
# TODO: Test get_file_list performance with and without pagination
# TODO: Refactor, maybe change the way checking for file existinace is done, rather use the pagination method and interrogate that object
# TODO: Add per file meta-data modifications ie. MIME-Content-Type, currently automatically set to bin-stream
# TODO: Add doc strings to each function
# TODO: Refactor bottom statements into a main function / py.test
# TODO: Refactor, performance test, check_remote_exists. currently very SLOW


# DONE: get from the real environment
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')  # old key or 'H3PTDVXALKYXB4OU7OMA'
# AWS_ACCESS_KEY_ID = '42CCNXCE2HV4RDJMBCID'
if not AWS_ACCESS_KEY_ID:
    # TODO: raise warning on logger level
    print('WARNING!!!, could not retrieve AWS_ACCESS_KEY_ID from environment using hard coded value')

AWS_SECRET_ACCESS_KEY = os.environ.get(
    'AWS_SECRET_ACCESS_KEY')  # old key or '2Z+YJ+qEhnL1rKakK47nVPFHPYzN93V10+mb7joFerk'
# AWS_SECRET_ACCESS_KEY = '66FCtiNVcIJgDV4jpzx8dYZCYUaQDbX8itNCyNX/niM'
if not AWS_SECRET_ACCESS_KEY:
    # TODO: raise warning on logger level
    print('WARNING!!!, could not retrieve AWS_SECRET_ACCESS_KEY from environment using hard coded value')


# print(ENV_DO_ACCESS_KEY_ID)
# print(ENV_DO_SECRET_ACCESS_KEY)


def digital_ocean_client_init(region_name='nyc3', endpoint_url='https://nyc3.digitaloceanspaces.com',
                              aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY):
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=region_name,
                            endpoint_url=endpoint_url,
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)
    return client


def get_list_of_files_using_pagination(client, spaces_name, folder_prefix=''):
    # TODO: use pagination S3 returns only the first 1000 objects per page.
    # Using example from https://adamj.eu/tech/2018/01/09/using-boto3-think-pagination/
    paginator = client.get_paginator('list_objects')
    file_list = []
    pages = paginator.paginate(Bucket=spaces_name, Prefix=folder_prefix)
    for page in pages:
        for obj in page['Contents']:
            # print(obj)
            file_list.append(obj)
    return file_list


def get_list_of_files(client, spaces_name, folder_prefix=''):
    # resp = client.list_objects(Bucket='s_spaces_name', Prefix='foo/')
    # resp = client.list_objects(Bucket=s_spaces_name, Prefix='Pictures')
    file_list = []
    # BUG: Here is a bug!! Should be Bucket=spaces_name
    resp = client.list_objects(Bucket=spaces_name, Prefix=folder_prefix)
    for obj in resp['Contents']:
        file_list.append(obj['Key'])
        # print(obj['Key'])
    return file_list


def upload_file(client, path_to_local_file, spaces_name, path_for_remote_file):
    client.upload_file(path_to_local_file,  # Path to local file
                       spaces_name,  # Name of Space
                       path_for_remote_file)  # Name for remote file


def download_file(client, path_to_local_file, spaces_name, path_for_remote_file):
    client.download_file(spaces_name, path_for_remote_file, path_to_local_file)


# TODO: Refactor get_remote_file_size to use this function and perform comparative benchmark, maybe this is faster
def _key_existing_size__head(client, bucket, key):
    """return the key's size if it exist, else None"""
    try:
        obj = client.head_object(Bucket=bucket, Key=key)
        return obj['ContentLength']
    except ClientError as exc:
        if exc.response['Error']['Code'] != '404':
            raise


def _key_existing_size__list(client, bucket, key):
    """return the key's size if it exist, else None"""
    response = client.list_objects_v2(
        Bucket=bucket,
        Prefix=key,
    )
    for obj in response.get('Contents', []):
        if obj['Key'] == key:
            return obj['Size']


def get_remote_file_size(client, spaces_name, path_for_remote_file):
    remote_file_size = _key_existing_size__list(client, spaces_name, path_for_remote_file)
    return remote_file_size


def get_remote_file_exists(client, spaces_name, path_for_remote_file):
    return bool(get_remote_file_size(client, spaces_name, path_for_remote_file))
