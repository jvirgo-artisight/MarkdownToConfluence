import os
import re
import hashlib
from atlassian import Confluence
from MarkdownToConfluence.utils.config import get_config

# Load config from environment (GitHub Actions inputs)
config = get_config()

BASE_URL = config["BASE_URL"]
AUTH_USERNAME = config["AUTH_USERNAME"]
AUTH_API_TOKEN = config["AUTH_API_TOKEN"]
SPACE_KEY = config["SPACE_KEY"]
FILES_PATH = config["FILES_PATH"]
PARENT_ID = config["PARENT_ID"]

confluence = Confluence(
    url=BASE_URL,
    username=AUTH_USERNAME,
    password=AUTH_API_TOKEN
)

def read_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_images(md_content):
    return re.findall(r'!\[.*?\]\((.*?)\)', md_content)

def upload_images(page_id, image_paths, base_path):
    for rel_path in image_paths:
        abs_path = os.path.join(base_path, rel_path)
        if os.path.exists(abs_path):
            confluence.attach_file(abs_path, page_id)

def sync_page(title, parent_id, content):
    # Get children under the parent and match by title
    children = confluence.get_child_pages(parent_id)
    for child in children:
        if child['title'] == title:
            print(f"🔄 Updating existing page: {title} (ID: {child['id']})")
            confluence.update_page(child['id'], title, content)
            return child['id']

    # If not found, create the page under the parent
    print(f"🆕 Creating new page: {title} under parent ID {parent_id}")
    new_page = confluence.create_page(
        space=SPACE_KEY,
        title=title,
        body=content,
        representation='storage',
        parent_id=parent_id
    )
    return new_page['id']

def process_folder(folder_path, parent_id):
    print(f"🔍 Processing: {folder_path}")
    if not os.path.isdir(folder_path):
        print(f"❌ Not a directory: {folder_path}")
        return

    entries = os.listdir(folder_path)
    print(f"📁 Found entries in {folder_path}: {entries}")

    if "index.md" not in entries:
        print(f"⏭️ Skipping folder (no index.md): {folder_path}")
        return

    folder_title = os.path.basename(folder_path)

    # If this folder is the top-level one matching the existing parent page, skip sync
    if parent_id == PARENT_ID and folder_title == os.path.basename(FILES_PATH):
        # update existing landing page with index.md
        index_path = os.path.join(folder_path, "index.md")
        index_content = read_md(index_path)
        print(f"📎 Updating top-level page: {folder_title} (ID: {parent_id})")
        confluence.update_page(parent_id, folder_title, index_content)
        folder_page_id = parent_id
    else:
        print(f"📄 Syncing folder page: {folder_title} (parent ID: {parent_id})")
        index_path = os.path.join(folder_path, "index.md")
        index_content = read_md(index_path)
        image_paths = extract_images(index_content)
        folder_page_id = sync_page(folder_title, parent_id, index_content)
        upload_images(folder_page_id, image_paths, folder_path)

    # Process child markdown files (not index.md)
    for entry in entries:
        entry_path = os.path.join(folder_path, entry)
        if entry.endswith(".md") and entry != "index.md":
            title = os.path.splitext(entry)[0]
            content = read_md(entry_path)
            image_paths = extract_images(content)
            child_page_id = sync_page(title, folder_page_id, content)
            upload_images(child_page_id, image_paths, folder_path)

    # Recurse into subfolders
    for entry in entries:
        entry_path = os.path.join(folder_path, entry)
        if os.path.isdir(entry_path):
            process_folder(entry_path, folder_page_id)

    print(f"✅ Synced page: {title} under parent ID {parent_id}")

# 🚀 Begin syncing
def sync_entire_docs_tree():
    print(f"📄 Starting sync from: {FILES_PATH}")

    # If no parent ID, create top-level page in the space
    if PARENT_ID is None:
        index_path = os.path.join(FILES_PATH, "index.md")
        title = os.path.basename(FILES_PATH)
        content = read_md(index_path)
        print(f"🆕 Creating top-level page in space: {SPACE_KEY} with title: {title}")
        root_page = confluence.create_page(SPACE_KEY, title, content)
        root_id = root_page["id"]
    else:
        root_id = PARENT_ID
        print(f"📎 Using existing parent page ID: {PARENT_ID}")

    process_folder(FILES_PATH, root_id)


# Optional direct run
if __name__ == "__main__":
    sync_entire_docs_tree()