import sqlite3
import logging
from models.sponsor_model import CSVManager
from models.transform_model import TransformDB
from models.applications_model import ApplicationsModel
from config import DB_PATH


logger = logging.getLogger()


class DataManager:
    def __init__(self):
        # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # DATA_DIR = os.path.join(BASE_DIR, "data")
        # self.db_path = os.path.join(DATA_DIR, "sponsorship.db")
        self.conn = None
        self.app_model = ApplicationsModel()

    def prepare_database(self):
        csv_manager = CSVManager()
        csv_manager.download_csv()

        transform_db = TransformDB()
        df = transform_db.clean_and_transform_csv()
        transform_db.save_as_sqlite(df, DB_PATH)

        self.conn = sqlite3.connect(DB_PATH)
        return self.conn

    def get_applications(self, organisation_name, city):
        return self.app_model.get_applications_by_organisation(organisation_name, city)

    def add_application(self, org, city, **data):
        logger.info("[APPLICATION]: [Added] for %s | %s ", org, city,)
        return self.app_model.add_application(org, city, **data)

    def update_application(self, application_id, org, city, **data):
        logger.info("[APPLICATION]: [Updated] for %s | %s ", org, city)
        return self.app_model.update_application(application_id, **data)

    def delete_application(self, application_id, org, role):
        logger.info('[APPLICATION]: [Deleted] "%s" role for "%s"', role, org)
        return self.app_model.delete_application(application_id)

    def has_application(self, org, city):
        return self.app_model.has_application(org, city)

    def get_applications_pairs(self):
        return self.app_model.get_application_org_city_pairs()
