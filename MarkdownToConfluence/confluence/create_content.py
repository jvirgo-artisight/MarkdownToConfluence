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
    parent_display = get_page_title_by_id(PARENT_ID) if not parent_name else parent_name
    attachments = MarkdownToConfluence.globals.attachments

    if confluence_utils.page_exists_in_space(page_name, SPACEKEY, PARENT_ID):
        return "Page already exists"

    print(f"Creating {page_name} with {parent_name} as parent")

    template = {
        "version": { "number": 1 },
        "title": page_name,
        "type": "page",
        "space": { "key": SPACEKEY },
        "body": {
            "storage": {
                "value": "",
                "representation": "storage"
            }
        }
    }

    if parent_name:
        if not confluence_utils.page_exists_in_space(parent_name, SPACEKEY, PARENT_ID):
            if 'parent_name' in MarkdownToConfluence.globals.settings and parent_name == MarkdownToConfluence.globals.settings['parent_name']:
                print(f"Parent didn't exist, creating empty parent at root: {parent_name}")
                create_empty_page(parent_name)
            else:
                print(f"Parent didn't exist, creating parent: {parent_name}")
                create_page(get_parent_path_from_child(filename))

        parent_page_id = confluence_utils.get_page_id(parent_name, SPACEKEY, PARENT_ID)
        template['ancestors'] = [{ "id": parent_page_id }]
    else:
        # 🚨 This is the missing piece
        # No parent_name set, but we have a configured parent_id
        if PARENT_ID:
            print(f"Assigning top-level ancestor using configured PARENT_ID: {PARENT_ID}")
            template['ancestors'] = [{ "id": PARENT_ID }]


    html_file = filename.replace(".md", ".html")

    # Remove <!DOCTYPE html> from html file
    with open(html_file, "r") as f:
        lines = f.readlines()
    with open(html_file, "w") as f:
        for line in lines:
            if line.strip("\n") != "<!DOCTYPE html>":
                f.write(line)

    # Load html into template
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
