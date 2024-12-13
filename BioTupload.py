"""
BioTupload.py
Author: Onalabs Engineer Team
Description: Tool to upload Onalab's devices to BioT and add them to an existing organization with a registration code to identify them.
Copyright (c) 2024 Onalabs.
All rights reserved.
"""

# Library Imports
import argparse
import json
import os
from datetime import datetime
import requests
import time


# Constants/Global Variables
DATE = datetime.now().strftime("%y%m%d")
SERIAL_NUMBER_LENGTH_ONASPORT = 10 # Length of the serial number (Onasport) in characters
MIN_SERIAL_NUMBER_ONASPORT = 1000000000 # Minimum value for a 10-digit serial number (Onasport)
MAX_SERIAL_NUMBER_ONASPORT = 9999999999 # Maximum value for a 10-digit serial number (Onasport)
ORGANIZATIONS_DIC = {}
EXECUTION_STATUS = 0 # Execution status of the flashing tool: 0 for success, other for failure
URL_DEV = "https://api.dev.onalabs.biot-med.com"
URL_PROD = "https://api.onalabs.biot-med.com"


# Functions

######################################################################################################
# Common file and directory operations
######################################################################################################
def format_filename(data):
    """
    Formats a filename based on the given data.

    The filename is formatted as "{SerialNumber}_{date}.json", 
    where "{SerialNumber}" is a value from the 'data' dictionary, 
    "{date}" is the current date in the format YYmmdd.

    Args:
        data (dict): A dictionary containing the data for the filename. 
                     It should have a key 'SerialNumber'.

    Returns:
        str: The formatted filename.
    """
    global EXECUTION_STATUS
    try:
        return f"{data.get('SerialNumber','No_Serial_Number_Available')}_{DATE}.json"
    except Exception as e:
        EXECUTION_STATUS = 1
        return None


######################################################################################################
# JSON file operations
######################################################################################################
def log_to_json(data, filepath):
    """
    Appends a dictionary of data to a JSON file at a specific filepath.

    This function opens the specified file in append mode and writes the data to it as a new JSON object. 
    If the file or its parent directory does not exist, they will be created. Each JSON object is written on a new line.

    Args:
        data (dict): A dictionary of values to be written to the file as a new JSON object.
        filepath (str): The path to the JSON file to which the data should be written.
    """
    global EXECUTION_STATUS
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'a') as file:
            json.dump(data, file)
            file.write('\n')
    except Exception as e:
        EXECUTION_STATUS = 2

def manage_data_json(data, filepath):
    """
    This function generates a json file from given data.

    Parameters:
    data (dict): A dictionary containing the data to be written to the json file.
    filepath (str): The path where the json file will be created.
    flash_status (dict): A dictionary containing the status of various flash actions.

    Returns:
    None
    """
    global EXECUTION_STATUS
    try:
        filename = format_filename(data)
        filepath = os.path.join(filepath, filename)
        generate_json(data, filepath)
        return filepath
    except Exception as e:
        EXECUTION_STATUS = 3
        return None

def generate_json(data, filepath):
    """
    This function generates a json file from given data.

    Parameters:
    data (dict): A dictionary containing the data to be written to the CSV file.
    filepath (str): The path where the json file will be created.

    Returns:
    None
    """
    global EXECUTION_STATUS
    try:
        content = {
        "serialNumber": data.get('SerialNumber'),
        "outputExecutionResult": EXECUTION_STATUS,
        }
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=4)
    except Exception as e:
        EXECUTION_STATUS = 4

######################################################################################################
# Argument Parsing
######################################################################################################
def check_serial_number(serial_number):
    """
    Check if the serial number is valid.

    This function checks if the serial number is a valid string of the corresponding length.

    Args:
        serial_number: The serial number to be checked.

    Raises:
        argparse.ArgumentTypeError: If the serial number is not valid.

    Returns:
        str: The serial number if it is valid.
    """
    global EXECUTION_STATUS
    if (not serial_number.isdigit()) or (len(serial_number) != SERIAL_NUMBER_LENGTH_ONASPORT) or (int(serial_number) < MIN_SERIAL_NUMBER_ONASPORT) or (int(serial_number) > MAX_SERIAL_NUMBER_ONASPORT):
        EXECUTION_STATUS = 5
    return serial_number

