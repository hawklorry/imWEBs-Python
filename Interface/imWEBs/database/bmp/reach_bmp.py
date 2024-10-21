from typing import Any
from sqlalchemy import Column, Integer, Float, String, Double
from .bmp_table import BMPTable
from ...names import Names

class ReachBMPDistribution(BMPTable):
	"""Location of reach bmps. Note that dugout is not part of the reach bmps"""

	__tablename__ = Names.table_name_reach_bmp
	Scenario = Column(Integer)
	Reach = Column(Integer)
	PointSource = Column(Integer)
	FlowDiversion = Column(Integer)
	Reservoir = Column(Integer)
	Wetland = Column(Integer)
	CatchBasin = Column(Integer)
	GrassWaterway = Column(Integer)
	Dugout = Column(Integer)
	AccessManagement = Column(Integer)
	WaterUse = Column(Integer)

	def __init__(self, reach):
		self.Reach = reach
		self.Scenario = -1
		self.PointSource = 0
		self.FlowDiversion = 0
		self.Reservoir = 0
		self.Wetland = 0
		self.CatchBasin = 0
		self.GrassWaterway = 0
		self.AccessManagement = 0
		self.WaterUse = 0

