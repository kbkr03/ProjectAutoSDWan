import os
from dotenv import load_dotenv

import requests
from requests.packages import urllib3
import re
import json

# Versa connection
class Versa:

    def __init__(self, log):
        self.log = log
        load_dotenv()

        self.log.logging_info('Trying to connect to Versa from .env to generate API token for oauth')
        self.URL = os.getenv('URL')
        self.USERNAME = os.getenv('USERNAME')
        self.PASSWORD = os.getenv('PASSWORD')
        self.CLIENT_ID = os.getenv('CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET')

        if not self.USERNAME:
            self.log.logging_error('No Username in .env file')
        if not self.PASSWORD:
            self.log.logging_error('No Password in .env file')
        if not self.URL:
            self.log.logging_error('No Url in .env file')
        if not self.CLIENT_ID:
            self.log.logging_error('No Client Id in .env file')
        if not self.CLIENT_SECRET:
            self.log.logging_error('No Client Secret in .env file')

    def versa_connect(self):
        # Suppress only the single warning from urllib3.
        urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

        #Establish a session
        self.session = requests.Session()

        body = {"username": self.USERNAME, "password": self.PASSWORD}
        # Gets X-CSRF-TOKEN (ECP-CSRF-TOKEN)
        self.session.get(self.URL, verify=False)
        headers = {
            "X-CSRF-Token": self.session.cookies["ECP-CSRF-TOKEN"],
            "Content-Type": "application/json"
        }
        cookies = {
            "EECP-CSRF-TOKEN": self.session.cookies["EECP-CSRF-TOKEN"]
        }

        # Logs in to the site
        response = self.session.post(
            self.URL + "/v1/auth/login",
            verify=False,
            cookies=cookies,
            headers=headers,
            json=body,
        )

        #self.log.logging_info(body)
        self.log.logging_info(response)
        self.log.logging_info(response.text)

        """# Step 1: Getting initial CSRF token"""

        self.log.logging_info("*** Step 1: Getting initial CSRF token")
        response = self.session.get(f"{self.URL}/", verify=False)
        self.log.logging_info(f"Initial request status code: {response.status_code}")

        ecp_csrf_token = self.session.cookies.get("ECP-CSRF-TOKEN")
        eecp_csrf_token = self.session.cookies.get("EECP-CSRF-TOKEN")

        if not ecp_csrf_token or not eecp_csrf_token:
            self.log.logging_error("Failed to obtain CSRF tokens")
            exit(1)

        self.log.logging_info(f"ECP-CSRF-TOKEN: {ecp_csrf_token}")
        self.log.logging_info(f"EECP-CSRF-TOKEN: {eecp_csrf_token}")

        """# Step 2: Authenticate"""

        self.log.logging_info("*** Step 2: Authenticating")
        auth_url = f"{self.URL}/v1/auth/token"
        headers = {
            "X-CSRF-Token": ecp_csrf_token,
            "Content-Type": "application/json"
        }
        cookies = {
            "EECP-CSRF-TOKEN": eecp_csrf_token
        }
        body = {
            "username"  : self.USERNAME,
            "password"  : self.PASSWORD,
            "grant_type": "password",
            "scope"     : "global" ,
            "client_id" : self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }

        auth_url = self.URL + "/portalapi/v1/auth/token"
        response = self.session.post(auth_url, json=body, headers=headers, cookies=cookies, verify=False)
        self.log.logging_info(f"Auth response status: {response.status_code}")


        # self.log.logging_info the full response for debugging
        self.log.logging_info(auth_url)
        self.log.logging_info (body)
        self.log.logging_info("Full authentication response:")
        self.log.logging_info(response.text)

        """# Get Token"""

        self.token = None

        if response.status_code == 201:
            self.log.logging_info("Authentication successful")
            self.log.logging_info(response)

            # Check response body for token
            try:
                json_response = response.json()
                self.log.logging_info(json_response)
                if 'access_token' in json_response:
                    self.token = json_response['access_token']
            except :
                self.log.logging_warning("Warning: Token key not found in the response json, continuing to look in non-json format")

            # Check headers for token
            self.log.logging_info("response.headers = ")
            self.log.logging_info(response.headers)
            if 'Authorization' in response.headers:
                self.token = response.headers['Authorization']
            elif 'Token' in response.headers:
                self.token = response.headers['Token']

            # Check cookies for token
            if 'auth_token' in response.cookies:
                self.token = response.cookies['auth_token']

            # Check HTML content for embedded token (if applicable)
            if not self.token and 'text/html' in response.headers.get('Content-Type', ''):
                match = re.search(r'var\s+token\s*=\s*["\']([^"\']+)["\']', response.text)
                if match:
                    self.token = match.group(1)

            if self.token:
                self.log.logging_info(f"Token found: {self.token}")
            else:
                self.log.logging_error("ERROR: Token not found in the expected locations")

            # self.log.logging_info all headers and cookies for inspection
            self.log.logging_info("All response headers:")
            for key, value in response.headers.items():
                self.log.logging_info(f"{key}: {value}")

            self.log.logging_info("All cookies:")
            for cookie in self.session.cookies:
                self.log.logging_info(f"{cookie.name}: {cookie.value}")


            headers = {
                "X-CSRF-Token": self.session.cookies.get("ECP-CSRF-TOKEN"),
                "Content-Type": "application/json"
            }
            # Add the token to the session headers
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

            # Refresh CSRF tokens if needed
            ecp_csrf_token = self.session.cookies.get("ECP-CSRF-TOKEN")
            eecp_csrf_token = self.session.cookies.get("EECP-CSRF-TOKEN")
            headers["X-CSRF-Token"] = ecp_csrf_token
            cookies["EECP-CSRF-TOKEN"] = eecp_csrf_token

            self.headers = headers
            self.body = body

        else:
            self.log.logging_error("Authentication failed")
            self.log.logging_error(f"Response body: {response.text}")


    # Function to invoke GET API call
    def invokeGET(self, sAPI, sPayLoad):

        if self.token:

            self.log.logging_info("*** Step 3: Making an API call with the token")

            endpoint=sAPI
            self.log.logging_info(f"Trying GET API call to: {endpoint}")
            api_url = f"{self.URL}{endpoint}"

            api_response = self.session.get(api_url, headers=self.headers, verify=False)
            self.log.logging_info(f"API response status: {api_response.status_code}")
            self.log.logging_info(f"API response body: {api_response.text}")

            return api_response

    # Function to invoke POST API call
    def invokePOST(self, sAPI, sPayLoad):

        if self.token:

            self.log.logging_info("*** Step 3: Making an API call with the token")

            endpoint=sAPI
            self.log.logging_info(f"Trying POST API call to: {endpoint}")
            api_url = f"{self.URL}{endpoint}"

            # Add the token to the session headers
            # session.headers.update({"Authorization": f"Bearer {self.token}"})

            # log.logging_info({"Authorization": f"Bearer {self.token}"})
            # log.logging_info("api_url = "+api_url)
            # log.logging_info("data payLoad = "+str(sPayLoad))
            # log.logging_info ("headers = "+str(self.headers))

            api_response = self.session.post(api_url, json=self.body, headers=self.headers, cookies=self.session.cookies, data=sPayLoad, verify=False)

            self.log.logging_info(f"API response status: {api_response.status_code}")
            self.log.logging_info(f"API response body: {api_response.text}")

            return api_response
