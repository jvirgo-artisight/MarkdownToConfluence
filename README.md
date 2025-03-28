# MarkdownToConfluence
Forked and enhanced by Artisight to support parent scoping, page cleanup, and flexible configuration.

This GitHub Action converts your markdown documentation into structured Confluence pages under a specific space and parent page.

---

## 🚀 What This Action Does
- Converts `.md` files into Confluence-formatted HTML.
- Preserves folder-based page hierarchy.
- Uploads to a **specific space and parent page** (`parent_id`).
- Deletes Confluence pages that no longer exist in the repo.
- Supports preview environments (only uploads changed content).

---

## ⚙️ Setup

### API User Token
Create an Atlassian API token for your Confluence user. This user should have full write access to the target space.

[How to create an API token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

---

## 📊 Inputs

### `confluence_url` ✨ **Required**
Base URL for your Atlassian instance. Format: `https://your-company.atlassian.net`

### `confluence_space_key` ✨ **Required**
The key of your Confluence space (shown in the URL).

### `auth_username` ✨ **Required**
Email address of your Confluence user. Recommended to use GitHub secrets.

### `auth_api_token` ✨ **Required**
API token for authentication. Recommended to use GitHub secrets.

### `fileslocation` ✅ Optional
Path to your markdown docs directory. Default: `./`

### `parent_id` ✨ **Required**
The Confluence page ID under which all new pages will be created.

### `should_upload` ✅ Optional
Whether to upload on push. Default: `true`

### `is_preview` ✅ Optional
If true, uploads only the changed pages and their parents (for use in preview environments).

---

## 📆 Example Usage

```yaml
jobs:
  markdown_to_confluence:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Publish Markdown to Confluence
        uses: jvirgo-artisight/MarkdownToConfluence@main
        with:
          fileslocation: 'docs'
          confluence_url: 'https://your-company.atlassian.net'
          confluence_space_key: 'SPACEKEY'
          parent_id: '1234567890'
          auth_username: ${{ secrets.CONFLUENCE_USERNAME }}
          auth_api_token: ${{ secrets.CONFLUENCE_API_TOKEN }}
          should_upload: true
          is_preview: false
```

### 🌐 Full CI Pipeline
**Preview on PR, Publish on Merge**

#### `.github/workflows/preview.yaml`
```yaml
on:
  pull_request:
    branches: ["main"]
    paths: ["docs/**"]

jobs:
  create-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Preview Docs to Confluence
        uses: jvirgo-artisight/MarkdownToConfluence@main
        with:
          fileslocation: 'docs'
          confluence_url: 'https://your-company.atlassian.net'
          confluence_space_key: 'PreviewKey'
          parent_id: '9876543210'
          auth_username: ${{ secrets.CONFLUENCE_USERNAME }}
          auth_api_token: ${{ secrets.CONFLUENCE_API_TOKEN }}
          is_preview: true
```

#### `.github/workflows/upload.yaml`
```yaml
on:
  push:
    branches: ["main"]
    paths: ["docs/**"]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Publish Docs to Confluence
        uses: jvirgo-artisight/MarkdownToConfluence@main
        with:
          fileslocation: 'docs'
          confluence_url: 'https://your-company.atlassian.net'
          confluence_space_key: 'SPACEKEY'
          parent_id: '1234567890'
          auth_username: ${{ secrets.CONFLUENCE_USERNAME }}
          auth_api_token: ${{ secrets.CONFLUENCE_API_TOKEN }}
          should_upload: true
          is_preview: false
```

---

## 📃 Writing Docs

### File Structure
Your docs folder mirrors the desired Confluence page tree.

- Each folder = a Confluence page
- `index.md` inside a folder = content for that page
- Other `.md` files = child pages
- Nested folders = nested child pages

```
docs/
  Overview/
    index.md
    HowItWorks.md
  Troubleshooting/
    index.md
  README.md (ignored)
```

### Prefixing
Include `prefix.txt` in any folder to prefix page names.

### Cleanup
Pages removed from the filesystem are automatically deleted from Confluence during the next push.

### Modules
Supports:
- Jira ticket linking
- Mermaid diagrams
- Trello boards
- Attachment upload
- Table of contents

See `doc/modules/*.md` for usage.

---

Maintained with ❤️ by Artisight