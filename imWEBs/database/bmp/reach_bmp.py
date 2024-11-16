from ...bmp.bmp_type import DefaultScenarioId

class ReachBMPDistribution:
	"""Location of reach bmps. Note that dugout is not part of the reach bmps"""

	def __init__(self, reach):
		self.Scenario = DefaultScenarioId
		self.Reach = reach		
		self.PointSource = 0
		self.FlowDiversion = 0
		self.Reservoir = 0
		self.Wetland = 0
		self.CatchBasin = 0
		self.GrassWaterway = 0
		self.AccessManagement = 0
		self.WaterUse = 0

