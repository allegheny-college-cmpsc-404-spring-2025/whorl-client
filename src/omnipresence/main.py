import os
import json
import getpass
import requests
from request import Request

from dotenv import load_dotenv

load_dotenv()

def get(agent_name: str = ""):
  
    """Get current user's presence record from API.

    Makes a GET request to the omnipresence API endpoint to retrieve the
    presence data for the currently authenticated user.

    :return: API response containing user presence data
    :rtype: dict
    :raises requests.exceptions.RequestException: If the API request fails
    """

    response = Request(
        method="GET",
        url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/omnipresence",
        data={"charname": os.getenv("GITHUB_USER") or getpass.getuser()},
    )()
    return response.json()



def post(agent_name: str = ""):
    """Create new presence record for current user.

    Posts a new presence record to the omnipresence API for the currently
    authenticated user with their current status.

    :param None: No parameters required
    :return: Success status of the operation
    :rtype: bool
    :raises requests.exceptions.RequestException: If the API request fails
    """

    response = Request(
        method="POST",
        url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/omnipresence/",
        data={
            "username": os.getenv("GITHUB_USER") or getpass.getuser(),
            "charname": os.getenv("GITHUB_USER") or getpass.getuser(),
            "working_dir": os.getcwd(),
        },
    )()
    
    if response.status_code == 201:
        return True
    return False

def patch(agent_name: str = "", data: dict = {}):
    """Update existing presence record.

    Updates an existing presence record in the omnipresence API with new data
    including the current working directory.

    :param data: Record data containing pk and charname
    :type data: dict
    :return: True if update successful, False otherwise
    :rtype: bool
    :raises requests.exceptions.RequestException: If API request fails
    :raises KeyError: If required data fields missing
    """
    response = Request(
        method="PATCH",
        url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/omnipresence/update/{data['pk']}/",
        data={
            "charname": data["charname"],
            "working_dir": os.getcwd(),
            "partial": True,
        },
    )()
    if response.status_code == 200:
        return True
    return False

def report(agent_name: str = ""):
    """Update existing record or create new one.

    Gets current presence data and either updates existing record
    or creates new record if none exists.

    :return: None
    :rtype: None
    :raises requests.exceptions.RequestException: If API requests fail
    """
    data = get(agent_name)
    data = get()
    if len(data) == 1:
        patch(agent_name, data[0])
    if len(data) == 0:
        post(agent_name)
