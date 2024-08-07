class Names:
    """
    Default name for input, temp, and output files
    """

    #default raster extension
    raster_extension = ".tif"
    shapefile_extension = ".shp"
    sqlite_extension = ".db3"
    lookup_extension = ".csv"

    #database
    hydroclimateDatabasename = "hydroclimate" + sqlite_extension
    bmpDatabaseName = "bmp" + sqlite_extension
    parameterDatabaseName = "parameter" + sqlite_extension

    # Lookup
    soilLookupName = "soilLookup" + lookup_extension
    landuseLookupName = "landuseLookup" + lookup_extension

    # DEM
    demName = "dem" + raster_extension
    demClippedName = "demClipped" + raster_extension
    demBurnedName = "demClippedBurned" + raster_extension
    demFilledName = "demClippedBurnedFilled" + raster_extension

    # Mask
    boundaryShpName = "boundary" + shapefile_extension
    maskRasName = "mask" + raster_extension
    maskRefindedWithSubbasinRasName = "maskRefinedWithSubbasin" + raster_extension

    # Flow Direction and Accumulation
    flowDirD8Name = "flow_dir" + raster_extension
    flowAccName = "flow_acc" + raster_extension

    # Stream Network
    streamNetworUserShpName = "streamNetworkUser" + shapefile_extension   
    streamNetworUserRasName = streamNetworUserShpName.replace(shapefile_extension, raster_extension)
    
    # streamname = "stream" + shapefile_extension
    # mainStreamRasName = "mainStream" + raster_extension    
    streamNetworkRasName = "stream_network" + raster_extension
    streamNetworkShpName = "stream_network" + shapefile_extension
    streamOutletsShpName = "stream_outlets" + shapefile_extension
    streamOutletsRasName = "stream_outlets" + raster_extension
    # streamLinkName = "stream_link" + raster_extension
    # streamOrderName = "stream_order" + raster_extension
    # streamOrderShpName = "stream_order" + shapefile_extension
    # streamSlopeName = "streamSlope" + raster_extension
    # streamDemName = "streamDem" + raster_extension
    # streamDegreeName = "streamDegree" + raster_extension

    # Reach
    reachRasName = "reach" + raster_extension 
    reachShpName = "reach" + shapefile_extension 

    # Slope
    slopeDegName = "slopeDeg" + raster_extension
    slopeRadiusName = "slopeRadius" + raster_extension

    # parameters
    PRCName = "PRC" + raster_extension
    DSCName = "DSC" + raster_extension
    cn2Name = "cn2" + raster_extension
    PRCAccAvgName = "PRC_Acc_Avg" + raster_extension
    DSCAccAvgName = "DSC_Acc_Avg" + raster_extension
    Cn2AccAvgName = "CN2_Acc_Avg" + raster_extension
    flowLengthName = "flow_le" + raster_extension
    usleKName = "usleK" + raster_extension
    uslePName = "usleP" + raster_extension
    usleCName = "usleC" + raster_extension
    densityName = "density" + raster_extension
    sandName = "sand" + raster_extension
    clayName = "clay" + raster_extension    
    wetnessIndexName = "WTI" + raster_extension
    depressionName = "depression" + raster_extension
    residualName = "residual" + raster_extension
    residualIntMaxName = "residualIntMax" + raster_extension
    residualIntMinName = "residualIntMin" + raster_extension
    runoffCoeffName = "runoffCoeff" + raster_extension
    porosityName = "porosity" + raster_extension
    fieldCapName = "fieldcap" + raster_extension
    poreIndexName = "poreIndex" + raster_extension
    wiltingPointName = "wiltingPoint" + raster_extension
    moistureInitialName = "Moist_in" + raster_extension
    reachDepthName = "depth" + raster_extension
    reachWidthName = "width" + raster_extension
    manningName = "manning" + raster_extension
    velocityName = "velocity" + raster_extension

    landuseSoilName = "landuseSoil" + raster_extension
    landuseSoil1Name = "landuseSoil1" + raster_extension
    streamWaterName = "streamWater" + raster_extension
    weightName = "weight" + raster_extension
    travelTimeHillT0Name = "travelTimeHillT0" + raster_extension
    travelTimeStreamT0Name = "travelTimeStreamT0" + raster_extension
    travelTimeHillDeltaName = "travelTimeHillDelta" + raster_extension
    travelTimeStreamDeltaName = "travelTimeStreamDelta" + raster_extension
    reachParameterFileName = "reachParameter" + ".txt"
    slopeLengthName = "slopeLength" + raster_extension
    rootDepthName = "rootDepth" + raster_extension
    coverFractionName = "coverFraction" + raster_extension
    distance2StreamName = "dist_stream" + raster_extension

    windDirSlopeName = "windDirSlope" + raster_extension
    windDirCurvaName = "windDirCurva" + raster_extension
    conductivityName = "conductivity" + raster_extension    

    # Subbasin
    subbasinRasName = "subbasin" + raster_extension
    subbasinShpName = "subbasin" + shapefile_extension
    # subbasinTempRasName = "subbasinTemp" + raster_extension
    # subbasinTempShpName = "subbasinTemp" + shapefile_extension

    # Soil 
    soilName = "soil" + raster_extension
    soilMappedName = "soilMapped" + raster_extension
    #soilUserName = "soilUser" + raster_extension

    # Landuse
    landuseName = "landuse" + raster_extension
    landuseMappedName = "landuseMapped" + raster_extension
    #landuseUserName = "landuseUser" + raster_extension

    # Farm
    farmShpName = "farm" + shapefile_extension
    farmRasName = farmShpName.replace(shapefile_extension, raster_extension)
    farmWithOnlyAgricultureRasName = "farmWithOnlyAgriCulture" + raster_extension
    

    # Field
    fieldShpName = "field" + shapefile_extension
    fieldRasName = fieldShpName.replace(shapefile_extension, raster_extension)
    fiedWithOnlyAgricultureRasName = "fiedWithOnlyAgriCulture" + raster_extension

    # Outlets
    insertOutletShpName = "insertOutlet" + shapefile_extension
    insertOutletTempShpName = "insertOutletTemp" + shapefile_extension
    insertOutletRasName = "insertOutlet" + raster_extension
    mainOutletsName = "mainOutlets" + shapefile_extension
    outletName = "outlet" + shapefile_extension
    watershedOutletsName = "watershedOutlets" + raster_extension
    streamOutletsName = "streamOutlets" + raster_extension
    streamOutletsWithInsertsName = "streamOutletsWithInserts" + raster_extension
    insertOutletsName = "insertOutlets"
    combinedOutletsName = "combinedOutlets"
    flowDirD8FinalName = "flow_dir"

    # Reservoir
    reservoirShpName = "reservoir" + shapefile_extension
    reservoirRasterName = reservoirShpName.replace(shapefile_extension, raster_extension)

    # Manure Storage - MSCD
    manureStorageShpName = "manureStorage" + shapefile_extension
    manureStorageName = manureStorageShpName.replace(shapefile_extension, raster_extension)
    manureStorageOutletUserShpName = "manureStorageOutletUser" + shapefile_extension

    # Catch basin
    catchbasinShpName = "catchbasin" + shapefile_extension
    catchbasinRasName = catchbasinShpName.replace(shapefile_extension, raster_extension)
    catchbasinOutletUserShpName = "catchbasinOutletUser" + shapefile_extension

    # dugout
    dugoutShpName = "dugout" + shapefile_extension
    dugoutRasName = dugoutShpName.replace(shapefile_extension, raster_extension)
    dugoutOutletUserShpName = "dugoutOutletUser" + shapefile_extension

    # Cattle Feedlot
    feedlotShpName = "feedlot" + shapefile_extension
    feedlotRasName = feedlotShpName.replace(shapefile_extension, raster_extension)
    feedlotOutletUserShpName = "feedlotOutletUser" + shapefile_extension

    # offsite wintering - OFSW
    offsiteWinteringShpName = "offsiteWintering" + shapefile_extension

    # Wetland
    wetlandShpName = "wetland" + shapefile_extension
    wetlandName = "wetland" + raster_extension
    wetlandInactName = "wetlandInact" + raster_extension
    wetlandAlteredName = "wetlandAltered" + raster_extension
    wetlandDrainAlteredName = "wetlandDrainAltered" + raster_extension
    wetlandDrainLostName = "wetlandDrainLost" + raster_extension
    wetlandClassTypeName = "wetlandClassType" + raster_extension
    wetlandDrainConsolidatedName = "wetlandDrainConsolidated" + raster_extension
    wetlandD8Temp1Name = "wetlandD8Temp1" + raster_extension
    wetlandD8Temp2Name = "wetlandD8Temp2" + raster_extension
    wetlandD8FinalName = "wetlandD8Final" + raster_extension
    wetlandFlowAccTemp1Name = "wetlandFlowAccTemp1" + raster_extension
    wetlandFlowAccTemp2Name = "wetlandFlowAccTemp2" + raster_extension
    wetlandFlowAccFinalName = "wetlandFlowAccFinal" + raster_extension
    wetlandStreamNetTemp1Name = "wetlandStreamNetTemp1" + raster_extension
    wetlandStreamNetTemp1ShpName = "wetlandStreamNetTemp1" + shapefile_extension #
    wetlandStreamNetTemp2Name = "wetlandStreamNetTemp2" + raster_extension
    wetlandStreamNetTemp3Name = "wetlandStreamNetTemp3" + raster_extension
    wetlandStreamNetUserName = "wetlandStreamNetUser" + raster_extension
    wetlandOutletsName = "wetlandOutlets" + raster_extension
    wetlandOutletsUserRasName = "wetlandOutletsUser" + raster_extension    
    wetlandOutletsUserShpName = "wetlandOutletsUser" + shapefile_extension
    wetlandInletRipaName = "wetlandInletRipa" + raster_extension
    wetlandEndNodesName = "wetlandEndNodes" + raster_extension
    wetlandStreamLinkName = "wetlandStreamLink" + raster_extension
    wetlandStreamLinkShpName = "wetlandStreamLink" + shapefile_extension
    wetlandIsoMOutName = "wetlandIsoMOut" + raster_extension
    wetlandIso1OutName = "wetlandIso1Out" + raster_extension
    wetlandIsolateName = "wetlandIsolate" + raster_extension 
    wetlandIsolateShpName = "wetlandIsolate" + shapefile_extension 
    wetlandRipaOutShpName = "wetlandRipaOut" + shapefile_extension 
    wetlandRipaOutName = "wetlandRipaOut" + raster_extension
    wetlandMdfyName = "wetlandMdfy" + raster_extension
    wetlandMdfyShpName = "wetlandMdfy" + shapefile_extension
    wetlandMdfyDissolveShpName = "wetlandMdfyDissolve" + shapefile_extension
    wetlandMdfyDissolvePointsShpName = "wetlandMdfyDissolvePoints" + shapefile_extension
    wetlandMdfyNewIDName = "wetlandMdfyNewID" + raster_extension
    wetlandMdfyNewIDShpName = "wetlandMdfyNewID" + shapefile_extension
    wetlandMdfyNewIDDissolveShpName = "wetlandMdfyNewIDDissolve" + shapefile_extension
    wetlandMdfyNewIDDissolvePointsShpName = "wetlandMdfyNewIDDissolvePoints" + shapefile_extension
    wetlandSubbasinName = "wetlandSubbasin" + raster_extension
    wetlandSubbasinNoWetName = "wetlandSubbasinNoWet" + raster_extension
    wetlandSubbasinWithWetName = "wetlandSubbasinWithWet" + raster_extension
    wetlandSubbasinNoWetShpName = "wetlandSubbasinNoWet" + shapefile_extension
    wetlandSubbasinWithWetShpName = "wetlandSubbasinWithWet" + shapefile_extension
    wetlandInfoName = "WetlandInfo" + ".csv"
    wetlandExtentName = "wetlandExtent" + raster_extension
    wetlandFlowDirMdfyName = "wetlandFlowDirMdfy" + raster_extension
    wetlandUpstreamName = "wetlandUpstream" + raster_extension

    #Wintering Site    
    winteringSiteShpName = "winteringSite" + shapefile_extension
    winteringSiteRasterName = winteringSiteShpName.replace(shapefile_extension,raster_extension)

    #Vegetation Filter Strip    
    vegetationFilterStripShpName = "vegetationFilterStrip" + shapefile_extension
    vegetationFilterStripRasterName = vegetationFilterStripShpName.replace(shapefile_extension, raster_extension)
    # vegetationFilterStripPartRasterName = "vegetationFilterStripPart" + raster_extension
    # vegetationFilterStripPartShpName = "vegetationFilterStripPart" + shapefile_extension
    # vegetationFilterStripDrainageRasterName = "vegetationFilterStripDrainage" + raster_extension
    # vegetationFilterStripDrainageShpName = "vegetationFilterStripDrainage" + shapefile_extension

    #Riparian Buffer Strip
    riparianBufferStripShpName = "riparianBufferStrip" + shapefile_extension
    riparianBufferStripRasterName = riparianBufferStripShpName.replace(shapefile_extension, raster_extension)
    
    # riparianBufferStripPartRasterName = "riparianBufferStripPart" + raster_extension
    # riparianBufferStripPartShpName = "riparianBufferStripPart" + shapefile_extension
    # riparianBufferStripDrainageRasterName = "riparianBufferStripDrainage" + raster_extension
    # riparianBufferStripDrainageShpName = "riparianBufferStripDrainage" + shapefile_extension

    #Pasture
    # pastureLandRasterName = "PasCropland" + raster_extension
    # pastureLandShpName = "PasCropland" + shapefile_extension
    # pastureLandH5RasterName = "PasCropland_H5" + raster_extension

    #Pasture grazing
    pastureGrazingRasterName = "pastureGrazing" + raster_extension
    pastureGrazingShpName = "pastureGrazing" + shapefile_extension

    #Manure Setback
    # manureSetbackShpName = "manureSetback" + shapefile_extension
    # manureSetbackUserName = "manureSetbackUser" + raster_extension

    # streamNetworkNoFieldName = "streamNetworkNoField" + raster_extension
    # averageDistanceToStreamName = "averageDistanceToStream" + raster_extension
    # averageSlopeToStreamName = "averageSlopeToStream" + raster_extension


    # grWaterSourceRasterName = "grWaterSource" + raster_extension
    # grAccessMgtRasterName = "grAccessMgt" + raster_extension
    # grazingRedistributionRasterName = "GrazingRedistribution" + raster_extension
    # grazingOffsiteWateringRasterName = "GrazingOffsiteWatering" + raster_extension

    #Marginal Crop Land
    # marCroplandRasterName = "MarCropland" + raster_extension
    # marCroplandShpName = "MarCropland" + shapefile_extension
    # marCroplandH5RasterName = "MarCropland_H5" + raster_extension

