"""
csv_manager.py

Handles downloading and updating the latest UK licensed sponsor CSV file.
Includes logic to determine if the current CSV file is outdated and fetch the
most recent version from the UK government's website.

This module is part of the 'Model' layer in the MVC architecture.
"""

import os
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from config import CSV_PATH, DATA_DIR
# from TSA.sponsor.init_logger import init_logger
# from sponsor.settings_manager import SettingsManager


class CSVLinkNotFoundError(Exception):
    """Raised when the latest sponsor CSV link could not be found."""


class CSVManager:
    def __init__(self, csv_dir=DATA_DIR, csv_file=CSV_PATH):
        """Manages sponsor CSV file download and freshness. Accepts optional custom paths."""
        self.csv_dir = csv_dir
        self.csv_file = csv_file
        self.uk_sponsors_url = (
            "https://www.gov.uk/government/publications/"
            "register-of-licensed-sponsors-workers"
        )
        # log_level = SettingsManager().get_setting("log_level")
        self.logger = logging.getLogger()

        os.makedirs(self.csv_dir, exist_ok=True)

    def is_csv_outdated(self, months=1):
        """Checks if the .csv file is up to date"""
        if not os.path.exists(self.csv_file):
            return True

        modified_time = datetime.fromtimestamp(os.path.getmtime(self.csv_file))
        current_time = datetime.now()
        diff_months = (current_time.year - modified_time.year) * 12 + (
            current_time.month - modified_time.month
        )
        return diff_months >= months

    def get_latest_csv_link(self):
        response = requests.get(self.uk_sponsors_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "Worker_and_Temporary_Worker.csv" in href:
                return (
                    href
                    if href.startswith("https://")
                    else "https://assets.publishing.service.gov.uk" + href
                )

        raise CSVLinkNotFoundError("Latest .csv file not found")

    def download_csv(self):
        """Download latest .csv file"""
        if self.is_csv_outdated():
            self.logger.info(".csv file is outdated, updating...")
            latest_csv_url = self.get_latest_csv_link()
            try:
                response = requests.get(latest_csv_url, stream=True, timeout=10)
                response.raise_for_status()

                with open(self.csv_file, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                self.logger.info("✅ Latest .csv file downloaded: %s", self.csv_file)

            except requests.exceptions.HTTPError as http_err:
                self.logger.error("❌ HTTP Error: %s", http_err)
                raise

            except Exception as err:
                self.logger.error("❌ An unexpected error occurred: %s", err)
                raise
        else:
            self.logger.info("✅ .csv file is up to date...")
