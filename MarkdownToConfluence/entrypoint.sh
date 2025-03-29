#!/bin/bash
set -e

echo "⚙️ entrypoint.sh triggered"
echo "📂 Showing docs inside workspace:"
find ./docs -type f

echo "🚀 Syncing all documentation content to Confluence..."
python3 /MarkdownToConfluence/confluence/update_content.py
