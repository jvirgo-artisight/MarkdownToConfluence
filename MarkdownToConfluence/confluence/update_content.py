from MarkdownToConfluence.utils.config import get_config
from MarkdownToConfluence.confluence.create_content import sync_entire_docs_tree

print("🔧 Running update_content.py...")
config = get_config()
print("📦 Config loaded:")
for k, v in config.items():
    if "TOKEN" in k:
        print(f"{k}: (hidden)")
    else:
        print(f"{k}: {v}")

print("📄 Starting full Confluence sync from local docs folder...")
sync_entire_docs_tree()