
# Versa Concerto API JSON 

This application utilizes the available Versa API to automate Versa services in enterprise networks. Each Python script performs various operations with Versa to meet service requests efficiently.




## Tasks

The program is designed to run several sequential API calls to perform the following tasks:

    1. Retrieve input from Excel.
    2. Validate the input.
    3. Perform pre-execution validation.
    4. Execute the required tasks.
    5. Perform post-execution validation.  


## Order of Operation

The program imports login.py where the API key is retrieved from .env file and also imports loggin.py for the logger. Few Programs makes use of password_generator.py to generate random keys.

- Get API Key from .env File.

- logging.py has been imported to perform logging.

- Perform API requests and responses with Exceptions.

- Execution logs are generated as script.log in root directory.



## Requirements

- Python==3.11.7
- python-dotenv~=1.0.1
- openpyxl~=3.1.5
- requests~=2.32.3


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`API_KEY`

`BASE_URL`


## Authors

- [@Earnestpraveen](https://www.github.com/Earnestpraveen)

