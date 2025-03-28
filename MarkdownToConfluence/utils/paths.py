import os
from posixpath import dirname
from MarkdownToConfluence.utils.config import get_config  # ✅ centralized config

config = get_config()

def get_abs_path_from_relative(relative_path: str, source_path: str, root=""):
    if root == "":
        root = config["FILES_PATH"]
    _root = os.path.abspath(root)

    if os.path.isfile(source_path):
        source_path = dirname(source_path)

    relative_path = relative_path.strip()
    source_path = source_path.strip()

    if os.path.exists(os.path.realpath(os.path.join(source_path, relative_path).strip())):
        abs_path = os.path.join(source_path, relative_path).strip()
    elif os.path.isabs(relative_path):
        if os.fspath(relative_path).startswith(os.getcwd()):
            abs_path = relative_path
        else:
            abs_path = os.path.join(_root, relative_path)
    else:
        abs_path = os.path.abspath(relative_path)

    return os.path.realpath(abs_path)

# Example (if testing directly):
# print(get_abs_path_from_relative('./zip_test.zip', os.path.abspath('./documentation/page 3/index.md'), './documentation'))
