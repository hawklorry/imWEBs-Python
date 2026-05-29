from sqlalchemy import Column, Integer, Float
from sqlalchemy import create_engine, select
from .bmp_table import BMPTable
from ...names import Names

class ReachParameter(BMPTable):
    """Reach parameter in BMP database"""
    __tablename__ = Names.bmp_table_name_reach_parameter

    # Define columns
    reach_id = Column(Integer, primary_key=True)
    subbasin_id = Column(Integer)
    outlet_id = Column(Integer)
    length = Column(Float)
    width = Column(Float)
    main_side_slope = Column(Float)
    floodplain_side_slope = Column(Float)
    w_ratio = Column(Float)
    depth = Column(Float)
    slope = Column(Float)
    order = Column(Integer)
    manning = Column(Float)
    velocity = Column(Float)
    t0 = Column(Float)
    d0 = Column(Float)
    max_elevation = Column(Float)
    min_elevation = Column(Float)
    Ave_elevation = Column(Float)
    receive_reach_id = Column(Integer)
    contribution_area = Column(Float)
    erodibility_factor = Column(Float)
    cover_factor = Column(Float)
    bc1 = Column(Float)
    bc2 = Column(Float)
    bc3 = Column(Float)
    bc4 = Column(Float)
    rk1 = Column(Float)
    rk2 = Column(Float)
    rk3 = Column(Float)
    rk4 = Column(Float)
    rs1 = Column(Float)
    rs2 = Column(Float)
    rs3 = Column(Float)
    rs4 = Column(Float)
    rs5 = Column(Float)
    minFlow = Column(Float)
    k_chb = Column(Float)
    k_bank = Column(Float)
    bnk0 = Column(Float)
    chs0 = Column(Float)
    a_bnk = Column(Float)
    b_bnk = Column(Float)
    MSK_X = Column(Float)
    MSK_col = Column(Float)
    bank_PP_coef = Column(Float)
    bank_DP_coef = Column(Float)
    bank_PN_coef = Column(Float)
    bank_DN_coef = Column(Float)
    bank_Ero_frac = Column(Float)

    def __init__(self):
        self.main_side_slope = 0.5
        self.floodplain_side_slope = 0.2
        self.w_ratio = 5.0
        self.t0 = 0
        self.d0 = 0
        self.erodibility_factor = 0.1
        self.cover_factor = 0.2
        self.bc1 = 0.55
        self.bc2 = 1.1
        self.bc3 = 0.21
        self.bc4 = 0.35
        self.rk1 = 1.71
        self.rk2 = 50
        self.rk3 = 0.36
        self.rk4 = 2
        self.rs1 = 1.0
        self.rs2 = 0.05
        self.rs3 = 0.5
        self.rs4 = 0.05
        self.rs5 = 0.05
        self.minFlow = 0
        self.k_chb = 0
        self.k_bank = 0
        self.bnk0 = 0
        self.chs0 = 0
        self.a_bnk = 0.2
        self.b_bnk = 0.05
        self.MSK_X = 0
        self.MSK_col = 0
        self.bank_PP_coef = 0.2
        self.bank_DP_coef = 0.05
        self.bank_PN_coef = 0.25
        self.bank_DN_coef = 1.0
        self.bank_Ero_frac = 0.5
        
    @staticmethod
    def get_columns():
        r = ReachParameter()
        columns = []
        for col in r.__table__.columns:
            if hasattr(r, col.name):
                columns.append(col.name)

        return columns