def parse_arguments():
    """
    Creates and configures an ArgumentParser object for the Tool.

    The parser is configured with various arguments for the upload and configuration process.
    Each argument is added with a short and long form (e.g., "-env" and "--Environment"), 
    a help message, whether it's required, and a type.

    The function then parses the command-line arguments and returns the resulting Namespace object.

    Returns:
        argparse.Namespace: The Namespace object resulting from parsing the command-line arguments. 
        This object has an attribute for each argument added to the parser, where the value of the 
        attribute is the value of the corresponding command-line argument.
    """
    global EXECUTION_STATUS
    try:

        # Create a temporary parser for the Device argument
        temp_parser = argparse.ArgumentParser(add_help=False)
        temp_args, unknown = temp_parser.parse_known_args()

        # Create the parser class
        # parser = argparse.ArgumentParser(prog= "ONASPORT upload BioT tool", description = "Upload Onalab's devices to BioT and add them to an existing organization with a registration code to identify them",
        #                                 epilog="Example: python BioTupload.py -env 'production' -user 'c.arechaga@onalabs.com' -password 'Carmen123.' -sn '1234567891' -org 'Tri-excellence.com' -rc '2099BFF6-6648-4AAE-B43F-D9907A0731120' -description 'ONAS0000' -version '2.0.0' -output 'C:\Users\Usuari\OS\PROD\shipping'")
        parser = argparse.ArgumentParser(prog= "ONASPORT upload BioT tool", description = "Upload Onalab's devices to BioT and add them to an existing organization with a registration code to identify them")
        # Add the arguments
        parser.add_argument("-env", "--Environment", choices=["production", "development"], help="Environment in BioT. Selectable values: 'production' (for Production), 'development' (for Development)", required=True, type=str)
        parser.add_argument("-user", "--Username", help="Username to log into BioT for the corresponding environment.", required=True, type=str)
        parser.add_argument("-password", "--Password", help="Password to log into BioT for the corresponding environment.", required=True, type=str)
        parser.add_argument("-sn", "--SerialNumber", help="Serial Number of the device on which the tool operates.", type=lambda s: check_serial_number(s), required=True)
        parser.add_argument("-org", "--Organization", help="Organization to which the device will be assigned.", required=True, type=str)
        parser.add_argument("-rc", "--RegistrationCode", help="Registration Code to which the device will be assigned.", required=True, type=str)
        parser.add_argument("-description", "--Description", help="Advertising name of the device that will appear as a description in BioT.", required=True, type=str)
        parser.add_argument("-version", "--Version", help="Version of the ONASPORT device.", required=True, type=str)
        parser.add_argument("-output", "--OutputDirectory", help="Directory where the traceability file is stored after completion.", default=None, type=str)

        # Parse the arguments - Create parsed object
        args = parser.parse_args()

        return args
    
    except Exception as e:
        EXECUTION_STATUS = 6
        return None

def parsed_object_to_dict(parsed_object):
    """
    Converts the parsed object to a dictionary.

    The function takes the parsed object resulting from parsing the command-line arguments and 
    converts it to a dictionary. The dictionary has the argument names as the keys and the argument 
    values as the values.

    Args:
        parsed_object (argparse.Namespace): The Namespace object resulting from parsing the command-line arguments.

    Returns:
        dict: A dictionary where the keys are the argument names and the values are the argument values.
    """
    global EXECUTION_STATUS
    try:
        parsed_dict = vars(parsed_object)

        return parsed_dict
    
    except Exception as e:
        EXECUTION_STATUS = 7
        return None


######################################################################################################
# Upload Functions (API Commands)
######################################################################################################

def get_api_call(url, header):
    """
    This is a generic function used whenever you want to interact with an API using the GET method, which means retrieving information from the platform.

    Args:
        None

    Returns:
        None
    """
    global EXECUTION_STATUS
    try:
        response_get = requests.get(url, headers=header)
        response_get.raise_for_status()
        return response_get
    except Exception as e:
        EXECUTION_STATUS = 8
        return None

