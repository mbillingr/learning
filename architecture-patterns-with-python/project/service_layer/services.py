from domain import model
from domain.model import OrderLine, Batch
from adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(line: OrderLine, batchref: str, repo: AbstractRepository, session) -> str:
    batch = repo.get(batchref)
    batch.deallocate(line)


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}
