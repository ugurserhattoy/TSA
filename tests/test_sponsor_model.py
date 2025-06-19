import os
import time
import tempfile
import pytest
from models.sponsor_model import CSVManager


@pytest.fixture(name="csv_manager")
def make_csv_manager():
    with tempfile.TemporaryDirectory() as temp_dir:
        csv_path = os.path.join(temp_dir, "sponsors.csv")
        yield CSVManager(csv_dir=temp_dir, csv_file=csv_path)


def test_is_csv_outdated_nofile(csv_manager):
    """Test if .csv file not found"""
    if os.path.exists(csv_manager.csv_file):
        os.remove(csv_manager.csv_file)
    assert not os.path.exists(
        csv_manager.csv_file
    ), "❌ CSV file should not exist before running the test, but it does."
    assert (
        csv_manager.is_csv_outdated()
    ), "❌ is_csv_outdated() should return True when the file not found."


def test_is_csv_outdated_old_file(csv_manager):
    """Test if .csv file outdated"""
    with open(csv_manager.csv_file, "w", encoding="utf-8") as f:
        f.write("dummy test data")
    old_time = time.time() - (90 * 24 * 60 * 60)  # 90 days before
    os.utime(csv_manager.csv_file, (old_time, old_time))
    assert (
        csv_manager.is_csv_outdated()
    ), "❌ is_csv_outdated() should return True when the file is outdated."


def test_is_csv_outdated_recent_file(csv_manager):
    """Test when .csv file is up to date"""
    with open(csv_manager.csv_file, "w", encoding="utf-8") as f:
        f.write("dummy test data")
    recent_time = time.time()
    os.utime(csv_manager.csv_file, (recent_time, recent_time))
    assert (
        not csv_manager.is_csv_outdated()
    ), "❌ is_csv_outdated() should return False when the file is up to date."


def test_download_csv(csv_manager):
    """Test .csv download"""
    if os.path.exists(csv_manager.csv_file):
        os.remove(csv_manager.csv_file)

    assert not os.path.exists(
        csv_manager.csv_file
    ), "❌ .csv file couldn't be removed or an error occured when checked"

    csv_manager.download_csv()

    assert os.path.exists(csv_manager.csv_file), "❌ .csv file not found after download"
