import time

import pytest

from src.manager import Manager
from src.models import Apartment, Parameters, Tenant


def _create_n_apartments(n: int) -> dict:
    """Return a dict of n apartments with keys 'apart-0', 'apart-1', ..., 'apart-(n-1)'."""
    return {
        f"apart-{i}": Apartment(
            key=f"apart-{i}",
            name=f"Apart {i}",
            area_m2=100.0,
            location=f"{i} Main St",
            rooms={},
        )
        for i in range(n)
    }


def _create_n_tenants(n: int, m: int) -> dict:
    """Return a dict of n tenants with keys 'tenant-0', 'tenant-1', ..., 'tenant-(n-1)'. Every m-th tenant is assigned to an existing apartment, the rest are assigned to non-existing apartments."""
    return {
        f"tenant-{i}": Tenant(
            key=f"tenant-{i}",
            name=f"Tenant {i}",
            apartment=f"apart-{i % m}",
            room="room-example",
            deposit_pln=0.0,
            rent_pln=0.0,
            date_agreement_from="2025-01-01",
            date_agreement_to="2025-12-31",
        )
        for i in range(n)
    }


def test_search_for_apartment_large_dataset():
    """Searching for an apartment in a dataset of 10 000 apartments should complete within the time limit."""
    ALLOWED_SEARCH_TIME_MS = 1  # 1 millisecond
    N = 100_000
    manager = Manager(Parameters())
    manager.apartments = _create_n_apartments(N)

    exisitng_apartment_key = "apart-80901"
    non_existent_apartment_key = "apart-1000000"

    ok_search_time = time.perf_counter()
    result_ok = manager.get_apartment(exisitng_apartment_key)
    ok_search_time = (
        time.perf_counter() - ok_search_time
    ) * 1e3  # convert to milliseconds

    fail_search_time = time.perf_counter()
    result_fail = manager.get_apartment(non_existent_apartment_key)
    fail_search_time = (
        time.perf_counter() - fail_search_time
    ) * 1e3  # convert to milliseconds

    assert type(result_ok) is Apartment
    assert result_fail is None
    assert ok_search_time < ALLOWED_SEARCH_TIME_MS, (
        f"Searching for existing apartment in {N} apartments took {ok_search_time:.3f}ms, limit {ALLOWED_SEARCH_TIME_MS}ms"
    )
    assert fail_search_time < ALLOWED_SEARCH_TIME_MS, (
        f"Searching for non-existing apartment in {N} apartments took {fail_search_time:.3f}ms, limit {ALLOWED_SEARCH_TIME_MS}ms"
    )


def test_check_tenants_apartment_keys_large_dataset():
    """Checking tenants' apartment keys in a dataset of 10 000 apartments and 100 000 tenants should complete within the time limit."""
    pytest.skip(
        reason="This test is very time consuming, it is only for performance testing purposes and should not be run with the rest of the tests."
    )
    ALLOWED_CREATE_TIME_S = 10  # 10 seconds
    ALLOWED_CHECK_TIME_MS = 10  # 10 milliseconds
    N_APARTMENTS = 10_000
    N_TENANTS = 1_000_000

    manager = Manager(Parameters())

    create_time = time.perf_counter()
    manager.apartments = _create_n_apartments(N_APARTMENTS)
    manager.tenants = _create_n_tenants(
        N_TENANTS, N_APARTMENTS + 1
    )  # every 10001-th tenant is assigned to a non-existing apartment
    create_time = time.perf_counter() - create_time  # convert to seconds

    check_time = time.perf_counter()
    result = manager.check_tenants_apartment_keys()
    check_time = (time.perf_counter() - check_time) * 1e3  # convert to milliseconds

    assert result is False
    assert check_time < ALLOWED_CHECK_TIME_MS, (
        f"Checking tenants' apartment keys in {N_APARTMENTS} apartments and {N_TENANTS} tenants took {check_time:.3f}ms, limit {ALLOWED_CHECK_TIME_MS}ms"
    )
    assert create_time < ALLOWED_CREATE_TIME_S, (
        f"Creating {N_APARTMENTS} apartments and {N_TENANTS} tenants took {create_time:.3f}s, limit {ALLOWED_CREATE_TIME_S}s"
    )
