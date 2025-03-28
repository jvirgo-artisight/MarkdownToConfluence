import json
from MarkdownToConfluence.utils.config import get_config

def init(settings_path=""):
    global attachments, settings
    _is_init = False
    if not _is_init:
        attachments = []
        _is_init = True

    config = get_config()

    if settings_path == "":
        if config["FILES_PATH"]:
            try:
                settings = json.load(open(os.path.join(config["FILES_PATH"], 'settings.json')))
            except FileNotFoundError:
                settings = None
    else:
        settings = json.load(open(settings_path))


def reset():
    global attachments
    attachments = []