import tempfile
import os
import pytest
from models.applications_model import ApplicationsModel


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        yield tf.name
    os.remove(tf.name)


@pytest.fixture
def model(temp_db):
    return ApplicationsModel(db_path=temp_db)


def test_add_and_get_application(model):
    # Add application
    model.add_application("Org1", "City1", role="RoleA", date="2024-07-01", contact="ContactA", note="NoteA")
    results = model.get_applications_by_organisation("Org1", "City1")
    assert len(results) == 1
    row = results[0]
    assert row[1:3] == ("Org1", "City1")
    assert row[3:] == ("RoleA", "2024-07-01", "ContactA", "NoteA")


def test_update_application(model):
    model.add_application("Org2", "City2", role="RoleB", date="2024-07-02", contact="ContactB", note="NoteB")
    app = model.get_applications_by_organisation("Org2", "City2")[0]
    app_id = app[0]
    model.update_application(app_id, role="RoleC", date="2024-07-03", contact="ContactC", note="NoteC")
    updated = model.get_applications_by_organisation("Org2", "City2")[0]
    assert updated[3:] == ("RoleC", "2024-07-03", "ContactC", "NoteC")


def test_delete_application(model):
    model.add_application("Org3", "City3", role="RoleX", date="2024-07-04", contact="ContactX", note="NoteX")
    app = model.get_applications_by_organisation("Org3", "City3")[0]
    app_id = app[0]
    model.delete_application(app_id)
    remaining = model.get_applications_by_organisation("Org3", "City3")
    assert len(remaining) == 0


def test_has_application(model):
    model.add_application("Org4", "City4", role="RoleY", date="2024-07-05", contact="ContactY", note="NoteY")
    assert model.has_application("Org4", "City4") is True
    assert model.has_application("Nonexistent", "NoCity") is False


def test_get_application_org_city_pairs(model):
    pairs = [("OrgA", "CityA"), ("OrgB", "CityB"), ("OrgA", "CityA")]
    for org, city in pairs:
        model.add_application(org, city, role="Role", date="2024-07-06", contact="Contact", note="Note")
    found_pairs = model.get_application_org_city_pairs()
    assert ("OrgA", "CityA") in found_pairs
    assert ("OrgB", "CityB") in found_pairs
    assert ("Nonexistent", "CityX") not in found_pairs


def test_multiple_applications_same_org_city(model):
    # Should allow multiple roles/dates for same org/city
    model.add_application("OrgD", "CityD", role="Role1", date="2024-07-07", contact="Contact1", note="Note1")
    model.add_application("OrgD", "CityD", role="Role2", date="2024-07-08", contact="Contact2", note="Note2")
    results = model.get_applications_by_organisation("OrgD", "CityD")
    assert len(results) == 2
    assert set([row[3] for row in results]) == {"Role1", "Role2"}

    print("✅ Applications CRUD tests passed")
