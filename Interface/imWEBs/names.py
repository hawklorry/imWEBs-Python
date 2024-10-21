class Names:
    """
    Default name for input, temp, and output files
    """

    bmp_table_name_reach_bmp = "Reach_BMP"
    bmp_table_name_scenarios = "BMP_scenarios"
    bmp_talbe_name_reach_parameter = "Reach_Parameter"
    bmp_talbe_name_point_source = "point_source"
    bmp_talbe_name_flow_diversion = "flow_diversion"
    bmp_table_name_reservoir = 'reservoir'
    bmp_table_name_riparian_buffer = "riparian_buffer"
    bmp_table_name_grass_waterway = 'grass_waterway'
    bmp_table_name_wetland = "wetland"
    bmp_table_name_crop_management = "crop_management"
    bmp_table_name_crop_parameter = "crop_parameter"
    bmp_table_name_tillage_management = "tillage_management"
    bmp_table_name_tillage_parameter = "tillage_parameter"
    bmp_table_name_fertilizer_management = "fertilizer_management"
    bmp_table_name_fertilizer_parameter = "fertilizer_parameter"
    bmp_table_name_grazing_parameter = "GRAMG_management"
    bmp_table_name_irrigation_management = "irrigation_management"
    bmp_table_name_irrigation_parameter = "irrigation_parameter"
    bmp_table_name_tile_drain_parameter = "tile_drain_parameter"
    bmp_table_name_manure_incorporation_within_48h_management = "manure_incorporation_within_48h_management"
    bmp_table_name_manure_application_setback_management = "manure_application_setback_management"
    bmp_table_name_manure_no_application_on_snow_management = "manure_no_application_on_snow_management"
    bmp_table_name_manure_spring_application_rather_than_fall_application_management = "manure_spring_application_rather_than_fall_application_management"
    bmp_table_name_manure_application_based_on_soil_nitrogen_limit_management = "manure_application_based_on_soil_nitrogen_limit_management"
    bmp_table_name_manure_application_based_on_soil_phosphorous_limit_management = "manure_application_based_on_soil_phosphorous_limit_management"
    bmp_table_name_manure_storage_parameter = "manure_storage_parameter"
    bmp_table_name_manure_storage_management = "manure_storage_management"
    bmp_table_name_manure_catch_basin = "manure_catch_basin"
    bmp_table_name_manure_feed_lot_parameter = "manure_feed_lot_parameter"
    bmp_table_name_manure_feed_lot_management = "manure_feed_lot_management"
    bmp_table_name_wintering_site_parameter = "wintering_site_parameter"
    bmp_table_name_wintering_site_management = "wintering_site_management"
    bmp_table_name_pasture_crop_management = "pasture_crop_management"
    bmp_table_name_pasture_fertilizer_management = "pasture_fertilizer_management"
    bmp_table_name_pasture_tillage_management = "pasture_tillage_management"    
    bmp_table_name_pasture_grazing_management = "pasture_grazing_management"
    bmp_table_name_dugout = "dugout"
    bmp_table_name_offsite_watering = "offsite_watering"
    bmp_table_name_managed_access_including_fencing = "access_management"
    bmp_table_name_wascob = "wascob"
    bmp_table_name_water_use = "water_use"


    field_name_id = "id"
    field_name_subbasin = "subbasin"
    field_name_contibution_area_ha = "con_area"
    field_name_raster_value = "VALUE"
    field_name_area = "AREA"

    #the feedlot column in manure storage layer
    field_name_feedlot = "feedlot"

    #the catch basin column in feedlot
    field_name_catch_basin = "cb"

    #default raster extension
    raster_extension = ".tif"
    shapefile_extension = ".shp"
    csv_extension = ".csv"
    sqlite_extension = ".db3"
    lookup_extension = ".csv"

    #parameter h5
    parameteH5Name = "parameter.h5"

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
    flowDirD8NoChangeName = "flow_dir_no_change" + raster_extension
    flowDirD8Name = "flow_dir" + raster_extension
    flowAccName = "flow_acc" + raster_extension

    # Stream Network
    streamNetworUserShpName = "streamNetworkUser" + shapefile_extension   
    streamNetworUserRasName = streamNetworUserShpName.replace(shapefile_extension, raster_extension)
    
    # streamname = "stream" + shapefile_extension
    # mainStreamRasName = "mainStream" + raster_extension   
    streamMainRasName = "stream_main" + raster_extension
    streamMainShpName = "stream_main" + shapefile_extension 
    streamNetworkRasName = "stream_network" + raster_extension
    streamNetworkShpName = "stream_network" + shapefile_extension
    streamOutletsOriginalShpName = "stream_outlets_original" + shapefile_extension
    streamOutletsOriginalRasName = "stream_outlets_original" + raster_extension
    streamPourPointShpName = "stream_pour_point" + shapefile_extension
    streamPourPointRasName = "stream_pour_point" + raster_extension
    # streamLinkName = "stream_link" + raster_extension
    streamOrderRasName = "stream_order" + raster_extension
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
    PRCName = "potentialRunoffCoefficient" + raster_extension
    DSCName = "depressionStorageCapacity" + raster_extension
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
   
    #point source
    pointSourceShpName = "point_source" + shapefile_extension
    pointSourceRastername = pointSourceShpName.replace(shapefile_extension, raster_extension)

    #flow diversion
    flowDiversionShpName = "flow_diversion" + shapefile_extension
    flowDiversionRastername = flowDiversionShpName.replace(shapefile_extension, raster_extension)


    # Reservoir
    reservoirShpName = "reservoir" + shapefile_extension
    reservoirRasterName = reservoirShpName.replace(shapefile_extension, raster_extension)

    # Catch basin
    catchbasinShpName = "catchbasin" + shapefile_extension
    catchbasinRasName = catchbasinShpName.replace(shapefile_extension, raster_extension)

    #grass waterway
    grassWaterwayShpName = "grass_waterway" + shapefile_extension
    grassWaterwayRasName = grassWaterwayShpName.replace(shapefile_extension, raster_extension)

    #access management
    accessManagementShpName = "access_management" + shapefile_extension
    accessManagementRasName = accessManagementShpName.replace(shapefile_extension, raster_extension)

    #water use
    waterUseShpName = "water_use" + shapefile_extension
    waterUseRasName = waterUseShpName.replace(shapefile_extension, raster_extension)

    # dugout
    dugoutShpName = "dugout" + shapefile_extension
    dugoutRasName = dugoutShpName.replace(shapefile_extension, raster_extension)

    # wascob
    wascobShpName = "wascob" + shapefile_extension
    wascobRasName = wascobShpName.replace(shapefile_extension, raster_extension)

    #Riparian Buffer Strip
    riparianBufferStripShpName = "riparianBufferStrip" + shapefile_extension
    riparianBufferStripRasterName = riparianBufferStripShpName.replace(shapefile_extension, raster_extension)
    riparianBufferStripPartRasterName = "riparianBufferStripPart" + raster_extension
    riparianBufferStripDrainageRasterName = "riparianBufferStripDrainage" + raster_extension
    riparianBufferParameterCSVName = "riparianBufferStrip" + csv_extension

    #tile drain
    tileDrainShpName = "tile_drain" + shapefile_extension
    tileDrainRasName = tileDrainShpName.replace(shapefile_extension, raster_extension)

    # Cattle Feedlot
    feedlotShpName = "feedlot" + shapefile_extension
    feedlotRasName = feedlotShpName.replace(shapefile_extension, raster_extension)
    feedlotOutletShpName = "feedlot_outlet" + shapefile_extension
    feedlotOutletRasName = feedlotOutletShpName.replace(shapefile_extension, raster_extension)

    # Manure Storage - MSCD
    manureStorageShpName = "manure_storage" + shapefile_extension
    manureStorageRasName = manureStorageShpName.replace(shapefile_extension, raster_extension)

    # offsite wintering - OFSW
    offsiteWinteringShpName = "offsiteWintering" + shapefile_extension

    #structures
    structureCombinedBoundaryShpName = "structureCombinedBoundary" + shapefile_extension
    structureCombinedOutputShpName = "structureCombinedOutlet" + shapefile_extension

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


    


    #Pasture
    pastureLandRasName = "PasCropland" + raster_extension
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
    marCroplandRasName = "MarCropland" + raster_extension
    # marCroplandShpName = "MarCropland" + shapefile_extension
    # marCroplandH5RasterName = "MarCropland_H5" + raster_extension

    #standard names
    config_item_standard_name_lookup = {
        #watershed
        "dem_raster": demName,
        "soil_raster": soilName,
        "landuse_raster": landuseName,
        "stream_shapefile": streamNetworUserShpName,
        "boundary_shapefile": boundaryShpName,
        "farm_shapefile": farmShpName,
        "field_shapefile": fieldShpName,
        "outlet_shapefile": outletName,

        #lookup tables
        "soil_lookup":soilLookupName,
        "landuse_lookup":landuseLookupName,

        #db3 database
        "hydroclimate":hydroclimateDatabasename,

        #reach bmp
        "point_source_shapefile": pointSourceShpName,
        "flow_diversion_shapefile": flowDiversionShpName,
        "reservoir_shapefile": reservoirShpName,
        "wetland_boundary_shapefile": wetlandShpName,
        "wetland_outlet_shapefile": wetlandOutletsUserShpName,
        "manure_catch_basin_shapefile" : catchbasinShpName,
        "grass_waterway_shapefile": grassWaterwayShpName,
        "access_management_shapefile":accessManagementShpName,
        "water_use_shapefile": waterUseShpName,

        #structure_bmp
        "dugout_boundary_shapefile":dugoutShpName,
        "wascob_boundary_shapefile":wascobShpName,
        "riparian_buffer_shapefile":riparianBufferStripShpName,
        "tile_drain_shapefile":tileDrainShpName,

        #areal non-structure bmp
        "manure_feedlot_boundary_shapefile": feedlotShpName,
        "manure_feedlot_outlet_shapefile": feedlotOutletShpName,
        "manure_storage_boundary_shapefile": manureStorageShpName
    }

    def get_standard_file_name(item_name:str)->str:
        if item_name in Names.config_item_standard_name_lookup:
            return Names.config_item_standard_name_lookup[item_name]
        
        raise ValueError(f"{item_name} is not a valide name for standard file name.")

