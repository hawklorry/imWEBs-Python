from typing import Any
from sqlalchemy import Column, Integer, Float, String, Double
from .bmp_table import BMPTable

class Reach_BMP(BMPTable):
	"""Location of reach bmps. Note that dugout is not part of the reach bmps"""

	__tablename__ = 'Reach_BMP'
	Scenario = Column(Integer)
	Reach = Column(Integer)
	PointSource = Column(Integer)
	FlowDiversion = Column(Integer)
	Reservoir = Column(Integer)
	Wetland = Column(Integer)
	CatchBasin = Column(Integer)
	GrassWaterway = Column(Integer)
	AccessManagement = Column(Integer)
	WaterUse = Column(Integer)

	def __init__(self):
		self.PointSource = 0
		self.FlowDiversion = 0
		self.Reservoir = 0
		self.Wetland = 0
		self.CatchBasin = 0
		self.GrassWaterway = 0
		self.AccessManagement = 0
		self.WaterUse = 0


