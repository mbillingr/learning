import pytest
from datetime import date
from allocation.adapters import repository
from allocation.domain import events
from allocation.service_layer import messagebus, handlers, unit_of_work
from typing import List


class TestAddBatch:
    def test_for_new_product(self):
        uow = FakeUnitOfWork()
        mb = messagebus.MessageBus()
        mb.handle(events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None), uow)
        assert uow.products.get('CRUNCHY-ARMCHAIR') is not None
        assert uow.committed

    def test_for_existing_product(self):
        uow = FakeUnitOfWork()
        mb = messagebus.MessageBus()
        mb.handle(events.BatchCreated("b1", "GARISH-RUG", 100, None), uow)
        mb.handle(events.BatchCreated("b2", "GARISH-RUG", 99, None), uow)
        assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG").batches]


class TestAllocate:
    def test_returns_allocation(self):
        uow = FakeUnitOfWork()
        mb = messagebus.MessageBus()
        mb.handle(events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None), uow)
        result = mb.handle(events.AllocationRequired("o1", "COMPLICATED-LAMP", 10), uow)
        assert result == ["batch1"]

    def test_errors_for_invalid_sku(self):
        uow = FakeUnitOfWork()
        mb = messagebus.MessageBus()
        mb.handle(events.BatchCreated("b1", "AREALSKU", 100, None), uow)

        with pytest.raises(handlers.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
            mb.handle(events.AllocationRequired("o1", "NONEXISTENTSKU", 10), uow)

    def test_commits(self):
        uow = FakeUnitOfWork()
        mb = messagebus.MessageBus()
        mb.handle(events.BatchCreated("b1", "OMINOUS-MIRROR", 100, None), uow)
        mb.handle(events.AllocationRequired("o1", "OMINOUS-MIRROR", 10), uow)
        assert uow.committed


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        uow = FakeUnitOfWork()
        mb = messagebus.MessageBus()
        mb.handle(events.BatchCreated("batch1", "ADORABLE-SETTEE", 100, None), uow)
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        mb.handle(events.BatchQuantityChanged("batch1", 50), uow)

        assert batch.available_quantity == 50

    def test_reallocates_if_necessary(self):
        uow = FakeUnitOfWork()
        mb = messagebus.MessageBus()
        event_history = [
            events.BatchCreated("batch1", "INDIFFERENT-TABLE", 50, None),
            events.BatchCreated("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            events.AllocationRequired("order1", "INDIFFERENT-TABLE", 20),
            events.AllocationRequired("order2", "INDIFFERENT-TABLE", 20),
        ]
        for e in event_history:
            mb.handle(e, uow)
        [batch1, batch2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        mb.handle(events.BatchQuantityChanged("batch1", 25), uow)

        assert batch1.available_quantity == 5
        assert batch2.available_quantity == 30

    def test_reallocates_if_necessary_isolated(self):
        uow = FakeUnitOfWork()
        mb = messagebus.MessageBus()
        event_history = [
            events.BatchCreated("batch1", "INDIFFERENT-TABLE", 50, None),
            events.BatchCreated("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            events.AllocationRequired("order1", "INDIFFERENT-TABLE", 20),
            events.AllocationRequired("order2", "INDIFFERENT-TABLE", 20),
        ]
        for e in event_history:
            mb.handle(e, uow)
        [batch1, batch2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        fmb = FakeMessageBus()

        fmb.handle(events.BatchQuantityChanged("batch1", 25), uow)
        [reallocation_event] = fmb.events_published
        assert isinstance(reallocation_event, events.AllocationRequired)
        assert reallocation_event.orderid in {'order1', 'order2'}
        assert reallocation_event.sku == 'INDIFFERENT-TABLE'


class FakeRepository(repository.AbstractRepository):

    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next((
            p for p in self._products for b in p.batches
            if b.reference == batchref
        ), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self):
        super().__init__()
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeUnitOfWorkWithFakeMessageBus(FakeUnitOfWork):

    def __init__(self):
        super().__init__()
        self.events_published = []  # type: List[events.Event]

    def collect_new_events(self):
        for product in self.products.seen:
            while product.events:
                self.events_published.append(product.events.pop(0))
        return []


class FakeMessageBus(messagebus.AbstractMessageBus):
    def __init__(self):
        self.events_published = []  # type: List[events.Event]
        self.handlers = {
            events.AllocationRequired: [self.publish],
            events.BatchCreated: [self.publish],
            events.BatchQuantityChanged: [self.publish],
            events.OutOfStock: [self.publish],
        }

    def publish(self, e, uow):
        self.events_published.append(e)
