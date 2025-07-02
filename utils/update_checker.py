import logging
import platform
import requests
import markdown2
from config import GITHUB_REL


system = platform.system()
logger = logging.getLogger()


def fetch_latest_release():
    try:
        rel_response = requests.get(GITHUB_REL, timeout=3)
        if rel_response.status_code == 200:
            data = rel_response.json()
            changelog_md = data.get("body", "")
            changelog_html = markdown_to_html(changelog_md)
            return {
                "tag": data["tag_name"],
                "asset": find_asset_url(data.get("assets", []), data["html_url"]),
                "changelog": changelog_html,
                "html_url": data["html_url"],
            }
    except requests.exceptions.HTTPError as http_err:
        logger.error("❌ [UpdateChecker] HTTP Error: %s", http_err)
        raise
    return None


def find_asset_url(assets, html_url):
    if system == "Windows":
        for asset in assets:
            if asset["name"].lower().endswith(".exe"):
                return asset["browser_download_url"]
    elif system == "Darwin":
        for asset in assets:
            if asset["name"].lower().endswith(".dmg"):
                return asset["browser_download_url"]
    elif system == "Linux":
        for asset in assets:
            if asset["name"].lower().endswith(".appimage"):
                return asset["browser_download_url"]
    if assets:
        logger.info(
            "[UpdateChecker] asset download url was not found, replaced with html link."
        )
        return html_url
    return None


def markdown_to_html(md_text):
    return markdown2.markdown(md_text)

# latest_version = fetch_latest_release()
# print(latest_version['changelog'])
