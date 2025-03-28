import os
from posixpath import basename, dirname
import MarkdownToConfluence.globals

# Returns "" if path == root or file does not exist
def get_prefix(path: str, root: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if not os.path.exists(root):
        raise FileNotFoundError(root)
    if path == root:
        return ""

    if os.path.isfile(path):
        dir_path = os.path.dirname(path)
    else:
        dir_path = path

    if path.endswith("index.md") and "prefix.txt" in os.listdir(dirname(path)):
        return ""
    if path.endswith("index.md") and dirname(path) == root:
        return ""
    if not os.path.isdir(dir_path):
        return ""

    while "prefix.txt" not in os.listdir(dir_path):
        dir_path = os.path.dirname(dir_path)
        if dir_path in [root, "", os.sep]:
            return ""
    try:
        with open(f"{dir_path}/prefix.txt", 'r') as f:
            return f.readline().strip()
    except Exception:
        return ""

def get_page_name_from_path(path: str, root: str):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if path == root:
        return ""

    if os.path.isdir(path):  # Assume index.md if path is dir
        path = os.path.join(path, "index.md")

    page_name = get_prefix(path, root)
    file_name = basename(path)
    parts = path.split('/')

    if file_name == "index.md":
        page_name += parts[-2] if len(parts) >= 2 else "index"
    else:
        page_name += os.path.splitext(file_name)[0]  # ✅ Correctly strip ".md"

    return page_name

def get_parent_name_from_path(path: str, root: str, default=""):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if path == root:
        return ""

    settings = MarkdownToConfluence.globals.settings
    if settings and "parent_page" in settings:
        default = settings["parent_page"]

    if os.path.isdir(path):  # Assume index.md if path is dir
        path = os.path.join(path, "index.md")

    file_name = basename(path)

    if file_name == "index.md":
        parent_path = dirname(dirname(path))
    else:
        parent_path = dirname(path)

    if os.path.exists(parent_path) and parent_path != root:
        try:
            return get_page_name_from_path(parent_path, root)
        except FileNotFoundError:
            return default
    return default

def get_all_md_paths(root: str):
    paths = []
    def traverse(directory):
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if os.path.isdir(f):
                traverse(f)
            elif f.endswith('.md'):
                paths.append(f)
    traverse(root)
    return paths

def get_all_page_names_in_filesystem(root: str):
    page_names = []
    for path in get_all_md_paths(root):
        try:
            name = get_page_name_from_path(path, root)
            page_names.append(name)
        except FileNotFoundError:
            continue
    return page_names

def get_parent_path_from_child(child_path: str):
    if basename(child_path).strip() != "index.md":
        return dirname(child_path)
    else:
        return dirname(dirname(child_path))
