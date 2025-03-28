from urllib.parse import quote
import requests, json
from requests.auth import HTTPBasicAuth
from MarkdownToConfluence.confluence.PageNotFoundError import PageNotFoundError
from MarkdownToConfluence.utils.config import get_config  # ✅ centralized config

config = get_config()
BASE_URL = config["BASE_URL"]
AUTH_USERNAME = config["AUTH_USERNAME"]
AUTH_API_TOKEN = config["AUTH_API_TOKEN"]

auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_API_TOKEN)

def page_exists_in_space(title: str, spaceKey: str, parent_id: str = None) -> bool:
    url = f"{BASE_URL}/wiki/rest/api/content?spaceKey={spaceKey}&title={quote(title)}"
    if parent_id:
        url += f"&ancestors={parent_id}"

    headers = { 'User-Agent': 'python' }
    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code == 200:
        return len(response.json().get("results", [])) > 0
    print(response.text)
    return False


def get_page_id(title: str, spaceKey: str, parent_id: str = None) -> str:
    url = f"{BASE_URL}/wiki/rest/api/content?spaceKey={spaceKey}&title={quote(title)}"
    if parent_id:
        url += f"&ancestors={parent_id}"  # ✅ limit search to children of parent_id

    headers = { 'User-Agent': 'python' }
    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0]["id"]
        raise PageNotFoundError(title, spaceKey)
    print(response.text)
    raise PageNotFoundError(title, spaceKey)


def get_all_descendants(parent_page: str, space_key: str):
    if page_exists_in_space(parent_page, space_key):
        page_id = get_page_id(parent_page, space_key)
        url = f"{BASE_URL}/wiki/rest/api/content/{page_id}/descendant/page"
        headers = { 'User-Agent': 'python' }

        results = []
        response = requests.get(url, headers=headers, auth=auth)
        if response.status_code == 200:
            response_json = response.json()
            results.extend(response_json.get("results", []))
            while "next" in response_json.get("_links", {}):
                next_url = response_json["_links"]["base"] + response_json["_links"]["next"]
                response = requests.get(next_url, headers=headers, auth=auth)
                if response.status_code == 200:
                    response_json = response.json()
                    results.extend(response_json.get("results", []))
                else:
                    break
        else:
            print(response)
        return results
    raise PageNotFoundError(parent_page, space_key)

def get_all_pages_in_space(space_key: str):
    url = f"{BASE_URL}/wiki/rest/api/content?spaceKey={space_key}"
    headers = { 'User-Agent': 'python' }

    results = []
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        response_json = response.json()
        results.extend(response_json.get("results", []))
        while "next" in response_json.get("_links", {}):
            url = BASE_URL + '/wiki' + response_json["_links"]["next"]
            response = requests.get(url, headers=headers, auth=auth)
            if response.status_code == 200:
                response_json = response.json()
                results.extend(response_json.get("results", []))
            else:
                break
    else:
        print(response)
    return results
