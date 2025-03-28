import requests, json, os
from .confluence_utils import page_exists_in_space, get_page_id
from .PageNotFoundError import PageNotFoundError
from requests.auth import HTTPBasicAuth
from MarkdownToConfluence.utils.config import get_config  # ✅ Use centralized config

config = get_config()
BASE_URL = config["BASE_URL"]
SPACEKEY = config["SPACE_KEY"]
AUTH_USERNAME = config["AUTH_USERNAME"]
AUTH_API_TOKEN = config["AUTH_API_TOKEN"]

auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_API_TOKEN)

headers = {
    'User-Agent': 'python',
    'X-Atlassian-Token': 'no-check'
}

def upload_attachment(page_title, attachment_name, filepath):
    if page_exists_in_space(page_title, SPACEKEY):
        url = f"{BASE_URL}/wiki/rest/api/content/{get_page_id(page_title, SPACEKEY)}/child/attachment"

        # Get existing attachment ID if it exists
        attachment_id = ""
        attachments = requests.get(url, headers=headers, auth=auth)
        for result in attachments.json().get('results', []):
            if result['title'] == attachment_name:
                attachment_id = result['id']

        with open(filepath, 'rb') as file_data:
            files = {'file': (attachment_name, file_data)}

            if not attachment_id:
                response = requests.post(url, headers=headers, files=files, auth=auth)
            else:
                response = requests.post(f'{url}/{attachment_id}/data', headers=headers, files=files, auth=auth)

        if response.status_code == 200:
            print(f"📎 Uploaded {attachment_name} to page: {page_title}")
        else:
            print(f"❌ Failed to upload {attachment_name} to page {page_title}. Status Code: {response.status_code}")
        return response
    else:
        raise PageNotFoundError(page_title, SPACEKEY)
