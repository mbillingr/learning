import abc

from domain import model


class AbstractProductRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product):
        raise NotImplementedError()

    @abc.abstractmethod
    def get(self, sku) -> model.Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractProductRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product):
        self.session.add(product)

    def get(self, sku):
        return self.session.query(model.Product).filter_by(sku=sku).one()

    def list(self):
        return self.session.query(model.Product).all()
