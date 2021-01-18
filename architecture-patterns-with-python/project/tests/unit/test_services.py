from datetime import date

import pytest

from adapters.repository import FakeRepository
from service_layer import services

today = date(year=2020, month=1, day=1)
tomorrow = date(year=2020, month=1, day=2)
later = date(year=2020, month=2, day=1)


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "b1"


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREAL-SKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTING-SKU"):
        services.allocate("o1", "NONEXISTING-SKU", 10, repo, session)


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)
    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.commited is True


def test_deallocate_removes_line_from_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)

    services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert repo.get("b1").available_quantity == 90

    services.deallocate("o1", "COMPLICATED-LAMP", 10, "b1", repo, session)

    assert repo.get("b1").available_quantity == 100


def test_prefers_warehouse_batches_to_shipments():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, None, repo, session)
    services.add_batch("shipment-batch", "RETRO-CLOCK", 100, tomorrow, repo, session)

    services.allocate('oref', "RETRO-CLOCK", 10, repo, session)

    assert repo.get('in-stock-batch').available_quantity == 90
    assert repo.get('shipment-batch').available_quantity == 100


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.commited


class FakeSession():
    commited = False

    def commit(self):
        self.commited = True
