from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from TSA.config import CSV_PATH, DATA_DIR

class CSVManager:
    def __init__(self):
        """Defines initial file path and url"""
        self.csv_dir = DATA_DIR
        self.csv_file = CSV_PATH
        self.uk_sponsors_url = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"

        os.makedirs(self.csv_dir, exist_ok=True)

    def is_csv_outdated(self, months=1):
        """Checks if the .csv file is up to date"""
        if not os.path.exists(self.csv_file):
            return True
        
        modified_time = datetime.fromtimestamp(os.path.getmtime(self.csv_file))
        current_time = datetime.now()
        diff_months = (current_time.year - modified_time.year) * 12 + (current_time.month - modified_time.month)
        return diff_months >= months
    
    def get_latest_csv_link(self):
        response = requests.get(self.uk_sponsors_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            # print(link)
            href = link["href"]
            if "Worker_and_Temporary_Worker.csv" in href:
                if href.startswith("https://"):
                    return href
                else:
                    return "https://assets.publishing.service.gov.uk" + href

        raise Exception("Lates .csv file not found")
    
    def download_csv(self):
        """Download latest .csv file"""
        if self.is_csv_outdated():
            print(".csv file is outdated, updating...")
            latest_csv_url = self.get_latest_csv_link()
            try:
                response = requests.get(latest_csv_url, stream=True)
                response.raise_for_status()

                with open(self.csv_file, "wb") as file:
                    # file.write(response.content)
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"✅ Latest .csv file downloaded: {self.csv_file}")
            
            except requests.exceptions.HTTPError as http_err:
                print(f"❌ HTTP Error: {http_err}")
                raise
            
            except Exception as err:
                print(f"❌ An unexpected error occurred: {err}")
                raise
        else:
            print("✅ .csv file is up to date...")

if __name__ == "__main__":
    csv_manager = CSVManager()
    csv_manager.download_csv()