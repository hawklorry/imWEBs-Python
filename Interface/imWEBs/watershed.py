
# Calculate Watershed Parameters
# 1. Waterhsed.buildWatershedParametersMaps
#     a. Generate mask with subbasin,Landuse and Soil. And copy it as USLEP raster. 
#     b. Calculate parameters with Customized Plugins - Done need some examples
#         1) StreamWidth
#         2) getReachDepthRaster
#         3) ReclassLookup for fc1 and manning
#         4) Velocity
#         5) WetlandIndex
#         6) SoilMoistureInitial
#     c. Watershed.BuildReachParTable - Junzhi Students
#     d. buildDSCRaster
#     e. buildDSCAccumulateAvgMap
#     f. buildCN2Raster
#     g. buildCN2AccumulateAvgMap
#     h. getFieldIDnAreas
#     i. getFarmIDnAreas
#     j. getSubbasinIDnAreas
#     k. createSpatialTables
#     l. buildBMPParMgtTables
#     m. Build livestock parameter table
#     n. Build manure_and_nutrient_parameter table
#     o. Build LS_parameter table
#     p. Build BMP index table
#     q. Build subbasin multiplier table    r. 
# 2. Watersehd.createManureSetbackMap
#     a.ExtractStreams
#     b.ExcludeStreamInField
#     c.AverageSlopeToStream
#     d.createManureSetbackMap

from whitebox_workflows import Raster
from names import inputs, outputs

class watershed:
    def __init__(self, input_folder:str, output_folder:str) -> None:
        self.outputs = outputs(output_folder, input_folder)

    def lookupValues(self, inputRaster:Raster, lookup:dict) -> Raster:
        """
        Replace the raster values based on lookup table. The application could be

        1. generate field capacity raster based on soil lookup table
        2. generate manning raster based on landuse lookup table
        3. 
        
        Parameters:
        inputRaster         : the input raster
        mask                : mask raster
        lookup              : lookup table assuming the input value is the key and output value is the value   
        """

        pass

    def getSlopeRadius(self, slopeDeg:Raster)->Raster:
        return (slopeDeg * math.pi / 180).tan()

    def calculateReachVelocity(self, manning:Raster, slopeRadius:Raster, streamDepth:Raster, mask:Raster, min:float = 0.005, max: float = 3) -> Raster:
        """
        Calculate full reach velocity using Manning equation

        Parameters:
        manning             : Manning raster
        slopeDeg            : Slope raster in degree. Could use radius instead
        streamDepth         : Stream depth raster
        mask                : mask raster
        min                 : min velocity
        max                 : max velocity

        """
        velocity = slopeRadius.sqrt() * streamDepth**0.6667 / manning
        return velocity.min(max).max(min)

    def calculateWetnessIndex(self, flowAcc:Raster, slopeRadius:Raster, mask:Raster)->Raster:
        """
        Calculate wetness index using flow accumulation and slope
        """

        return (flowAcc * getRasterCellAreaM2(mask)).log() / slopeRadius.tan()

    def calculateIntialSoilMoisture(self, wetnessIndex:Raster, fieldCapacity:Raster, mask:Raster, minSaturation:float=0.05, maxSaturation:float=1)->Raster:
        """
        Calculate the initial soil moisture using linear interpolation
        """

        minWetnessIndex = wetnessIndex.configs.minimum
        maxWetnessIndex = wetnessIndex.configs.maximum * 0.8

        wti = wetnessIndex.max(maxWetnessIndex)
        ratio = (wti - minWetnessIndex) * (maxSaturation - minSaturation) / (maxWetnessIndex - minWetnessIndex) + minSaturation
        return ratio * fieldCapacity

    def buildReachParameterTable():
        pass

    def calculatePotentialRunoffCoefficient(self, lope:Raster, mask:Raster, landuse:Raster, soil:Raster, reach:Raster, flowDirectionD8:Raster, reachWidth:dict)->Raster:
        
        #calculate reach water surface fraction
        #need to find a quick way to do lookup
        reachWaterSurfaceFraction = this.getReachWidth(reachID) / mask.configs.resolution_x    
        reachWaterSurfaceFraction = flowDirectionD8.con("(value == 1) || (value ==4) || (value == 8) || (value ==16)", 1.41421356 * reachWaterSurfaceFraction - 0.5 * reachWaterSurfaceFraction * reachWaterSurfaceFraction, reachWaterSurfaceFraction)

    def getPotentialRunoffCoefficient(landuseId:int, soilId:int, slope:float, reachFraction:float, landuseParameterLookup:pd.DataFrame, soilParameterLookup:pd.DataFrame):
        """
        
        Soid Id -> Soil Texture (1-12
        LanUse Id -> PRC_ST1, ..., PRC_ST12 where ST is for soil texture
        """



