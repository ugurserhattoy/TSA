import os
import tempfile
import pytest
from models.sponsor_model import CSVManager


@pytest.fixture
def temp_csv_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def csv_manager(temp_csv_dir):
    csv_path = os.path.join(temp_csv_dir, "sponsors.csv")
    return CSVManager(csv_dir=temp_csv_dir, csv_file=csv_path)


def test_is_csv_outdated_when_no_file(csv_manager):
    if os.path.exists(csv_manager.csv_file):
        os.remove(csv_manager.csv_file)
    assert (
        csv_manager.is_csv_outdated() is True
    ), "❌ is_csv_outdated() should return True if file does not exist."


def test_is_csv_outdated_when_old_file(csv_manager):
    with open(csv_manager.csv_file, "w", encoding="utf-8") as f:
        f.write("test")
    old_time = 60 * 60 * 24 * 100  # 100 days ago
    os.utime(
        csv_manager.csv_file,
        (
            os.path.getatime(csv_manager.csv_file) - old_time,
            os.path.getmtime(csv_manager.csv_file) - old_time,
        ),
    )
    assert (
        csv_manager.is_csv_outdated() is True
    ), "❌ is_csv_outdated() should return True if the file is outdated."


def test_is_csv_outdated_when_recent_file(csv_manager):
    with open(csv_manager.csv_file, "w", encoding="utf-8") as f:
        f.write("test")
    assert (
        csv_manager.is_csv_outdated() is False
    ), "❌ is_csv_outdated() should return False if the file is recent."


def test_download_csv_creates_file(csv_manager):
    if os.path.exists(csv_manager.csv_file):
        os.remove(csv_manager.csv_file)
    csv_manager.download_csv()
    assert os.path.exists(
        csv_manager.csv_file
    ), "❌ download_csv() did not create the CSV file."
    with open(csv_manager.csv_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content) > 0, "❌ download_csv() produced an empty file."

    # def test_reload_csv(csv_manager):
    #     csv_manager.download_csv()
    #     data1 = csv_manager.reload_csv()
    #     assert isinstance(data1, list), "❌ reload_csv() should return a list."
    #     csv_manager.download_csv()
    #     data2 = csv_manager.reload_csv()
    #     assert data1 == data2, (
    #         "❌ reload_csv() should return the same data on repeated reads."
    #     )

    print("✅ CSV Download tests passed")
