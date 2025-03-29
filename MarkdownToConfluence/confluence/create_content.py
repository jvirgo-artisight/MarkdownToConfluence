import json
import codecs
import requests
import sys, os
from requests.auth import HTTPBasicAuth

import MarkdownToConfluence.utils.convert_markdown as convert_markdown
import MarkdownToConfluence.confluence.confluence_utils as confluence_utils
from MarkdownToConfluence.utils import get_parent_path_from_child
import MarkdownToConfluence.globals
from MarkdownToConfluence.confluence.create_empty_page import create_empty_page
from MarkdownToConfluence.confluence.upload_attachments import upload_attachment
from MarkdownToConfluence.utils.config import get_config 
from MarkdownToConfluence.confluence import confluence_utils
from MarkdownToConfluence.confluence.confluence_utils import get_page_title_by_id

def create_page(filename: str):
    if os.path.isdir(filename):
        filename = os.path.join(filename, 'index.md')

    config = get_config()
    BASE_URL = config["BASE_URL"]
    AUTH_USERNAME = config["AUTH_USERNAME"]
    AUTH_API_TOKEN = config["AUTH_API_TOKEN"]
    SPACEKEY = config["SPACE_KEY"]
    ROOT = config["FILES_PATH"]
    PARENT_ID = config["PARENT_ID"]
    auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_API_TOKEN)

    MarkdownToConfluence.globals.init()
    page_name, parent_name = convert_markdown.convert(filename, ROOT)
    attachments = MarkdownToConfluence.globals.attachments

    # 🧠 Determine correct parent_id FIRST
    if parent_name:
        if not confluence_utils.page_exists_in_space(parent_name, SPACEKEY, PARENT_ID):
            if 'parent_name' in MarkdownToConfluence.globals.settings and parent_name == MarkdownToConfluence.globals.settings['parent_name']:
                print(f"Parent didn't exist, creating empty parent at root: {parent_name}")
                create_empty_page(parent_name)
            else:
                print(f"Parent didn't exist, creating parent: {parent_name}")
                create_page(get_parent_path_from_child(filename))
        parent_id = confluence_utils.get_page_id(parent_name, SPACEKEY, PARENT_ID)
        parent_display = parent_name
    else:
        parent_id = PARENT_ID
        parent_display = get_page_title_by_id(PARENT_ID)

    # ✅ Check if page exists under correct parent
    if confluence_utils.page_exists_in_space(page_name, SPACEKEY, parent_id):
        print(f"🔁 Page '{page_name}' already exists under correct parent — switching to update")
        from MarkdownToConfluence.confluence.update_content import update_page_content
        update_page_content(filename)
        return

    if confluence_utils.page_exists_in_space(page_name, SPACEKEY):
        print(f"⚠️ Page '{page_name}' already exists in space but not under parent '{parent_display}' — skipping or handling conflict")
        return

    print(f"🆕 Page '{page_name}' not found under parent — creating new page")

    # Page creation template
    template = {
        "version": { "number": 1 },
        "title": page_name,
        "type": "page",
        "space": { "key": SPACEKEY },
        "ancestors": [{ "id": parent_id }],
        "body": {
            "storage": {
                "value": "",
                "representation": "storage"
            }
        }
    }

    # Remove <!DOCTYPE html> from html file
    html_file = filename.replace(".md", ".html")
    with open(html_file, "r") as f:
        lines = f.readlines()
    with open(html_file, "w") as f:
        for line in lines:
            if line.strip("\n") != "<!DOCTYPE html>":
                f.write(line)

    # Load HTML into template
    with codecs.open(html_file, 'r', encoding='utf-8') as f:
        template['body']['storage']['value'] = f.read()

    url = f'{BASE_URL}/wiki/rest/api/content'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'python'
    }

    response = requests.post(url, headers=headers, data=json.dumps(template), auth=auth)

    if response.status_code == 200:
        for attachment in attachments:
            upload_attachment(page_name, attachment[0], attachment[1])
        print(f"✅ Created {page_name} with {parent_display} as parent")
        MarkdownToConfluence.globals.reset()
    else:
        print(f"❌ Error uploading {page_name}. Status code {response.status_code}")
        print(response.text)
        sys.exit(1)

    return response


if __name__ == "__main__":
    create_page(sys.argv[1])
