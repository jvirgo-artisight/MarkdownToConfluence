import os, markdown
import MarkdownToConfluence.module_loader as module_loader
from MarkdownToConfluence.utils import convert_all_md_img_to_confluence_img
from MarkdownToConfluence.utils.page_file_info import get_page_name_from_path, get_parent_name_from_path
import MarkdownToConfluence.globals

def convert(filename: str, root: str):
    MarkdownToConfluence.globals.init()

    # If a directory is given as path, assume index.md as file
    if os.path.isdir(filename):
        filename += "/index.md"

    # 🛑 Exit early if the file doesn't exist (e.g. after rename/move)
    if not os.path.exists(filename):
        raise FileNotFoundError(f"[convert_markdown] File not found: {filename}")

    temp_file = filename.replace('.md', '_final.md')

    # Get page name and parent
    page_name = get_page_name_from_path(filename, root)
    parent_name = get_parent_name_from_path(filename, root)

    # Copy into *_final.md
    with open(filename, 'r') as i, open(temp_file, 'w') as o:
        for line in i:
            o.write(line)

    # Run transform modules
    modules = module_loader.get_modules()
    for module in modules:
        module_loader.run_module(module, temp_file)

    # Convert images
    convert_all_md_img_to_confluence_img(temp_file)

    # Convert to HTML
    with open(temp_file, 'r') as f:
        text = f.read()
        html = markdown.markdown(
            text,
            extensions=['markdown.extensions.tables', 'markdown.extensions.fenced_code']
        )

    with open(filename.replace('.md', '.html'), 'w') as f:
        f.write(html)

    return (page_name, parent_name)
