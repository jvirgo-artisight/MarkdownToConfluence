#!/bin/bash
set -e

echo "⚙️ entrypoint.sh triggered"
echo "📂 Showing files inside workspace:"
find . -type f

echo "🚀 Syncing all documentation content to Confluence..."
python3 /MarkdownToConfluence/confluence/update_content.py
