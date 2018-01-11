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

# TODO: Refactor test file paths to relative paths to work in any environment
s_spaces_name = 'prlombaard-my-first-space'
s_local_file_path = '/home/abc/Pictures/polarbear_1920x1080.jpeg'
s_local_file_name = 'polarbear_1920x1080.jpeg'
s_find_file_path = 'new-folder/polarbear_1920x1080.jpeg'
i_local_file_size = os.path.getsize(s_local_file_path)

# DONE: get from the real environment
if not os.environ.get('ENV_DO_ACCESS_KEY_ID'):
    # TODO: raise warning on logger level
    print('WARNING!!!, could not retrieve ENV_DO_ACCESS_KEY_ID from environment using hard coded value')
ENV_DO_ACCESS_KEY_ID = os.environ.get('ENV_DO_ACCESS_KEY_ID') or 'H3PTDVXALKYXB4OU7OMA'

if not os.environ.get('ENV_DO_SECRET_ACCESS_KEY'):
    # TODO: raise warning on logger level
    print('WARNING!!!, could not retrieve ENV_DO_SECRET_ACCESS_KEY from environment using hard coded value')
ENV_DO_SECRET_ACCESS_KEY = os.environ.get('ENV_DO_SECRET_ACCESS_KEY') or '2Z+YJ+qEhnL1rKakK47nVPFHPYzN93V10+mb7joFerk'


def digital_ocean_client_init(region_name='nyc3', endpoint_url='https://nyc3.digitaloceanspaces.com',
                              aws_access_key_id=ENV_DO_ACCESS_KEY_ID, aws_secret_access_key=ENV_DO_SECRET_ACCESS_KEY):
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=region_name,
                            endpoint_url=endpoint_url,
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)
    return client


def get_list_of_files_using_pagination(client, spaces_name, folderPrefix=''):
    # TODO: use pagination S3 returns only the first 1000 objects per page.
    # Using example from https://adamj.eu/tech/2018/01/09/using-boto3-think-pagination/
    paginator = client.get_paginator('list_objects')
    file_list = []
    pages = paginator.paginate(Bucket=spaces_name, Prefix=folderPrefix)
    for page in pages:
        for obj in page['Contents']:
            # print(obj)
            file_list.append(obj)
    return file_list


def get_list_of_files(client, spaces_name, folderPrefix=''):
    # resp = client.list_objects(Bucket='s_spaces_name', Prefix='foo/')
    # resp = client.list_objects(Bucket=s_spaces_name, Prefix='Pictures')
    file_list = []
    resp = client.list_objects(Bucket=s_spaces_name, Prefix=folderPrefix)
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


client_do = digital_ocean_client_init()

# print("Here is a list of the files contained in the spaces")
# list_of_files = get_list_of_files(client_do, s_spaces_name, folderPrefix='Pictures')
# TODO: print the file list better
# print(list_of_files)
# cpprint(list_of_files)

print('Get list of files using pagination')
list_of_files_pagination = get_list_of_files_using_pagination(client_do, s_spaces_name, folderPrefix='new-folder')
# print(list_of_files)
cpprint(list_of_files_pagination)

print("Uploading file")

upload_file(client_do, s_local_file_path, s_spaces_name, 'new-folder/polarbear_1920x1080.jpeg')

print("File uploaded to DigitalOcean")

print('Downloading file')

download_file(client_do, s_local_file_name, s_spaces_name, 'new-folder/polarbear_1920x1080.jpeg')

print('File downloaded')

print('Check if a particular file exists')

exists_size = get_remote_file_size(client_do, s_spaces_name, s_find_file_path)
not_exist_size = get_remote_file_size(client_do, s_spaces_name, 'notexist.jpeg')

does_exist_bool = get_remote_file_exists(client_do, s_spaces_name, s_find_file_path)
does_not_exists_bool = get_remote_file_size(client_do, s_spaces_name, 'notexist.jpeg')

print(f'Do {s_find_file_path} exist?        : {does_exist_bool}')
if exists_size:
    print(f'Existing size of {s_find_file_path} : {exists_size}')

print(f'Original local file size {i_local_file_size}')

i_after_download_file_size = os.path.getsize(s_local_file_name
                                             )
print(f'Local file size  after download {i_after_download_file_size}')

print(f'Do notexists.jpeg exist?          : {"yes" if not_exist_size else "no"}')
if not_exist_size:
    print(f'Existing size of notexists.jpeg : {not_exist_size}')

response_times = []
# Check all of the files on digital ocean if they exist
for f in list_of_files:
    start = time.time()
    print(f'Does {f} exist?')
    bool_remote_file_exist = get_remote_file_exists(client_do, s_spaces_name, f)
    print(f'{"YES" if bool_remote_file_exist else "NO"}')
    response_times.append(time.time() - start)
    print(f'Exists operation took : {response_times[-1]} seconds')

print(f'Total time taken ({sum(response_times)} seconds) to check {len(response_times)} files')
print(f'Average time to check each file = {sum(response_times) / len(response_times)}')

print('FINISHED')
