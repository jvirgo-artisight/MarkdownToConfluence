import json, sys
import codecs
import requests
import os
from requests.auth import HTTPBasicAuth
import subprocess

from MarkdownToConfluence.utils import convert_markdown
from MarkdownToConfluence.utils.page_file_info import get_page_name_from_path, get_parent_name_from_path, get_parent_path_from_child
from MarkdownToConfluence.confluence import confluence_utils
from MarkdownToConfluence.confluence.PageNotFoundError import PageNotFoundError
import MarkdownToConfluence.globals
from MarkdownToConfluence.confluence.upload_attachments import upload_attachment
from MarkdownToConfluence.utils.config import get_config
from MarkdownToConfluence.confluence.confluence_utils import get_page_title_by_id

subprocess.run(["python3", "./confluence/create_content.py"], check=True)




def update_page_content(filename: str, old_filename=""):
    config = get_config()
    BASE_URL = config["BASE_URL"]
    AUTH_USERNAME = config["AUTH_USERNAME"]
    AUTH_API_TOKEN = config["AUTH_API_TOKEN"]
    SPACE_KEY = config["SPACE_KEY"]
    ROOT = config["FILES_PATH"]
    PARENT_ID = config["PARENT_ID"]

    auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_API_TOKEN)
    MarkdownToConfluence.globals.init()

    old_page_name = ""
    old_parent_name = ""

    try:
        page_name, parent_name = convert_markdown.convert(filename, ROOT)
        parent_display = get_page_title_by_id(PARENT_ID) if not parent_name else parent_name
    except FileNotFoundError:
        print(f"⚠️ Skipping missing file: {filename}")
        return None

    if old_filename:
        if not os.path.exists(old_filename):
            with open(old_filename, 'w') as old:
                old.write(" ")
            old_page_name = get_page_name_from_path(old_filename, ROOT)
            old_parent_name = get_parent_name_from_path(old_filename, ROOT)
            page_id = confluence_utils.get_page_id(old_page_name, SPACE_KEY, PARENT_ID)
            os.remove(old_filename)
        else:
            old_page_name = get_page_name_from_path(old_filename, ROOT)
            old_parent_name = get_parent_name_from_path(old_filename, ROOT)
            page_id = confluence_utils.get_page_id(old_page_name, SPACE_KEY, PARENT_ID)
    else:
        try:
            page_id = confluence_utils.get_page_id(page_name, SPACE_KEY, PARENT_ID)
        except PageNotFoundError:
            print(f"🆕 Page '{page_name}' not found under parent — creating new page")
            create_page(filename.replace(".html", ".md"))
            return None  # Skip further update since create_page already handles upload


    print(f"🔄 Updating page {page_id} with title {page_name}")

    filename = filename.replace(".md", ".html")
    template = {
        "version": { "number": 0 },
        "title": page_name,
        "type": "page",
        "space": { "key": SPACE_KEY },
        "body": {
            "storage": {
                "value": "",
                "representation": "storage"
            }
        }
    }

    if parent_name:
        if not confluence_utils.page_exists_in_space(parent_name, SPACE_KEY, PARENT_ID):
            if 'parent_name' in MarkdownToConfluence.globals.settings and parent_name == MarkdownToConfluence.globals.settings['parent_name']:
                print(f"📄 Creating missing root parent: {parent_name}")
                create_empty_page(parent_name)
            else:
                print(f"📄 Creating missing parent: {parent_name}")
                create_page(get_parent_path_from_child(filename))

    # Strip <!DOCTYPE html>
    with open(filename, "r") as f:
        lines = f.readlines()
    with open(filename, "w") as f:
        for line in lines:
            if line.strip() != "<!DOCTYPE html>":
                f.write(line)

    with codecs.open(filename, 'r', encoding='utf-8') as f:
        template['body']['storage']['value'] = f.read()

    url = f"{BASE_URL}/wiki/rest/api/content/{page_id}"
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'python'
    }

    if old_parent_name != parent_name and parent_name:
        try:
            new_parent_id = confluence_utils.get_page_id(parent_name, SPACE_KEY, PARENT_ID)
            move_url = f"{BASE_URL}/wiki/rest/api/content/{page_id}/move/append/{new_parent_id}"
            move_response = requests.put(move_url, headers=headers, auth=auth)
            if move_response.status_code == 200:
                print(f"✅ Moved page {page_name} from {old_parent_name} to {parent_name}")
            else:
                print(f"⚠️ Move failed. Status: {move_response.status_code}")
                print(move_response.text)
        except Exception as e:
            print(f"⚠️ Could not move page {page_name}: {str(e)}")


    get_response = requests.get(f"{url}?expand=version", headers=headers, auth=auth)
    version_number = int(get_response.json()['version']['number'])
    template['version']['number'] = version_number + 1

    put_response = requests.put(url, headers=headers, data=json.dumps(template), auth=auth)

    if put_response.status_code == 200:
        for attachment in MarkdownToConfluence.globals.attachments:
            upload_attachment(page_name, attachment[0], attachment[1])
        print(f"✅ Updated page {page_id} with title {page_name}")
        MarkdownToConfluence.globals.reset()
    else:
        print(f"❌ Error uploading {page_name}. Status code {put_response.status_code}")
        print(put_response.text)
        sys.exit(1)

    return put_response

if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            update_page_content(sys.argv[1])
        elif len(sys.argv) == 3:
            update_page_content(sys.argv[1], sys.argv[2])
    except FileNotFoundError as e:
        print(f"⚠️ Skipping missing file: {e}")
        sys.exit(0)
