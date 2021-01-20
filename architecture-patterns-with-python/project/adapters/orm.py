from sqlalchemy.orm import mapper, relationship
from sqlalchemy import MetaData, Table, Column, Integer, String, Date, ForeignKey

from domain import model


metadata = MetaData()

order_lines = Table(
    'order_lines', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
    Column('orderid', String(255)),)

batches = Table(
    'batches', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('reference', String(255)),
    Column('sku', String(255)),
    Column('eta', Date),
    Column('_purchased_quantity', Integer, nullable=False),)

products = Table(
    'products', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),)

allocations = Table(
    'allocations', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('orderline_id', ForeignKey('order_lines.id')),
    Column('batch_id', ForeignKey('batches.id')),)

productbatches = Table(
    'productbatches', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('product_id', ForeignKey('products.id')),
    Column('batch_id', ForeignKey('batches.id')),)


def start_mappers():
    lines_mapper = mapper(model.OrderLine, order_lines)
    batch_mapper = mapper(model.Batch, batches, properties={
        '_allocations': relationship(lines_mapper, secondary=allocations, collection_class=set)
    })
    mapper(model.Product, products, properties={
        'batches': relationship(batch_mapper, secondary=productbatches, collection_class=list)
    })
