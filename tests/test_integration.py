from src.manager import Manager
from src.models import Apartment, ApartmentEvent, Parameters


def test_load_data():
    parameters = Parameters()
    manager = Manager(parameters)
    assert isinstance(manager.apartments, dict)
    assert isinstance(manager.tenants, dict)
    assert isinstance(manager.transfers, list)
    assert isinstance(manager.bills, list)

    for apartment_key, apartment in manager.apartments.items():
        assert isinstance(apartment, Apartment)
        assert apartment.key == apartment_key


def test_tenants_in_manager():
    parameters = Parameters()
    manager = Manager(parameters)
    assert len(manager.tenants) > 0
    names = [tenant.name for tenant in manager.tenants.values()]
    for tenant in ["Jan Nowak", "Adam Kowalski", "Ewa Adamska"]:
        assert tenant in names


def test_if_tenants_have_valid_apartment_keys():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.check_tenants_apartment_keys()

    manager.tenants["tenant-1"].apartment = "invalid-key"
    assert not manager.check_tenants_apartment_keys()


def test_apartment_events():
    parameters = Parameters()
    manager = Manager(parameters)
    manager.load_additional_data()
    assert len(manager.apartments) > 0

    for event in manager.apartment_events:
        event: ApartmentEvent
        assert event.apartment in manager.apartments

    events = manager.generate_apartment_events_report("apart-polanka")
    for event in events:
        assert event.apartment == "apart-polanka"
