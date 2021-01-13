from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence


class OutOfStock(Exception): pass


# Can't freeze but SQLAlchemy needs to inject attributes.
# Let's promise not to mutate OrderLines...
@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
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
