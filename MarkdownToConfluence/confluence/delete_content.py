import os
import requests
import json
from requests.auth import HTTPBasicAuth

from MarkdownToConfluence.utils.config import get_config
from MarkdownToConfluence.confluence.confluence_utils import get_child_pages_under_parent

def delete_stale_confluence_pages():
    config = get_config()
    BASE_URL = config["BASE_URL"]
    AUTH_USERNAME = config["AUTH_USERNAME"]
    AUTH_API_TOKEN = config["AUTH_API_TOKEN"]
    SPACEKEY = config["SPACE_KEY"]
    FILES_PATH = config["FILES_PATH"]
    PARENT_ID = config["PARENT_ID"]

    auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_API_TOKEN)

    # Step 1: Get current markdown files (without .md extension)
    local_pages = set()
    for root, dirs, files in os.walk(FILES_PATH):
        for file in files:
            if file.endswith(".md"):
                page_title = os.path.splitext(file)[0]
                local_pages.add(page_title)

    # Step 2: Get current Confluence child pages
    confluence_pages = get_child_pages_under_parent(PARENT_ID)
    confluence_titles_to_ids = {page["title"]: page["id"] for page in confluence_pages}

    # Step 3: Find stale pages
    stale_pages = set(confluence_titles_to_ids.keys()) - local_pages

    for title in stale_pages:
        page_id = confluence_titles_to_ids[title]
        print(f"🗑️ Deleting stale page '{title}' (ID: {page_id})")

        url = f"{BASE_URL}/wiki/rest/api/content/{page_id}"
        response = requests.delete(url, auth=auth)

        if response.status_code == 204:
            print(f"✅ Deleted: {title}")
        else:
            print(f"❌ Failed to delete {title} — Status {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    delete_stale_confluence_pages()
