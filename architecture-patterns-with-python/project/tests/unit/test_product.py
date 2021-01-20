from datetime import date

import pytest

from domain.model import Batch, OrderLine, OutOfStock, Product

today = date(year=2020, month=1, day=1)
tomorrow = date(year=2020, month=1, day=2)
later = date(year=2020, month=2, day=1)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch('in-stock-batch', "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch('shipment-batch', "RETRO-CLOCK", 100, eta=tomorrow)
    product = Product("RETRO-CLOCK", [in_stock_batch, shipment_batch])
    line = OrderLine('oref', "RETRO-CLOCK", 10)

    product.allocate(line)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch('speedy-batch', 'MINIMALIST-SPOON', 100, eta=today)
    medium = Batch('normal-batch', 'MINIMALIST-SPOON', 100, eta=tomorrow)
    latest = Batch('slow-batch', 'MINIMALIST-SPOON', 100, eta=later)
    product = Product('MINIMALIST-SPOON', [medium, earliest, latest])
    line = OrderLine('order1', 'MINIMALIST-SPOON', 10)

    product.allocate(line)

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch('in-stock-batch', "FUTURISTIC-CLOCK", 100, eta=None)
    shipment_batch = Batch('shipment-batch', "FUTURISTIC-CLOCK", 100, eta=tomorrow)
    product = Product("FUTURISTIC-CLOCK", [in_stock_batch, shipment_batch])
    line = OrderLine('oref', 'FUTURISTIC-CLOCK', 10)
    allocation = product.allocate(line)
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
    product = Product('SMALL-FORK', [batch])
    product.allocate(OrderLine('order1', 'SMALL-FORK', 10))

    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        product.allocate(OrderLine('order1', 'SMALL-FORK', 10))
