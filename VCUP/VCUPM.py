#Code to connect to Versa

import json

import os
from dotenv import load_dotenv

from Modules.logging import AuditLog
from Modules.versa import Versa
from Modules.input import Excel

#Load all environment settings
load_dotenv()  # take environment variables from .env.

#Get all the required environment variables
inputFile = os.getenv('input_file_path')
tenant_uuid=os.getenv('tenant_uuid') #For Later: Remove this hard coding with actual code logic

# INITIALIZE LOGGING
log = AuditLog()
log.create_log_file()
log.logging_info('____Versa API POC___')

# INITIALIZE API CALL
versa = Versa(log)
conn = versa.versa_connect()

#
# Process the input
#
inputExcel = Excel(log)
if (not inputExcel.get_input(inputFile)):
    exit(0)

api="/portalapi/v1/tenants/"+tenant_uuid+"/sase/authentication/versa-directory"
payLoad={
  "attributes": {
    "directory": {
      "value": {
        "userGroups": [
          {
            "description": inputExcel.desc,
            "name": inputExcel.name1
          }
        ],
        "users": [
          {
            "description": inputExcel.descrip,
            "emailId": inputExcel.emailID,
            "firstName": inputExcel.firstName,
            "groupNames": [
              inputExcel.groupName
            ],
            "lastName": inputExcel.lastName,
            "password": inputExcel.password,
            "phoneNumber": "4518931234",
            "userName": inputExcel.userName
          }
        ]
      }
    }
  },
  "description": inputExcel.description,
  "enabled": inputExcel.enabled,    
  "name": inputExcel.name2
}

response = versa.invokePOST(api, json.dumps(payLoad))
log.logging_info(response)

log.logging_info(f"PayLoad= {payLoad}")

print("\n Program completed, for more info refer scriptlog file")

