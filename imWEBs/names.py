class Names:
    """
    Default name for input, temp, and output files
    """
    
    bmp_table_name_bmp_index = "bmp_index"
    bmp_table_name_scenarios = "bmp_scenarios"

    #reach bmps
    bmp_table_name_reach_lookup = "reach_lookup"
    bmp_table_name_reach_parameter = "reach_parameter"
    bmp_table_name_reach_bmp = "reach_bmp"
    bmp_table_name_point_source = "reach_bmp_point_source"
    bmp_table_name_flow_diversion = "reach_bmp_flow_diversion"
    bmp_table_name_reservoir = 'reach_bmp_reservoir'
    bmp_table_name_wetland = "reach_bmp_wetland"
    bmp_table_name_manure_catch_basin = "reach_bmp_manure_catch_basin"
    bmp_table_name_grass_waterway = 'reach_bmp_grass_waterway'    
    bmp_table_name_managed_access_including_fencing = "reach_bmp_access_management"
    bmp_table_name_water_use = "reach_bmp_water_use"

    #structure bmps
    bmp_table_name_dugout = "structure_bmp_dugout"    
    bmp_table_name_riparian_buffer = "structure_bmp_riparian_buffer"    
    bmp_table_name_filter_strip = "structure_bmp_filter_strip"    
    bmp_table_name_tile_drain = "structure_bmp_tile_drain"
    bmp_table_name_wascob = "structure_bmp_wascob"
    bmp_table_name_outlet_drainage = "outlet_drainage" #fixed name

    #areal non-structure
    bmp_table_name_crop_management = "non_structure_bmp_crop_management"
    bmp_table_name_crop_parameter = "non_structure_bmp_crop_parameter"
    bmp_table_name_crop_remove_parameter = "non_structure_bmp_crop_remove_parameter"
    bmp_table_name_tillage_management = "non_structure_bmp_tillage_management"
    bmp_table_name_tillage_parameter = "non_structure_bmp_tillage_parameter"
    bmp_table_name_fertilizer_management = "non_structure_bmp_fertilizer_management"
    bmp_table_name_fertilizer_parameter = "fertilizer_parameter"
    bmp_table_name_grazing_management = "GRAMG_management"
    bmp_table_name_livestock_parameter = "livestock_parameter"
    bmp_table_name_irrigation_management = "non_structure_bmp_irrigation_management"
    bmp_table_name_irrigation_parameter = "non_structure_bmp_irrigation_parameter"
    bmp_table_name_manure_storage_parameter = "non_structure_bmp_manure_storage_parameter"
    bmp_table_name_manure_storage_management = "non_structure_bmp_manure_storage_management"    
    bmp_table_name_manure_feed_lot_parameter = "non_structure_bmp_manure_feed_lot_parameter"
    bmp_table_name_manure_feed_lot_management = "non_structure_bmp_manure_feed_lot_management"
    bmp_table_name_wintering_site_parameter = "non_structure_bmp_wintering_site_parameter"
    bmp_table_name_wintering_site_management = "non_structure_bmp_wintering_site_management"
    bmp_table_name_marginal_crop_management = "non_structure_bmp_marginal_crop_management"
    bmp_table_name_marginal_fertilizer_management = "non_structure_bmp_marginal_fertilizer_management"
    bmp_table_name_marginal_tillage_management = "non_structure_bmp_marginal_tillage_management"    
    bmp_table_name_pasture_crop_management = "non_structure_bmp_pasture_crop_management"
    bmp_table_name_pasture_fertilizer_management = "non_structure_bmp_pasture_fertilizer_management"
    bmp_table_name_pasture_tillage_management = "non_structure_bmp_pasture_tillage_management"    
    bmp_table_name_pasture_grazing_management = "non_structure_bmp_pasture_grazing_management"
    bmp_table_name_pasture_grazing_parameter = "non_structure_bmp_pasture_grazing_parametert"
    
    #manure appication adjustment
    bmp_table_name_manure_incorporation_within_48h_management = "manure_adjustment_incorporation_within_48h_management"
    bmp_table_name_manure_application_setback_management = "manure_adjustment_application_setback_management"
    bmp_table_name_manure_no_application_on_snow_management = "manure_adjustment_no_application_on_snow_management"
    bmp_table_name_manure_spring_application_rather_than_fall_application_management = "manure_adjustment_spring_application_rather_than_fall_application_management"
    bmp_table_name_manure_application_based_on_soil_nitrogen_limit_management = "manure_adjustment_application_based_on_soil_nitrogen_limit_management"
    bmp_table_name_manure_application_based_on_soil_phosphorous_limit_management = "manure_adjustment_application_based_on_soil_phosphorous_limit_management"

    

    #other tables
    bmp_table_name_ls_parameter = "LS_parameter"

    bmp_table_name_farm_info = "farm_info"
    bmp_table_name_field_info = "field_info"
    bmp_table_name_field_farm = "field_farm"
    bmp_table_name_farm_subbasin = "farm_subbasin"
    bmp_table_name_field_subbasin = "field_subbasin"
    bmp_table_name_subbasin_info = "subbasin_info"
    bmp_table_name_subbasin_multiplier = "subbasin_multiplier"

    #subarea - all fixed names, don't change
    bmp_table_name_subarea = "Subarea"
    bmp_table_name_subarea_soil = "SubareaSoilType"
    bmp_table_name_subarea_landuse = "SubareaLandUseType"
    bmp_table_name_subarea_cell = "CellSubarea"

    bmp_table_name_subarea_riparian_buffer_lookup = "SubareaRiparianBufferLookup"
    bmp_table_name_subarea_vegetative_filter_strip_lookup = "SubareaVegetativeFilterStripLookup"
    bmp_table_name_subarea_feedlot_lookup = "SubareaFeedlotLookup"
    bmp_table_name_subarea_manure_storage_lookup = "SubareaManureStorageLookup"

    bmp_table_name_subarea_riparian_buffer_drainage_lookup = "SubareaRiparianBufferDrainageLookup"
    bmp_table_name_subarea_vegetative_filter_strip_drainage_lookup = "SubareaVegetativeFilterStripDrainageLookup"
    bmp_table_name_subarea_feedlot_drainage_lookup = "SubareaFeedlotDrainageLookup"
    bmp_table_name_subarea_wascob_drainage_lookup = "SubareaWascobDrainageLookup"
    bmp_table_name_subarea_tile_drain_drainage_lookup = "SubareaTileDrainLookup"



    #
    bmp_table_name_offsite_watering = "offsite_watering"

    #----------------------------------------------------------------------------

    field_name_id = "id"
    field_name_subbasin = "subbasin"
    field_name_contibution_area_ha = "con_area"
    field_name_raster_value = "VALUE"
    field_name_area = "AREA"

    #the feedlot column in manure storage layer
    field_name_feedlot = "feedlot"

    #feedlot shapefile
    field_name_feedlot_catch_basin = "cb"
    field_name_feedlot_animal_id = "ani_id"
    field_name_feedlot_adult = "adult"
    field_name_feedlot_non_adult = "nonadult"
    field_name_feedlot_storage_ids = "stoid"
    field_name_feedlot_storage_ratios = "storatio"
    fields_feedlot = [
            field_name_feedlot_catch_basin,
            field_name_feedlot_animal_id,
            field_name_feedlot_adult,
            field_name_feedlot_non_adult,
            field_name_feedlot_storage_ids,
            field_name_feedlot_storage_ratios 
    ]


    #-------------------------------------------------------------------------------

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
    parameterSubareaDatabaseName = "parameter_subarea" + sqlite_extension

    # Lookup
    soilLookupName = "soil_id_lookup" + lookup_extension
    landuseLookupName = "landuse_id_lookup" + lookup_extension

    # parameter
    parameterSoilLookupName = "SoilLookup" + lookup_extension

    # DEM
    demName = "dem" + raster_extension
    demClippedName = "demClipped" + raster_extension
    demBurnedName = "demClippedBurned" + raster_extension
    demFilledName = "demClippedBurnedFilled" + raster_extension

    # Mask
    boundaryShpName = "boundary" + shapefile_extension
    maskRasName = "mask_before_subbasin_refinement" + raster_extension
    maskRefindedWithSubbasinRasName = "mask" + raster_extension #don't change the name as it will be the base for parameter.h5

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
    streamThresholdRasName = "stream_threshold" + raster_extension
    streamNetworkRasName = "stream_network" + raster_extension
    streamNetworkShpName = "stream_network" + shapefile_extension
    streamPourPointShpName = "stream_pour_point" + shapefile_extension
    streamPourPointRasName = "stream_pour_point" + raster_extension
    streamPourPointThresholdShpName = "stream_pour_point_threshold" + shapefile_extension
    streamOrderRasName = "stream_order" + raster_extension

    # Reach
    reachRasName = "reach" + raster_extension 
    reachShpName = "reach" + shapefile_extension 
    reachParameterCsvName = bmp_table_name_reach_parameter + csv_extension
    reachParameterTxtName = "reachParameter.txt"
    reachDepthName = "reach_depth" + raster_extension
    reachWidthName = "reach_width" + raster_extension

    # Slope
    slopeDegName = "slopeDeg" + raster_extension
    slopeRadiusName = "slopeRadius" + raster_extension
    slopePercentName = "Slope" + raster_extension

    # parameters
    PRCName = "potentialRunoffCoefficient" + raster_extension
    DSCName = "depressionStorageCapacity" + raster_extension
    cn2Name = "cn2" + raster_extension
    PRCAccAvgName = "PRC_Acc_Avg" + raster_extension
    DSCAccAvgName = "DSC_Acc_Avg" + raster_extension
    Cn2AccAvgName = "CN2_Acc_Avg" + raster_extension
    flowLengthName = "flow_length" + raster_extension
    usleKName = "USLE_K" + raster_extension
    uslePName = "USLE_P" + raster_extension
    usleCName = "USLE_C" + raster_extension
    densityName = "density" + raster_extension
    sandName = "sand" + raster_extension
    clayName = "clay" + raster_extension    
    wetnessIndexName = "wetness_index" + raster_extension
    depressionName = "depression" + raster_extension
    residualName = "residual" + raster_extension
    residualIntMaxName = "residualIntMax" + raster_extension
    residualIntMinName = "residualIntMin" + raster_extension
    runoffCoeffName = "runoffCoeff" + raster_extension
    porosityName = "porosity" + raster_extension
    fieldCapName = "field_capacity" + raster_extension
    poreIndexName = "pore_index" + raster_extension
    wiltingPointName = "wilting_point" + raster_extension

    #fixed name, don't change
    moistureInitialName = "Moist_in" + raster_extension 

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

    # Soil 
    soilName = "soil" + raster_extension
    soilMappedName = "soilMapped" + raster_extension

    # Landuse
    landuseName = "landuse" + raster_extension
    landuseMappedOriginalName = "landuseMappedOriginal" + raster_extension

    # Farm
    farmShpName = "farm" + shapefile_extension
    farmRasName = farmShpName.replace(shapefile_extension, raster_extension)
    farmWithOnlyAgricultureRasName = "farmWithOnlyAgriCulture" + raster_extension    

    # Field
    fieldShpName = "field" + shapefile_extension
    fieldRasName = fieldShpName.replace(shapefile_extension, raster_extension)
    fieldOriginalRasName = "fieldOriginal" + raster_extension
    fieldClippedShpName = "fieldClipped" + shapefile_extension
    fiedWithOnlyAgricultureRasName = "fiedWithOnlyAgriCulture" + raster_extension

    # management unit
    subareaShpName = "subarea" + shapefile_extension
    subareaRasName = subareaShpName.replace(shapefile_extension, raster_extension)

    #



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
    wascobDrainageAreaRasName = "wascob_drainage_area" + raster_extension

    #Riparian Buffer
    riparianBufferShpName = "riparian_buffer" + shapefile_extension
    riparianBufferRasterName = riparianBufferShpName.replace(shapefile_extension, raster_extension)
    riparianBufferPartRasterName = "riparian_buffer_part" + raster_extension
    riparianBufferDrainageRasterName = "riparian_buffer_drainage" + raster_extension
    riparianBufferParameterCSVName = "riparian_buffer_parameter" + csv_extension

    #filter strip
    filterStripShpName = "filter_strip" + shapefile_extension
    filterStripRasterName = filterStripShpName.replace(shapefile_extension, raster_extension)
    filterStripPartRasterName = "filter_strip_part" + raster_extension
    filterStripDrainageRasterName = "filter_strip_drainage" + raster_extension
    filterStripParameterCSVName = "filter_strip_parameter" + csv_extension

    #Vegetation Filter Strip    
    vegetationFilterStripShpName = "vegetationFilterStrip" + shapefile_extension
    vegetationFilterStripRasterName = vegetationFilterStripShpName.replace(shapefile_extension, raster_extension)
    # vegetationFilterStripPartRasterName = "vegetationFilterStripPart" + raster_extension
    # vegetationFilterStripPartShpName = "vegetationFilterStripPart" + shapefile_extension
    # vegetationFilterStripDrainageRasterName = "vegetationFilterStripDrainage" + raster_extension
    # vegetationFilterStripDrainageShpName = "vegetationFilterStripDrainage" + shapefile_extension

    #tile drain
    tileDrainShpName = "tile_drain" + shapefile_extension
    tileDrainOutletShpName = "tile_drain_outlet" + shapefile_extension
    tileDrainRasName = tileDrainShpName.replace(shapefile_extension, raster_extension)
    tileDrainOutletPourPointShpName = "tile_drain_outlet_pour_point" + shapefile_extension
    tileDrainOutletPourPointRasName = tileDrainOutletPourPointShpName.replace(shapefile_extension, raster_extension)

    # Cattle Feedlot
    feedlotShpName = "feedlot" + shapefile_extension    
    feedlotOutletShpName = "feedlot_outlet" + shapefile_extension
    feedlotBoundaryProcessedRasName = "feedlotBoundaryProcessed" + raster_extension

    # Manure Storage - MSCD
    manureStorageShpName = "manure_storage" + shapefile_extension
    manureStorageRasName = manureStorageShpName.replace(shapefile_extension, raster_extension)

    # offsite wintering - fixed name - don't change
    offsiteWinteringShpName = "grazingoffsitewatering" + shapefile_extension
    offsiteWinteringRasName = "grazingoffsitewatering" + raster_extension

    #structures
    structureCombinedBoundaryShpName = "structureCombinedBoundary" + shapefile_extension
    structureCombinedOutputShpName = "structureCombinedOutlet" + shapefile_extension
    structureCombinedOutputRasName = "structureCombinedOutlet" + raster_extension

    # Wetland
    wetlandShpName = "wetland" + shapefile_extension
    wetlandRasName = "wetland" + raster_extension
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

    #Manure Setback
    manure48hShpName = "manure_within_48h" + shapefile_extension
    manure48hRasName = manure48hShpName.replace(shapefile_extension, raster_extension)
    manureSetbackShpName = "manure_setback" + shapefile_extension
    manureSetbackRasName = manureSetbackShpName.replace(shapefile_extension, raster_extension)
    manureNoOnSnowShpName = "manure_no_on_snow" + shapefile_extension
    manureNoOnSnowRasName = manureNoOnSnowShpName.replace(shapefile_extension, raster_extension)
    manureSpringShpName = "manure_spring" + shapefile_extension
    manureSpringRasName = manureSpringShpName.replace(shapefile_extension, raster_extension)
    manureNLimitShpName = "manure_n_limit" + shapefile_extension
    manureNLimitRasname = manureNLimitShpName.replace(shapefile_extension, raster_extension)
    manurePLimitShpName = "manure_p_limit" + shapefile_extension
    manurePLimitRasname = manurePLimitShpName.replace(shapefile_extension, raster_extension)
  
    #iuh
    iuhAverage2yrRasName = "iuh_t0_2yr" + raster_extension
    iuhStandardDeviation2yrRasName = "iuh_delta_2yr" + raster_extension
    iuhAverage10yrRasName = "iuh_t0_10yr" + raster_extension
    iuhStandardDeviation10yrRasName = "iuh_delta_10yr" + raster_extension
    iuhAverage100yrRasName = "iuh_t0_100yr" + raster_extension
    iuhStandardDeviation100yrRasName = "iuh_delta_100yr" + raster_extension


    # streamNetworkNoFieldName = "streamNetworkNoField" + raster_extension
    # averageDistanceToStreamName = "averageDistanceToStream" + raster_extension
    # averageSlopeToStreamName = "averageSlopeToStream" + raster_extension

    # grWaterSourceRasterName = "grWaterSource" + raster_extension
    # grAccessMgtRasterName = "grAccessMgt" + raster_extension
    # grazingRedistributionRasterName = "GrazingRedistribution" + raster_extension
    # grazingOffsiteWateringRasterName = "GrazingOffsiteWatering" + raster_extension

    #Marginal Crop Land
    marginalCroplandShpName = "marginal_crop_land" + shapefile_extension
    marginalCroplandOriginalFieldRasName = "marginal_crop_land_original_field" + raster_extension
    marginalCroplandSeparatedFieldRasName = "marginal_crop_land_separated_field" + raster_extension

    #Pasture crop land
    pastureCropLandShpName = "pasture_crop_land" + shapefile_extension
    pastureCropLandOriginalFieldRasName = "pasture_crop_land_original_field" + raster_extension
    pastureCropLandSeparatedFieldRasName = "pasture_crop_land_separated_field" + raster_extension

    #Pasture grazing
    pastureGrazingRasterName = "pastureGrazing" + raster_extension
    pastureGrazingShpName = "pastureGrazing" + shapefile_extension

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

        #parameters
        "SoilLookup":parameterSoilLookupName,

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
        "riparian_buffer_shapefile":riparianBufferShpName,
        "filter_strip_shapefile":filterStripShpName,
        "wascob_shapefile":wascobShpName,
        "tile_drain_boundary_shapefile":tileDrainShpName,
        "tile_drain_outlet_shapefile":tileDrainOutletShpName,

        #areal non-structure bmp
        "manure_feedlot_boundary_shapefile": feedlotShpName,
        "manure_feedlot_outlet_shapefile": feedlotOutletShpName,
        "manure_storage_boundary_shapefile": manureStorageShpName,
        "offsite_watering_shapefile": offsiteWinteringShpName,

        #margnial and pasture crop land
        "marginal_crop_land_shapefile": marginalCroplandShpName,
        "pasture_crop_land_shapefile": pastureCropLandShpName,

        #manure adjustment bmp
        "manure_adjustment_incorporation_within_48h_shapefile": manure48hShpName,
        "manure_adjustment_application_setback_shapefile": manureSetbackShpName,
        "manure_adjustment_no_application_on_snow_shapefile": manureNoOnSnowShpName,
        "manure_adjustment_spring_rather_than_fall_shapefile": manureSpringShpName,
        "manure_adjustment_based_on_n_limit_shapefile": manureNLimitShpName,
        "manure_adjustment_based_on_p_limit_shapefile": manurePLimitShpName
    }

    @staticmethod
    def get_standard_file_name(item_name:str)->str:
        if item_name in Names.config_item_standard_name_lookup:
            return Names.config_item_standard_name_lookup[item_name]
        
        raise ValueError(f"{item_name} is not a valide name for standard file name.")
    
    @staticmethod
    def remove_extension_from_raster_file(raster_file_name:str)->str:
        return raster_file_name.replace(Names.raster_extension, "")
    

    


