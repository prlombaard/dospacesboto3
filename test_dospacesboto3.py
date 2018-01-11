"""Module to test the main dospacesboto3 module"""
import pytest
from prettyprinter import cpprint
import dospacesboto3
import os
import time

# *********************Test variables**************************
# TODO: Refactor test file paths to relative paths to work in any environment
s_spaces_name = 'prlombaard-my-first-space'
s_local_file_path = '/home/abc/Pictures/polarbear_1920x1080.jpeg'
s_local_file_name = 'polarbear_1920x1080.jpeg'
s_find_file_path = 'new-folder/polarbear_1920x1080.jpeg'
i_local_file_size = os.path.getsize(s_local_file_path)

print('Initializing Digital Ocean Spaces Client')
client_do = dospacesboto3.digital_ocean_client_init()
print('DO client initialized')

# print("Here is a list of the files contained in the spaces")
list_of_files = dospacesboto3.get_list_of_files(client_do, s_spaces_name, folder_prefix='Pictures')
# TODO: print the file list better
# print(list_of_files)
# cpprint(list_of_files)

print('Get list of files using pagination')
list_of_files_pagination = dospacesboto3.get_list_of_files_using_pagination(client_do, s_spaces_name,
                                                                            folder_prefix='new-folder')
# print(list_of_files)
cpprint(list_of_files_pagination)

print("Uploading file")

dospacesboto3.upload_file(client_do, s_local_file_path, s_spaces_name, 'new-folder/polarbear_1920x1080.jpeg')

print("File uploaded to DigitalOcean")

print('Downloading file')

dospacesboto3.download_file(client_do, s_local_file_name, s_spaces_name, 'new-folder/polarbear_1920x1080.jpeg')

print('File downloaded')

print('Check if a particular file exists')

exists_size = dospacesboto3.get_remote_file_size(client_do, s_spaces_name, s_find_file_path)
not_exist_size = dospacesboto3.get_remote_file_size(client_do, s_spaces_name, 'notexist.jpeg')

does_exist_bool = dospacesboto3.get_remote_file_exists(client_do, s_spaces_name, s_find_file_path)
does_not_exists_bool = dospacesboto3.get_remote_file_size(client_do, s_spaces_name, 'notexist.jpeg')

print(f'Do {s_find_file_path} exist?        : {does_exist_bool}')
if exists_size:
    print(f'Existing size of {s_find_file_path} : {exists_size}')

print(f'Original local file size {i_local_file_size}')

i_after_download_file_size = os.path.getsize(s_local_file_name
                                             )
print(f'Local file size  after download {i_after_download_file_size}')

print(f'Do not exists.jpeg exist?          : {"yes" if not_exist_size else "no"}')
if not_exist_size:
    print(f'Existing size of notexists.jpeg : {not_exist_size}')

response_times = []
# Check all of the files on digital ocean if they exist
for f in list_of_files:
    start = time.time()
    print(f'Does {f} exist?')
    bool_remote_file_exist = dospacesboto3.get_remote_file_exists(client_do, s_spaces_name, f)
    print(f'{"YES" if bool_remote_file_exist else "NO"}')
    response_times.append(time.time() - start)
    print(f'Exists operation took : {response_times[-1]} seconds')

print(f'Total time taken ({sum(response_times)} seconds) to check {len(response_times)} files')
print(f'Average time to check each file = {sum(response_times) / len(response_times)}')

print('FINISHED')
