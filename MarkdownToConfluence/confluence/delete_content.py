import requests, json, sys
from requests.auth import HTTPBasicAuth

from MarkdownToConfluence.utils import get_all_page_names_in_filesystem, get_page_name_from_path
import MarkdownToConfluence.confluence.confluence_utils as confluence_utils
from MarkdownToConfluence.confluence.confluence_utils import get_all_pages_in_space
import MarkdownToConfluence.globals
from MarkdownToConfluence.utils.config import get_config  # ✅ central config

config = get_config()

BASE_URL = config["BASE_URL"]
FILES_PATH = config["FILES_PATH"]
SPACE_KEY = config["SPACE_KEY"]
AUTH_USERNAME = config["AUTH_USERNAME"]
AUTH_API_TOKEN = config["AUTH_API_TOKEN"]
PARENT_ID = config["PARENT_ID"]

auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_API_TOKEN)

def delete_page_from_file(filename: str):
    page_name = get_page_name_from_path(filename, FILES_PATH)
    if confluence_utils.page_exists_in_space(page_name, SPACE_KEY, PARENT_ID):
        page_id = confluence_utils.get_page_id(page_name, SPACE_KEY, PARENT_ID)
        return delete_page(page_id)

def delete_page(page_id: str, page_name=""):
    url = f"{BASE_URL}/wiki/rest/api/content/{page_id}"
    headers = { 'User-Agent': 'python' }
    response = requests.delete(url, headers=headers, auth=auth)

    if response.status_code == 204:
        print(f"✅ Deleted page: {page_id} {page_name}")
    else:
        print(f"❌ Error deleting page: {page_id}, status code: {response.status_code}")

    return response

"""
Deletes all pages in Confluence that don't exist in the filesystem.
The `exclude` arg lets you skip deletion for specific page names.
"""
def delete_non_existing_descendants(space_key: str, root: str, exclude=[]):
    MarkdownToConfluence.globals.init()
    settings = MarkdownToConfluence.globals.settings
    if settings and 'parent_name' in settings:
        pages_in_space = confluence_utils.get_all_descendants(settings['parent_page'], space_key)
    else:
        pages_in_space = confluence_utils.get_all_pages_in_space(space_key)

    pages_in_filesystem = get_all_page_names_in_filesystem(root)
    for result in pages_in_space:
        if result['title'] not in pages_in_filesystem and result['title'] not in exclude:
            delete_page(result['id'], result['title'])

def delete_all_pages_in_space(space_key):
    MarkdownToConfluence.globals.init()
    settings = MarkdownToConfluence.globals.settings
    parent_page = settings.get("parent_page", "") if settings else ""

    pages = (
        confluence_utils.get_all_descendants(parent_page, space_key)
        if parent_page else
        get_all_pages_in_space(space_key)
    )

    for page in pages:
        delete_page(page['id'])

if __name__ == "__main__":
    if sys.argv[1] == '--all':
        delete_all_pages_in_space(SPACE_KEY)
    elif sys.argv[1] == '--clean':
        delete_non_existing_descendants(SPACE_KEY, FILES_PATH)
    else:
        delete_page_from_file(sys.argv[1])