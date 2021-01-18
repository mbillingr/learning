from datetime import date
from typing import Optional

from adapters.repository import AbstractRepository
from domain import model


class InvalidSku(Exception):
    pass


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], repo: AbstractRepository, session):
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()


def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
    line = model.OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(orderid: str, sku: str, qty: int, batchref: str, repo: AbstractRepository, session) -> str:
    batch = repo.get(batchref)
    line = model.OrderLine(orderid, sku, qty)
    batch.deallocate(line)


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}
