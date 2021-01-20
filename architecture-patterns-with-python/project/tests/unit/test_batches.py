
from domain.model import Batch, OrderLine


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
