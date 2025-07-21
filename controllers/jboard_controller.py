import webbrowser, re

class JobBoardController:
    def __init__(self, application_view):
        self.view = application_view
        self.setup_signals()

    def setup_signals(self, org=None):
        try:
            self.view.linkedin_btn.clicked.disconnect()
            self.view.indeed_btn.clicked.disconnect()
            self.view.glassdoor_btn.clicked.disconnect()
            self.view.google_btn.clicked.disconnect()
        except TypeError:
            pass
        self.view.linkedin_btn.clicked.connect(
            lambda: self.open_linkedin(
                org if org else self.get_current_organisation()
            )
        )
        self.view.indeed_btn.clicked.connect(
            lambda: self.open_indeed(
                org if org else self.get_current_organisation()
            )
        )
        self.view.glassdoor_btn.clicked.connect(
            lambda: self.open_glassdoor(
                org if org else self.get_current_organisation()
            )
        )
        self.view.google_btn.clicked.connect(
            lambda: self.open_google_jobs(
                org if org else self.get_current_organisation()
            )
        )

    def get_current_organisation(self):
        table = self.view.applications_table
        row = table.currentRow()
        if row < 0:
            return None
        # Organisation name is assumed to be in the first column
        org_item = table.item(row, 1)
        print("Opening LinkedIn for organisation:", org_item.text() if org_item else None)
        return org_item.text() if org_item else None

    def open_linkedin(self, org=None):
        print("Opening LinkedIn for organisation:", org)
        if org:
            org = self.clean_organisation_name(org)
            print("Opening LinkedIn for organisation:", org)
            url = f"https://www.linkedin.com/jobs/search/?keywords={org}"
            webbrowser.open(url)

    def open_indeed(self, org=None):
        print("Opening LinkedIn for organisation:", org)
        if org:
            org = self.clean_organisation_name(org)
            print("Opening LinkedIn for organisation:", org)
            url = f"https://www.indeed.com/jobs?q={org}"
            webbrowser.open(url)

    def open_glassdoor(self, org=None):
        print("Opening LinkedIn for organisation:", org)
        if org:
            org = self.clean_organisation_name(org)
            print("Opening LinkedIn for organisation:", org)
            # url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={org}"
            url = f"https://www.glassdoor.com/Search/results.htm?keyword={org}"
            webbrowser.open(url)

    def open_google_jobs(self, org=None):
        print("Opening LinkedIn for organisation:", org)
        if org:
            org = self.clean_organisation_name(org)
            print("Opening LinkedIn for organisation:", org)
            url = f"https://www.google.com/search?q={org}+careers"
            webbrowser.open(url)

    @staticmethod
    def clean_organisation_name(org_name):
        # Remove common suffixes and clean the name
        remove_suffixes = [
            r"\binc\b",
            r"\blimited\b",
            r"\bltd\b",
            r"\bplc\b",
            r"\bcorp\b",
            r"\bllc\b",
            r"\bco\b",
            r"\bsarl\b", r"\bgmbh\b", r"\bgroup\b", r"\bservices\b"
        ]
        name = org_name.lower()
        name = re.sub(r"[^a-zA-Z0-9\s]", "", name)  # remove special characters
        name = re.sub(r"\s+", " ", name).strip()    # remove extra spaces
        for suffix in remove_suffixes:
            name = re.sub(suffix, "", name)
        words = name.split()
        # If there are more than 3 words, take the first 3
        core_name = " ".join(words[:3]) if len(words) > 3 else " ".join(words)
        return core_name.strip().title()  # Uppercase the first letter of each word