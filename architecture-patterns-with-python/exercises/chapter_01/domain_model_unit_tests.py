import pytest


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = make_batch_and_line('SMALL-TABLE', 20, 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch, line = make_batch_and_line('SMALL-TABLE', 20, 2)

    assert batch.can_allocate(line)


def test_cant_allocate_if_available_less_than_required():
    batch, line = make_batch_and_line('BLUE-CUSHION', 2, 20)

    assert not batch.can_allocate(line)


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line('SMALL-TABLE', 2, 2)

    assert batch.can_allocate(line)


def test_cant_allocate_if_skus_dont_match():
    batch = Batch('batch-001', 'SMALL-TABLE', qty=1, eta=None)
    line = OrderLine('order-001', 'BLUE-VASE', 1)

    assert not batch.can_allocate(line)


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line('DECORATIVE-TRINKET', 10, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 10


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line('ANGULAR-DESK', 20, 2)
    batch.allocate(line)

    batch.allocate(line)

    assert batch.available_quantity == 18


def make_batch_and_line(sku, batch_qty, line_qty):
    batch = Batch('batch-001', sku, qty=batch_qty, eta=None)
    different_sku_line = OrderLine('order-001', sku, line_qty)
    return batch, different_sku_line


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch('in-stock-batch', "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch('shipment-batch', "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine('oref', "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch('speedy-batch', 'MINIMALIST-SPOON', 100, eta=today)
    medium = Batch('normal-batch', 'MINIMALIST-SPOON', 100, eta=tomorrow)
    latest = Batch('slow-batch', 'MINIMALIST-SPOON', 100, eta=later)
    line = OrderLine('order1', 'MINIMALIST-SPOON', 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch('in-stock-batch', "FUTURISTIC-CLOCK", 100, eta=None)
    shipment_batch = Batch('shipment-batch', "FUTURISTIC-CLOCK", 100, eta=tomorrow)
    line = OrderLine('oref', 'FUTURISTIC-CLOCK', 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
    allocate(OrderLine('order1', 'SMALL-FORK', 10), [batch])

    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine('order1', 'SMALL-FORK', 10), [batch])


from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence

today = date(year=2020, month=1, day=1)
tomorrow = date(year=2020, month=1, day=2)
later = date(year=2020, month=2, day=1)


class OutOfStock(Exception): pass


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_qty = qty
        self._allocations = set()

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def available_quantity(self) -> int:
        return self._purchased_qty - self.allocated_quantity

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __gt__(self, other):
        if self.eta is None:
            return False

        if other.eta is None:
            return True

        return self.eta > other.eta


def allocate(line: OrderLine, batches: Sequence[Batch]) -> str:
    try:
        batch = min(b for b in batches if b.can_allocate(line))
    except ValueError:
        raise OutOfStock(f'Out of stock: {line.sku}')
    batch.allocate(line)
    return batch.reference
