from allocation.service_layer import unit_of_work
from allocation.adapters import redis_eventpublisher


def allocations(orderid: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    batches = redis_eventpublisher.get_readmodel(orderid)
    return [{'sku': s.decode(), 'batchref': b.decode()} for s, b in batches.items()]
