import pytest

from domain import model
from service_layer import services
from adapters.repository import FakeRepository


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTING-SKU", 10)
    batch = model.Batch("b1", "AREAL-SKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTING-SKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.commited is True


def test_deallocate_removes_line_from_batch():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    batch.allocate(line)
    repo = FakeRepository([batch])

    assert batch.available_quantity == 90

    services.deallocate(line, "b1", repo, FakeSession())

    assert batch.available_quantity == 100


class FakeSession():
    commited = False

    def commit(self):
        self.commited = True
