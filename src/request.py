"""Processes and sends the GitHub Token for authentication in the server."""

import getpass
import os
import requests
import sys
from typing import Dict
from pathlib import Path


class Request:
    """Defining a request class which uses different methods to return different parameters to the server.

    This class handles HTTP requests with authentication to the server API, supporting
    various HTTP methods (GET, POST, PATCH, DELETE, PUT) with consistent authentication
    and error handling.
    """

    def __init__(
        self, method: str, url: str, files={}, data: Dict = {}, headers: Dict = {}
    ):
        """Initialize with request parameters.

        :param method: HTTP method (GET, POST, PATCH, DELETE, UPDATE)
        :param url: API endpoint URL
        :param files: Files to upload, defaults to {}
        :param data: Request data/parameters, defaults to {}
        :param headers: HTTP headers, defaults to {}
        """
        self.method = method
        self.url = url
        self.data = data
        self.headers = headers
        self.files = files
        self.__create_auth_header()

    def __call__(self, raise_error: bool = True) -> requests.Response:
        """Execute HTTP request with specified method and handle response.

        Makes the HTTP request using the appropriate method, handles authentication,
        and manages errors. Updates login status based on response.

        :return: Response object from the request
        :rtype: requests.Response
        :raises SystemExit: If HTTP error occurs
        """
        response: requests.Response = getattr(
            self, f"_Request__{self.method.lower()}"
        )()
        if raise_error:
            try:
                response.raise_for_status()
                # LOGIN IS TRUE
                false_login_file(False)
                return response
            except requests.HTTPError as e:
                if response.status_code == 403:
                    # LOGIN IS FALSE
                    false_login_file(True)
                print(f"Something went wrong: {e}")
                sys.exit(1)
                # workspaces
        else:
            return response

    def __create_auth_header(self):
        """Create authentication headers using GitHub token.

        Retrieves GitHub token and username from environment variables
        and adds them to the request headers.

        :return: None
        :rtype: None
        :raises ValueError: If GitHub token is not found
        """
        token = os.getenv("GITHUB_TOKEN")
        user = os.getenv("GITHUB_USER") or getpass.getuser()

        if not token:
            raise ValueError("GitHub token not found in environment variables")
        # Get GitHub username and add authentication headers
        self.headers["Authorization"] = f"token {token}"
        self.headers["user"] = user

    def __get(self) -> requests.Response:
        """Past the GET request to the server.

        Makes a GET request to the API endpoint with the current directory path
        and passes a url, file, params, and headers.

        :return: If the user is authenticated or if there was a response that wasn't 200
        """
        response = requests.get(
            url=self.url, files=self.files, params=self.data, headers=self.headers
        )
        return response

    def __post(self) -> requests.Response:
        """Past the POST request to the server.

        Makes a POST request to the API endpoint with the current directory path
        and passes a url, file, params, and headers.

        :return: If the user is authenticated or if there was a response that wasn't 200
        """
        response = requests.post(
            self.url, files=self.files, data=self.data, headers=self.headers
        )
        return response

    def __patch(self) -> requests.Response:
        """Past the PATCH request to the server.

        Makes a PATCH request to the API endpoint with the current directory path
        and passes a url, file, params, and headers.

        :return: If the user is authenticated or if there was a response that wasn't 200
        """
        response = requests.patch(
            self.url, files=self.files, data=self.data, headers=self.headers, json={}
        )
        return response

    def __delete(self) -> requests.Response:
        """Past the DELETE request to the server.

        Makes a DELETE request to the API endpoint with the current directory path
        and passes a url, file, params, and headers.

        :return: If the user is authenticated or if there was a response that wasn't 200
        """
        response = requests.delete(
            self.url, files=self.files, params=self.data, headers=self.headers
        )
        return response

    def __update(self) -> requests.Response:
        """Past the UPDATE request to the server.

        Makes a UPDATE request to the API endpoint with the current directory path
        and passes a url, file, params, and headers.

        :return: If the user is authenticated or if there was a response that wasn't 200
        """
        response = requests.put(
            self.url, files=self.files, params=self.data, headers=self.headers
        )
        return response


def false_login_file(should_add: bool = True) -> Path:
    """Calculate repository root path and manage .worldloginfalse file.

    This function finds the root directory of the current Git repository,
    then either creates or removes a file named .worldloginfalse in the parent directory.

    :param should_add: If True, create the file; if False, remove it if it exists
    :type should_add: bool, optional
    :return: Path to the file (whether created or removed)
    :rtype: Path
    """
    try:
        root_dir = os.path.expanduser(
            os.getenv("FILE_SYSTEM") + os.getenv("RepositoryName")
        )
    except TypeError:
        # Find repository root by looking for .git directory
        cwd = os.getcwd()
        root_dir = None
        while cwd != "/":
            path = os.path.join(cwd, ".git")
            if os.path.exists(path):
                root_dir = Path(path).parent.absolute()
                break
            cwd = os.path.dirname(cwd)
    if root_dir:
        # Set path for .worldloginfalse file one directory above repo root
        parent_dir = Path(root_dir).parent
        login_false_file = parent_dir / ".worldloginfalse"

        if should_add:
            # Create empty file
            with open(login_false_file, "w") as f:
                pass
        else:
            # Remove file if it exists
            if login_false_file.exists():
                login_false_file.unlink()

        return login_false_file

    return None
