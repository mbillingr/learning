from datetime import date

import pytest

from adapters import repository
from service_layer import services, unit_of_work

today = date(year=2020, month=1, day=1)
tomorrow = date(year=2020, month=1, day=2)
later = date(year=2020, month=2, day=1)


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    product = uow.products.get("CRUNCHY-ARMCHAIR")
    assert product.get_batch("b1") is not None
    assert uow.commited


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "b1"


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREAL-SKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTING-SKU"):
        services.allocate("o1", "NONEXISTING-SKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.commited is True


def test_deallocate_removes_line_from_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)

    services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert uow.products.get("COMPLICATED-LAMP").get_batch("b1").available_quantity == 90

    services.deallocate("o1", "COMPLICATED-LAMP", 10, "b1", uow)

    assert uow.products.get("COMPLICATED-LAMP").get_batch("b1").available_quantity == 100


def test_prefers_warehouse_batches_to_shipments():
    uow = FakeUnitOfWork()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, None, uow)
    services.add_batch("shipment-batch", "RETRO-CLOCK", 100, tomorrow, uow)

    services.allocate('oref', "RETRO-CLOCK", 10, uow)

    assert uow.products.get("RETRO-CLOCK").get_batch('in-stock-batch').available_quantity == 90
    assert uow.products.get("RETRO-CLOCK").get_batch('shipment-batch').available_quantity == 100


class FakeRepository(repository.AbstractProductRepository):
    def __init__(self, products):
        self._products = set(products)

    def add(self, product):
        self._products.add(product)

    def get(self, sku):
        try:
            return next(p for p in self._products if p.sku == sku)
        except StopIteration:
            return None

    def list(self):
        return list(self._products)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.commited = False

    def commit(self):
        self.commited = True

    def rollback(self):
        pass
