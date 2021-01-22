from typing import Dict, Type, List, Callable

from allocation.domain import events
from allocation.service_layer import unit_of_work, handlers


class AbstractMessageBus:
    handlers: Dict[Type[events.Event], List[Callable]]

    def handle(self, event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
        results = []
        queue = [event]
        while queue:
            event = queue.pop(0)
            for handler in self.handlers[type(event)]:
                results.append(handler(event, uow=uow))
                queue.extend(uow.collect_new_events())
        return results


class MessageBus(AbstractMessageBus):
    handlers = {
        events.AllocationRequired: [handlers.allocate],
        events.BatchCreated: [handlers.add_batch],
        events.BatchQuantityChanged: [handlers.change_batch_quantity],
        events.OutOfStock: [handlers.send_out_of_stock_notification],
    }
