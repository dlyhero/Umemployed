import json

import requests


def execute_code(script, language, version_index):
    """
    Execute code using JDoodle API.

    Args:
        script (str): The code to execute.
        language (str): The programming language of the code.
        version_index (int): The index of the language version.

    Returns:
        str: Output of the code execution.
    """
    client_id = ""  # client ID
    client_secret = ""  # client Secret

    url = "https://api.jdoodle.com/v1/execute"
    headers = {"Content-Type": "application/json"}

    data = {
        "clientId": client_id,
        "clientSecret": client_secret,
        "script": script,
        "language": language,
        "versionIndex": version_index,
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Error occurred: {e}"
