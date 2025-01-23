from typing import Any
from sqlalchemy import Column, TEXT, REAL, INTEGER
from .bmp_table import BMPTable
from ...names import Names


class OutletDrainage(BMPTable):
    __tablename__ = Names.bmp_table_name_outlet_drainage
    Id = Column(INTEGER, primary_key=True)
    Reach = Column(INTEGER)
    DrainageCapacity = Column(REAL)

    def __init__(self, **kw):
        super().__init__(**kw)
