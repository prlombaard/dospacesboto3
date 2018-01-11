# dospacesboto3
A wrapper for boto3 to access Digital Ocean Spaces

## TODO
 - TODO: Refactor script into a module
 - TODO: Add py.test
 - Test get_file_list performance with and without pagination
 - Refactor, maybe change the way checking for file existance is done, rather use the pagination method and interrogate that object
 - Add per file meta-data modifications ie. MIME-Content-Type, currently automatically set to bin-stream
 - Add doc strings to each function
 - Refactor bottom statements into a main function / py.test
 - Refactor, performance test, check_remote_exists. currently very SLOW
 - Refactor test file paths to relative paths to work in any environment
 - Raise warnings when Digital Ocean ACCESS and SECRET not found in environment
 