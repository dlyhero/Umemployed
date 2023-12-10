import requests
import json

def execute_code(script, language, version_index):
    client_id = "c531a51504fda77d3bd97d4dce3d17b3"  # Replace with your client ID
    client_secret = "fc14913ecdfda745506f613f4a92c807e01395240bd19fc1390d7e2d6a756583"  # Replace with your client Secret

    url = "https://api.jdoodle.com/v1/execute"
    headers = {"Content-Type": "application/json"}

    data = {
        "clientId": client_id,
        "clientSecret": client_secret,
        "script": script,
        "language": language,
        "versionIndex": version_index
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Error occurred: {e}"
