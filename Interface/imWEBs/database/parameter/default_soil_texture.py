from sqlalchemy import Column, Integer, Float, String
from .parameter_table import ParameterTable

class DefaultSoilTexture(ParameterTable):
    __tablename__ = 'DefaultSoilTexture'
    TextureID = Column(Integer, primary_key=True)
    TextureClass = Column(String)
    Class = Column(String)
    HydraulicConductivity = Column(Float)
    Porosity = Column(Float)
    FieldCapacity = Column(Float)
    WiltingPoint = Column(Float)
    ResidualMoisture = Column(Float)
    PoreSizeDistributionIndex = Column(Integer)