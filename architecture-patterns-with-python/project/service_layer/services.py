from datetime import date
from typing import Optional

from domain import model
from service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product = model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batchref = product.allocate(line)
        uow.commit()
    return batchref


def deallocate(orderid: str, sku: str, qty: int, batchref: str, uow: AbstractUnitOfWork) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        product.deallocate(line, batchref)
        uow.commit()


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}
