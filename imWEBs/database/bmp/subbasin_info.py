from sqlalchemy import Column, Integer, Float, String
from .bmp_table import BMPTable
from ...names import Names

class SubbasinInfo(BMPTable):
    __tablename__ = Names.bmp_table_name_subbasin_info
    ID = Column(Integer, primary_key=True)
    Area_Ha = Column(Float)
    FlowAcc_Max = Column(Float)
    PRC_Avg = Column(Float)
    DSC_Avg = Column(Float)
    CN2_Avg = Column(Float)

    def __init__(self, id, area_ha, flow_acc, prc, dsc, cn2):
        self.ID = id
        self.Area_Ha = area_ha
        self.FlowAcc_Max = flow_acc
        self.PRC_Avg = prc
        self.DSC_Avg = dsc
        self.CN2_Avg = cn2