import requests, json, shutil, time
import os
from urllib.parse import quote
from requests.auth import HTTPBasicAuth
from MarkdownToConfluence.utils.config import get_config

config = get_config()

SPACE_KEY = config["SPACE_KEY"]
BASE_URL = config["BASE_URL"]
AUTH_USERNAME = config["AUTH_USERNAME"]
AUTH_API_TOKEN = config["AUTH_API_TOKEN"]
DOCS_FOLDER_NAME = config.get("FILES_PATH", "docs")
PARENT_ID = config.get("PARENT_ID")

auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_API_TOKEN)


def get_all_pages_in_space(space_key: str):
    url = f"{BASE_URL}/wiki/rest/api/content?spaceKey={space_key}"
    headers = { 'User-Agent': 'python' }

    results = []
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        response_json = response.json()
        results.extend(response_json['results'])
        while "next" in response_json.get('_links', {}):
            url = BASE_URL + '/wiki' + response_json["_links"]["next"]
            response = requests.get(url, headers=headers, auth=auth)
            if response.status_code == 200:
                response_json = response.json()
                results.extend(response_json['results'])
            else:
                break
    else:
        print(response)
    return [s['title'] for s in results]


def get_all_descendants_in_page(pageID: str):
    url = f"{BASE_URL}/wiki/rest/api/content/{pageID}/descendant/page?limit=9999"
    headers = { 'User-Agent': 'python' }

    results = []
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        response_json = response.json()
        results.extend(response_json['results'])
        while "next" in response_json.get('_links', {}):
            url = BASE_URL + '/wiki' + response_json["_links"]["next"]
            response = requests.get(url, headers=headers, auth=auth)
            if response.status_code == 200:
                response_json = response.json()
                results.extend(response_json['results'])
            else:
                break
    else:
        print(response)
    return [s['title'] for s in results]


def getChildren(pageId: str):
    url = f"{BASE_URL}/wiki/rest/api/content/{pageId}/child/page"
    headers = { 'User-Agent': 'python' }

    results = []
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        response_json = response.json()
        results.extend(response_json['results'])
        while "next" in response_json.get('_links', {}):
            url = response_json["_links"]["base"] + response_json["_links"]["next"]
            response = requests.get(url, headers=headers, auth=auth)
            if response.status_code == 200:
                response_json = response.json()
                results.extend(response_json['results'])
            else:
                break
    else:
        print(response)

    return results


def findPath(folder: str, dirname: str):
    for root, dirs, files in os.walk(os.path.abspath(folder)):
        for name in dirs:
            if name == dirname:
                return os.path.abspath(os.path.join(root, name))


def checkIfFolderExist():
    global DOCS_FOLDER_NAME
    if not os.path.exists(DOCS_FOLDER_NAME):
        os.makedirs(DOCS_FOLDER_NAME)


def createPages(pages: list):
    for page in pages:
        safe_page = pathReplacer(page)
        page_path = f"{DOCS_FOLDER_NAME}/{safe_page}"
        os.makedirs(page_path, exist_ok=True)
        with open(f"{page_path}/index.md", 'w') as f:
            f.write("")  # empty placeholder


def sortPages(pages: list):
    for page in pages:
        page_id = get_page_id(page, SPACE_KEY, PARENT_ID)
        safe_page = pathReplacer(page)
        for child in getChildren(page_id):
            child_name = pathReplacer(child['title'])
            print(f"Moving {child_name} → {safe_page}")
            child_path = findPath(DOCS_FOLDER_NAME, child_name)
            parent_path = findPath(DOCS_FOLDER_NAME, safe_page)
            if child_path and parent_path:
                shutil.move(child_path, parent_path)


def get_page_id(title: str, space_key: str, parent_id: str = None) -> str:
    url = f"{BASE_URL}/wiki/rest/api/content?spaceKey={space_key}&title={quote(title)}"
    if parent_id:
        url += f"&ancestors={parent_id}"
    headers = { 'User-Agent': 'python' }
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]['id']
        else:
            raise Exception(f"Page not found: {title}")
    raise Exception(f"Error looking up page: {title} → {response.status_code}")


def pathReplacer(page: str):
    page = page.replace('"', "'").replace("*", "").replace("\\", "")
    page = page.replace("?", "").replace("<", "").replace(">", "")
    page = page.replace("|", "").replace(":", "")
    if page.endswith("."):
        page = page[:-1]
    return page.replace("/", "%")


# ---- Main Runner ----

if __name__ == "__main__":
    start = time.time()

    checkIfFolderExist()

    if PARENT_ID:
        pages = get_all_descendants_in_page(PARENT_ID)
    else:
        pages = get_all_pages_in_space(SPACE_KEY)

    createPages(pages)
    sortPages(pages)

    end = time.time()
    print("✅ Markdown folder structure complete.")
    print(f"⏱️ Time taken: {(end - start) / 60:.2f} minutes")