def post_api_call(url, header, data):
    """
    This is a generic function used whenever you want to interact with an API using the POST method, which means sending information to the platform.

    Args:
        None

    Returns:
        None
    """
    global EXECUTION_STATUS
    try:
        response_post = requests.post(url, data=data, headers=header)
        response_post.raise_for_status()
        return response_post
    except Exception as e:
        EXECUTION_STATUS = 9
        return None

def define_apis(username, password, environment):
    """
    Creates URLs to interact with the necessary APIs.

    The function first chooses the environment in BioT which will interact with. 
    It then uses the given base URLs and credentials to configure the URLs that will interact with the APIs to:
        - Log in.
        - Post a Registration Code.
        - Get a list of organizations available.
        - Get a template of a Registration Code.
        - Get a template of a ONASPORT device.
        - Post an ONASPORT device.

    Args:
        username: The username from the command-line arguments.
        password: The password from the command-line arguments.
        environment: The environment from the command-line arguments.

    Returns:
        None
    """
    global EXECUTION_STATUS, URL_DEV, URL_PROD
    global headers_login, payload, api_login, api_post_registration_code, api_get_organizations, api_get_template_registration_code, api_get_template_onasport_device, api_post_onasport_device
    try:
        if environment=='development':
            base_url = URL_DEV
        elif environment=='production':
            base_url = URL_PROD
        headers_login = {'content-type': "application/json"}
        payload = {"username": username, "password": password}
        api_login = "%s/ums/v2/users/login" % (base_url)
        api_post_registration_code = "{}/organization/v1/registration-codes".format(base_url)
        api_get_organizations = "{}/organization/v1/organizations?searchRequest=%7B%22limit%22%3A30%2C%22filter%22%3A%7B%7D%2C%22freeTextSearch%22%3A%22%22%7D".format(base_url)
        api_get_template_registration_code = "{}/settings/v1/templates/minimized?searchRequest=%7B%22filter%22%3A%7B%22entityTypeName%22%3A%7B%22in%22%3A%5B%22registration-code%22%5D%7D%7D%2C%22limit%22%3A1000%7D".format(base_url)
        api_get_template_onasport_device = "{}/settings/v1/portal-builder/MANUFACTURER_PORTAL/views-full-info/TEMPLATE_EXPAND?entityTypeName=device&templateId=0acb3d5b-c70b-4101-b8f7-be17c452fbc5".format(base_url)
        api_post_onasport_device = "{}/device/v2/devices".format(base_url)
        signin()
    except Exception as e:
        print(e)
        EXECUTION_STATUS = 10
        return None

def signin():
    """
    Logs into the system (BioT) in the environment that was chosen. To do so, it first sends a request to log in with the credentials mentioned before. 
    The response is a token that will serve for the other interactions with APIs.

    Args:
        None

    Returns:
        None
    """
    global EXECUTION_STATUS
    global api_login, payload, headers_login, headers_apis
    try:
        response = requests.post(api_login, json=payload, headers=headers_login)
        response.raise_for_status()
        response_json = response.json()
        token_authorization = response_json["accessJwt"]["token"]
        headers_apis = {'content-type': "application/json", "Authorization": "Bearer %s" % (token_authorization)}
        get_organizations()
    except requests.exceptions.RequestException as e:
        EXECUTION_STATUS = 11
        return None

def get_organizations():
    """
    Gets a list of the organizations available. These organizations are then saved as a json format.
    
    Args:
        None

    Returns:
        None
    """
    global EXECUTION_STATUS
    global response_list_organizations, api_get_organizations, headers_apis, response_json_list_organizations
    try:
        response_list_organizations = get_api_call(api_get_organizations, headers_apis)
        response_json_list_organizations = json.loads((response_list_organizations.content).decode("utf-8"))
        registration_id()
    except requests.exceptions.RequestException as e:
        EXECUTION_STATUS = 12
        return None

