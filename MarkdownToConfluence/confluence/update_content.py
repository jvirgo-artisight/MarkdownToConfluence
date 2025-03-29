from MarkdownToConfluence.utils.config import get_config
from MarkdownToConfluence.confluence.create_content import sync_entire_docs_tree

print("📄 Starting full Confluence sync from local docs folder...")
sync_entire_docs_tree()
