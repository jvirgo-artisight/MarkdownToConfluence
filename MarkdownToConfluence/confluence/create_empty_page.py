import json
import requests
from requests.auth import HTTPBasicAuth

import MarkdownToConfluence.confluence.confluence_utils as confluence_utils
from MarkdownToConfluence.utils.config import get_config  # ✅ Central config

config = get_config()
BASE_URL = config["BASE_URL"]
AUTH_USERNAME = config["AUTH_USERNAME"]
AUTH_API_TOKEN = config["AUTH_API_TOKEN"]
SPACEKEY = config["SPACE_KEY"]
PARENT_ID = config["PARENT_ID"]

auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_API_TOKEN)

def create_empty_page(page_name: str):
    if confluence_utils.page_exists_in_space(confluence_utils.get_page_id(page_name, SPACEKEY, PARENT_ID)):
        return "Page already exists"

    template = {
        "version": { "number": 1 },
        "title": page_name,
        "type": "page",
        "space": { "key": SPACEKEY }
    }

    url = f'{BASE_URL}/wiki/rest/api/content'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'python'
    }

    response = requests.post(url, headers=headers, data=json.dumps(template), auth=auth)

    if response.status_code == 200:
        print(f"✅ Created empty page: {page_name}")
    else:
        print(f"❌ Failed to create empty page '{page_name}'. Status code: {response.status_code}")
        print(response.text)

    return response
