from importlib.resources import path
from posixpath import dirname, basename
from MarkdownToConfluence.confluence.PageNotFoundError import PageNotFoundError
from confluence import page_exists_in_space, get_page_id
from confluence import create_page
from confluence import update_page_content
from confluence import upload_attachment
from utils import convert_all_md_img_to_confluence_img
import MarkdownToConfluence.confluence.convert_markdown as conver_markdown
import MarkdownToConfluence.globals
from utils.page_file_info import get_page_name_from_path, get_parent_name_from_path
from MarkdownToConfluence.utils.config import get_config 
from MarkdownToConfluence.confluence.delete_content import delete_stale_confluence_pages
import subprocess
import markdown
import module_loader
import os
import sys

config = get_config()
SPACE_KEY = config["SPACE_KEY"]
PARENT_ID = config["PARENT_ID"]
FILES_PATH = config["FILES_PATH"]

space_obj = { "key": SPACE_KEY }

def upload_documentation(path_name: str, root: str):
    response = ""
    if os.path.isdir(path_name):
        path_name += "/index.md"

    page_name, parent_name = conver_markdown.convert(path_name, root)

    if config["SHOULD_UPLOAD"]:
        if page_exists_in_space(page_name, SPACE_KEY, PARENT_ID):
            try:
                page_id = get_page_id(page_name, SPACE_KEY, PARENT_ID)
                response = update_page_content(path_name, page_name, page_id, space_obj)
                if response.status_code == 200:
                    print(f"Updated {page_name} with {parent_name} as parent")
            except PageNotFoundError as e:
                print(e)
        else:
            if parent_name != "":
                try:
                    if not page_exists_in_space(parent_name, SPACE_KEY, PARENT_ID):
                        print(f"Uploading parent: {parent_name}")
                        file_name = basename(path_name).replace(".md", "")
                        if file_name != "index":
                            subprocess.call(["bash", "/MarkdownToConfluence/convert.sh", f"{dirname(path_name)}/index.md"])
                        else:
                            subprocess.call(["bash", "/MarkdownToConfluence/convert.sh", f"{dirname(dirname(path_name))}/index.md"])
                    parent_id = get_page_id(parent_name, SPACE_KEY, PARENT_ID)
                    response = create_page(path_name, page_name, space_obj, parent_id)
                except PageNotFoundError as e:
                    print(e)
            else:
                response = create_page(path_name, page_name, space_obj)

            if response.status_code == 200:
                print(f"Created {page_name} with {parent_name} as parent")

        if response.status_code == 200:
            for attachment in MarkdownToConfluence.globals.attachments:
                upload_attachment(page_name, attachment[0], attachment[1])
        else:
            print(f"Error uploading {page_name}. Status code {response.status_code}")
            print(response.text)
            sys.exit(1)
        return response
    else:
        print("Skipped uploading")

def upload_all_docs(docs_dir):
    for root, dirs, files in os.walk(docs_dir):
        md_files = [f for f in files if f.endswith(".md")]
        parent_page_title = os.path.basename(root)
        parent_path = os.path.join(root, "index.md")

        if "index.md" in md_files:
            print(f"📄 Uploading parent page: {parent_page_title}")
            upload_documentation(parent_path, docs_dir)

        for file in md_files:
            if file == "index.md":
                continue
            child_path = os.path.join(root, file)
            print(f"📄 Uploading subpage: {file} under {parent_page_title}")
            upload_documentation(child_path, docs_dir)

if __name__ == "__main__":
    MarkdownToConfluence.globals.init()
    upload_all_docs("docs")
    delete_stale_confluence_pages()
