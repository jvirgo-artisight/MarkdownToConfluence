import os

def get_config():
    return {
        "BASE_URL": os.environ.get("INPUT_CONFLUENCE_URL"),
        "AUTH_USERNAME": os.environ.get("INPUT_AUTH_USERNAME"),
        "AUTH_API_TOKEN": os.environ.get("INPUT_AUTH_API_TOKEN"),
        "SPACE_KEY": os.environ.get("INPUT_CONFLUENCE_SPACE_KEY"),
        "FILES_PATH": os.environ.get("INPUT_FILESLOCATION", "docs"),
        "PARENT_ID": os.environ.get("INPUT_PARENT_ID") or None
        "SHOULD_UPLOAD": os.environ.get("INPUT_SHOULD_UPLOAD") == "true"
    }
