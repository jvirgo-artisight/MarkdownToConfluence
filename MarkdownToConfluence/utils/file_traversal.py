import os
from MarkdownToConfluence.utils.config import get_config  # ✅ Central config

config = get_config()
FILES_PATH = config["FILES_PATH"]

def traverse(directory):
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isdir(f):
            traverse(f)
        if f.endswith('.md'):
            print(f)

if __name__ == "__main__":
    traverse(FILES_PATH)