def registration_id():
    """
    Retrieves a list of the templates related to Registration Codes and then chooses the first one.
    
    Args:
        None

    Returns:
        None
    """
    global EXECUTION_STATUS
    global template_id_registration_code, response_template_registration_code, api_get_template_registration_code, headers_apis, response_json_template_registration_code 
    try:
        response_template_registration_code = get_api_call(api_get_template_registration_code, headers_apis)
        response_json_template_registration_code = json.loads((response_template_registration_code.content).decode("utf-8"))
        template_id_registration_code = response_json_template_registration_code['data'][0]['id']
        template_id()
    except requests.exceptions.RequestException as e:
        EXECUTION_STATUS = 13
        return None

def template_id():
    """
    Retrieves a list of templates related to ONASPORT devices and selects the one that matches the ID corresponding to the organization where it will be assigned. 

    Args:
        None

    Returns:
        None
    """
    global EXECUTION_STATUS, ORGANIZATIONS_DIC, data
    global response_onasport_id_template, api_get_template_onasport_device, headers_apis, response_json_onasport_id_template, onasport_device_template_id, response_json_list_organizations
    try:
        response_onasport_id_template = get_api_call(api_get_template_onasport_device, headers_apis)
        response_json_onasport_id_template = json.loads((response_onasport_id_template.content).decode("utf-8"))
        onasport_device_template_id = response_json_onasport_id_template['template']['id']
        for organization in response_json_list_organizations['data']:
            ORGANIZATIONS_DIC[organization["_name"]] = organization["_id"]
        add_device(data)
    except requests.exceptions.RequestException as e:
        EXECUTION_STATUS = 14
        return None
    
def add_device(data):
    """
    Posts the Registration Code along with all the required data. It then receives a response containing the ID assigned to the Registration Code.
    This ID is subsequently used to post the device, assign it to the organization, and link it to the recently posted Registration Code.
    
    Args:
        None

    Returns:
        None
    """
    global EXECUTION_STATUS, ORGANIZATIONS_DIC
    global data_registration_code, response_post_registration_code, template_id_registration_code, api_post_registration_code, headers_apis, response_json_registration_code, registration_code_id, data_device, onasport_device_template_id, response_post_device, api_post_onasport_device
    try:
        data_registration_code = json.dumps({"_ownerOrganization": {"id": ORGANIZATIONS_DIC.get(data.get('Organization'))},"_code": data.get('RegistrationCode'),"_templateId": template_id_registration_code})
        response_post_registration_code = post_api_call(api_post_registration_code, headers_apis, data_registration_code)
        response_json_registration_code = json.loads((response_post_registration_code.content).decode("utf-8"))
        registration_code_id = response_json_registration_code['_id']
        time.sleep(1)
        data_device = json.dumps({"_ownerOrganization": {"id": ORGANIZATIONS_DIC.get(data.get('Organization'))}, "_registrationCode": {"id": registration_code_id},"_id": data.get('SerialNumber'),"_description": data.get('Description'),"device_version": data.get('Version'),"_templateId": onasport_device_template_id})
        response_post_device = post_api_call(api_post_onasport_device, headers_apis, data_device)
    except requests.exceptions.RequestException as e:
        EXECUTION_STATUS = 15
        return None


######################################################################################################
# Main flow functions (TOP LEVEL)
######################################################################################################
def main():
    """
    Entry point of the script.

    This function parses command-line arguments, converts the parsed object to a dictionary, 
    and then manages the data (and actions), storing it in the Traceability file.

    """
    global EXECUTION_STATUS, data
    try:
        # Create the parsed object and convert it to a dictionary
        data = parsed_object_to_dict(parse_arguments())
        output_directory = data.get('OutputDirectory')
        if EXECUTION_STATUS == 0:
            # Upload device
            define_apis(data.get('Username'), data.get('Password'), data.get('Environment'))
        # Store the data in the Traceability file and print it to the terminal
        path_to_print = manage_data_json(data, output_directory)
        return path_to_print

    except Exception as e:
        EXECUTION_STATUS = 16
        path_to_print = manage_data_json(data, output_directory)
        return path_to_print

######################################################################################################
# Main function call
######################################################################################################
if __name__ == "__main__":
    print(main())
