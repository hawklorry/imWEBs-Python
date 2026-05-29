from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from html import escape
from pathlib import Path
import re
from typing import Sequence


@dataclass(frozen=True)
class FieldDefinition:
    section: str
    name: str
    label: str
    kind: str = "text"
    help_text: str = ""
    relative_to_input: bool = False
    options: Sequence[str] = ()
    required: bool = False
    file_filter: str = "All Files (*)"


FALLBACK_FIELD_HELP_TEXTS: dict[tuple[str, str], str] = {
    ("default", "input_folder"): "Folder containing the model input files. File references in the config are read from this folder.",
    ("watershed", "dem_raster"): "DEM raster file in GeoTIFF format.",
    ("watershed", "soil_raster"): "Soil raster file in GeoTIFF format.",
    ("watershed", "landuse_raster"): "Landuse raster file in GeoTIFF format.",
    ("watershed", "stream_shapefile"): "Stream shapefile used to burn streams into the DEM.",
    ("watershed", "boundary_shapefile"): "Optional watershed boundary shapefile used to limit the watershed extent.",
    ("watershed", "farm_shapefile"): "Optional farm shapefile.",
    ("watershed", "field_shapefile"): "Field shapefile used for field-level delineation.",
    ("watershed", "outlet_shapefile"): "Optional outlet shapefile.",
    ("lookup", "soil_lookup"): "CSV lookup mapping soil raster IDs to imWEBs soil IDs.",
    ("lookup", "landuse_lookup"): "CSV lookup mapping landuse raster IDs to imWEBs landuse IDs.",
    ("parameter", "SoilLookup"): "CSV parameter table used by the soil lookup stage.",
    ("database", "hydroclimate"): "Hydroclimate SQLite database in the current imWEBs format.",
    ("reach_bmp", "point_source_shapefile"): "Point source point shapefile.",
    ("reach_bmp", "flow_diversion_shapefile"): "Flow diversion point shapefile.",
    ("reach_bmp", "reservoir_shapefile"): "Reservoir point shapefile.",
    ("reach_bmp", "wetland_boundary_shapefile"): "Wetland boundary polygon shapefile.",
    ("reach_bmp", "wetland_outlet_shapefile"): "Optional wetland outlet point shapefile.",
    ("reach_bmp", "manure_catch_basin_shapefile"): "Manure catch basin point shapefile.",
    ("reach_bmp", "grass_waterway_shapefile"): "Grass waterway shapefile.",
    ("reach_bmp", "access_management_shapefile"): "Access management shapefile.",
    ("reach_bmp", "water_use_shapefile"): "Water use shapefile.",
    ("structure_bmp", "dugout_boundary_shapefile"): "Dugout boundary shapefile.",
    ("structure_bmp", "riparian_buffer_shapefile"): "Riparian buffer shapefile.",
    ("structure_bmp", "filter_strip_shapefile"): "Vegetation filter strip shapefile.",
    ("structure_bmp", "tile_drain_boundary_shapefile"): "Tile drain boundary shapefile.",
    ("structure_bmp", "tile_drain_outlet_shapefile"): "Tile drain outlet shapefile.",
    ("structure_bmp", "wascob_shapefile"): "WASCOB shapefile.",
    ("non_structure_bmp", "manure_feedlot_boundary_shapefile"): "Feedlot boundary shapefile.",
    ("non_structure_bmp", "manure_feedlot_outlet_shapefile"): "Feedlot outlet shapefile.",
    ("non_structure_bmp", "manure_storage_boundary_shapefile"): "Manure storage boundary shapefile.",
    ("non_structure_bmp", "offsite_watering_shapefile"): "Offsite watering shapefile.",
    ("reservoir", "reservoir_flow_routing"): "Reservoir flow routing method. Supported values include RAT_RES, MDO_RES, MMO_RES, AAR_RES and TRR_RES.",
    ("reservoir", "reservoir_flow_data_folder"): "Folder containing external reservoir flow CSV files when the selected routing method needs them.",
    ("delineation", "stream_threshold_area_ha"): "Threshold area for stream delineation in hectares.",
    ("delineation", "use_all_pour_points_from_stream_threshold"): "If enabled, use all pour points from the stream threshold and structures. If disabled, a coarser threshold is used.",
    ("delineation", "wetland_min_area_ha"): "Minimum wetland area in hectares. Smaller wetlands are ignored.",
    ("marginal_crop_land", "marginal_crop_land_simulation"): "Enable marginal crop land characterization.",
    ("marginal_crop_land", "marginal_crop_land_shapefile"): "Optional marginal crop land shapefile.",
    ("marginal_crop_land", "marginal_crop_land_non_agriculture_landuse_ids"): "Comma-separated landuse IDs treated as non-agriculture.",
    ("marginal_crop_land", "marginal_crop_land_buffer_size_m"): "Buffer distance in metres for marginal crop land characterization.",
    ("marginal_crop_land", "marginal_crop_land_slope_threshold_percentage"): "Slope threshold percentage for marginal crop land characterization.",
    ("marginal_crop_land", "marginal_crop_land_grass_type"): "Grass type ID used when marginal crop land is created.",
    ("pasture_crop_land", "pasture_crop_land_simulation"): "Enable pasture crop land characterization.",
    ("pasture_crop_land", "pasture_crop_land_shapefile"): "Optional pasture crop land shapefile.",
    ("pasture_crop_land", "pasture_crop_land_landuse_ids"): "Comma-separated landuse IDs treated as pasture.",
    ("pasture_crop_land", "pasture_crop_land_grass_type"): "Grass type ID used for pasture crop land.",
    ("manure_adjustment_bmp", "manure_adjustment_incorporation_within_48h_shapefile"): "Shapefile for incorporation within 48 hours manure adjustment areas.",
    ("manure_adjustment_bmp", "manure_adjustment_application_setback_shapefile"): "Shapefile for manure application setback areas.",
    ("manure_adjustment_bmp", "manure_adjustment_no_application_on_snow_shapefile"): "Shapefile for no-application-on-snow areas.",
    ("manure_adjustment_bmp", "manure_adjustment_spring_rather_than_fall_shapefile"): "Shapefile for spring-rather-than-fall manure application areas.",
    ("manure_adjustment_bmp", "manure_adjustment_based_on_n_limit_shapefile"): "Shapefile for nitrogen-limited manure adjustment areas.",
    ("manure_adjustment_bmp", "manure_adjustment_based_on_p_limit_shapefile"): "Shapefile for phosphorus-limited manure adjustment areas.",
    ("crop_rotation", "method"): "Crop rotation generation method. Currently only crop_inventory is supported.",
    ("crop_rotation", "AAFC_crop_inventory_folder"): "Folder containing AAFC crop inventory rasters, typically named by year such as 1991.tif.",
    ("crop_rotation", "first_year"): "First year to include in the crop rotation sequence.",
    ("crop_rotation", "last_year"): "Last year to include in the crop rotation sequence.",
    ("crop_rotation", "include_grazing"): "Include grazing management when generating crop rotation tables.",
    ("model", "model_folder"): "Folder where the model files will be created.",
    ("scenario", "name"): "Scenario name. A subfolder with this name is created under the model folder.",
    ("scenario", "model_type"): "Scenario model type: cell or subarea.",
    ("scenario", "interval"): "Simulation time interval: daily or hourly.",
    ("scenario", "start_date"): "Simulation start date in yyyy-mm-dd format. Leave empty to use the earliest date in the hydroclimate database.",
    ("scenario", "end_date"): "Simulation end date in yyyy-mm-dd format. Leave empty to use the latest date in the hydroclimate database.",
    ("climate_station", "P"): "Comma-separated precipitation station IDs. Leave empty to use all available stations.",
    ("climate_station", "T"): "Comma-separated temperature station IDs. Leave empty to use all available stations.",
    ("climate_station", "RM"): "Comma-separated relative humidity station IDs. Leave empty to use all available stations.",
    ("climate_station", "SR"): "Comma-separated solar radiation station IDs. Leave empty to use all available stations.",
    ("climate_station", "WS"): "Comma-separated wind speed station IDs. Leave empty to use all available stations.",
    ("climate_station", "WD"): "Comma-separated wind direction station IDs. Leave empty to use all available stations.",
    ("climate_interpolation", "method"): "Interpolation method used to build weight files: average_uniform, grid_interpolation, inverse_distance, linear_triangle or thiessen_polygon.",
    ("climate_interpolation", "radius"): "Interpolation search radius used by methods that require a distance threshold.",
}


DOC_SECTION_NAMES = {
    "default",
    "watershed",
    "lookup",
    "database",
    "reach_bmp",
    "structure_bmp",
    "non_structure_bmp",
    "reservoir",
    "delineation",
    "marginal_crop_land",
    "pasture_land",
    "crop_rotation",
    "model",
    "scenario",
    "climate_station",
    "climate_interpolation",
}


DOC_FIELD_ALIASES: dict[tuple[str, str], tuple[str, str]] = {
    ("marginal_crop_land", "marginal_crop_land_non_agriculture_landuse_ids"): ("marginal_crop_land", "non_agriculture_landuse_ids"),
    ("marginal_crop_land", "marginal_crop_land_buffer_size_m"): ("marginal_crop_land", "buffer_size_m"),
    ("marginal_crop_land", "marginal_crop_land_slope_threshold_percentage"): ("marginal_crop_land", "slope_threshold_percentage"),
    ("pasture_crop_land", "pasture_crop_land_landuse_ids"): ("pasture_land", "non_agriculture_landuse_ids"),
}


def _normalize_heading(heading: str) -> str:
    return heading.strip().lower().replace(" ", "_")


@lru_cache(maxsize=1)
def _load_doc_help_texts() -> dict[tuple[str, str], str]:
    repo_root = Path(__file__).resolve().parents[2]
    doc_paths = [
        repo_root / "docs" / "user-guide" / "model_config.qmd",
        repo_root / "docs" / "user-guide" / "scenario_config.qmd",
    ]
    bullet_pattern = re.compile(r"^-\s+\*\*(?P<field>[^*]+)\*\*\s*-\s*(?P<description>.+)$")
    help_texts: dict[tuple[str, str], str] = {}

    for doc_path in doc_paths:
        if not doc_path.exists():
            continue
        current_section: str | None = None
        for line in doc_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("## "):
                heading = _normalize_heading(stripped[3:])
                if heading in DOC_SECTION_NAMES:
                    current_section = heading
                continue

            if current_section is None:
                continue

            match = bullet_pattern.match(line)
            if match is None:
                continue

            field_name = match.group("field").strip()
            description = match.group("description").strip()
            help_texts[(current_section, field_name)] = description

    return help_texts


def _field_kind_summary(field: FieldDefinition) -> str:
    if field.kind == "folder":
        return "Select a folder path."
    if field.kind == "file":
        if field.file_filter != "All Files (*)":
            return f"Select a file matching: {field.file_filter.split(';;')[0]}."
        return "Select a file path."
    if field.kind == "bool":
        return "Choose yes/true to enable it or no/false to disable it."
    if field.kind == "date":
        return "Use yyyy-mm-dd format. Leave empty when the scenario should use the database date range."
    if field.options:
        return f"Choose one of: {', '.join(field.options)}."
    return "Enter the value directly."


def get_field_help_text(field: FieldDefinition) -> str:
    doc_key = DOC_FIELD_ALIASES.get((field.section, field.name), (field.section, field.name))
    help_text = _load_doc_help_texts().get(doc_key, "")
    if not help_text:
        help_text = FALLBACK_FIELD_HELP_TEXTS.get((field.section, field.name), "")
    if help_text:
        return help_text

    if field.kind == "folder":
        return f"Select the folder for {field.label.lower()}."
    if field.kind == "file":
        return f"Select the file for {field.label.lower()}."
    if field.kind == "bool":
        return f"Enable or disable {field.label.lower()}."
    if field.kind == "date":
        return f"Enter {field.label.lower()} in yyyy-mm-dd format or leave it empty when allowed."
    return f"Value for {field.label.lower()}."


def get_field_help_html(field: FieldDefinition) -> str:
    help_text = get_field_help_text(field)
    details = [
        f"<p><b>Section:</b> {escape(field.section)}</p>",
        f"<p><b>Required:</b> {'Yes' if field.required else 'No'}</p>",
        f"<p>{escape(_field_kind_summary(field))}</p>",
    ]
    return (
        f"<h3>{escape(field.label)}</h3>"
        f"<p>{escape(help_text)}</p>"
        + "".join(details)
    )


MODEL_FIELDS = [
    FieldDefinition("default", "input_folder", "Input Folder", "folder", required=True),
    FieldDefinition("watershed", "dem_raster", "DEM Raster", "file", relative_to_input=True, required=True, file_filter="Raster Files (*.tif *.tiff);;All Files (*)"),
    FieldDefinition("watershed", "soil_raster", "Soil Raster", "file", relative_to_input=True, required=True, file_filter="Raster Files (*.tif *.tiff);;All Files (*)"),
    FieldDefinition("watershed", "landuse_raster", "Landuse Raster", "file", relative_to_input=True, required=True, file_filter="Raster Files (*.tif *.tiff);;All Files (*)"),
    FieldDefinition("watershed", "stream_shapefile", "Stream Shapefile", "file", relative_to_input=True, required=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("watershed", "boundary_shapefile", "Boundary Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("watershed", "farm_shapefile", "Farm Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("watershed", "field_shapefile", "Field Shapefile", "file", relative_to_input=True, required=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("watershed", "outlet_shapefile", "Outlet Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("lookup", "soil_lookup", "Soil Lookup", "file", relative_to_input=True, required=True, file_filter="CSV Files (*.csv);;All Files (*)"),
    FieldDefinition("lookup", "landuse_lookup", "Landuse Lookup", "file", relative_to_input=True, required=True, file_filter="CSV Files (*.csv);;All Files (*)"),
    FieldDefinition("parameter", "SoilLookup", "Parameter SoilLookup", "file", relative_to_input=True, required=True, file_filter="CSV Files (*.csv);;All Files (*)"),
    FieldDefinition("database", "hydroclimate", "Hydroclimate Database", "file", relative_to_input=True, required=True, file_filter="Database Files (*.db3 *.db *.sqlite *.sqlite3);;All Files (*)"),
    FieldDefinition("reach_bmp", "point_source_shapefile", "Point Source Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reach_bmp", "flow_diversion_shapefile", "Flow Diversion Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reach_bmp", "reservoir_shapefile", "Reservoir Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reach_bmp", "wetland_boundary_shapefile", "Wetland Boundary Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reach_bmp", "wetland_outlet_shapefile", "Wetland Outlet Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reach_bmp", "manure_catch_basin_shapefile", "Manure Catch Basin Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reach_bmp", "grass_waterway_shapefile", "Grass Waterway Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reach_bmp", "access_management_shapefile", "Access Management Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reach_bmp", "water_use_shapefile", "Water Use Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("structure_bmp", "dugout_boundary_shapefile", "Dugout Boundary Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("structure_bmp", "riparian_buffer_shapefile", "Riparian Buffer Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("structure_bmp", "filter_strip_shapefile", "Filter Strip Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("structure_bmp", "tile_drain_boundary_shapefile", "Tile Drain Boundary Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("structure_bmp", "tile_drain_outlet_shapefile", "Tile Drain Outlet Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("structure_bmp", "wascob_shapefile", "WASCOB Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("non_structure_bmp", "manure_feedlot_boundary_shapefile", "Manure Feedlot Boundary Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("non_structure_bmp", "manure_feedlot_outlet_shapefile", "Manure Feedlot Outlet Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("non_structure_bmp", "manure_storage_boundary_shapefile", "Manure Storage Boundary Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("non_structure_bmp", "offsite_watering_shapefile", "Offsite Watering Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("reservoir", "reservoir_flow_routing", "Reservoir Flow Routing", options=("RAT_RES", "MDO_RES", "MMO_RES", "AAR_RES", "TRR_RES")),
    FieldDefinition("reservoir", "reservoir_flow_data_folder", "Reservoir Flow Data Folder", "folder", relative_to_input=True),
    FieldDefinition("delineation", "stream_threshold_area_ha", "Stream Threshold Area (ha)", "text", required=True),
    FieldDefinition("delineation","use_all_pour_points_from_stream_threshold","Use All Threshold Pour Points","bool"),
    FieldDefinition("delineation", "wetland_min_area_ha", "Wetland Minimum Area (ha)", "text", required=False),
    FieldDefinition("marginal_crop_land", "marginal_crop_land_simulation", "Marginal Crop Land Simulation", "bool"),
    FieldDefinition("marginal_crop_land", "marginal_crop_land_shapefile", "Marginal Crop Land Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("marginal_crop_land", "marginal_crop_land_non_agriculture_landuse_ids", "Non-Agriculture Landuse IDs"),
    FieldDefinition("marginal_crop_land", "marginal_crop_land_buffer_size_m", "Buffer Size (m)"),
    FieldDefinition("marginal_crop_land", "marginal_crop_land_slope_threshold_percentage", "Slope Threshold (%)"),
    FieldDefinition("marginal_crop_land", "marginal_crop_land_grass_type", "Grass Type"),
    FieldDefinition("pasture_crop_land", "pasture_crop_land_simulation", "Pasture Crop Land Simulation", "bool"),
    FieldDefinition("pasture_crop_land", "pasture_crop_land_shapefile", "Pasture Crop Land Shapefile", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("pasture_crop_land", "pasture_crop_land_landuse_ids", "Pasture Landuse IDs"),
    FieldDefinition("pasture_crop_land", "pasture_crop_land_grass_type", "Pasture Grass Type"),
    FieldDefinition("manure_adjustment_bmp", "manure_adjustment_incorporation_within_48h_shapefile", "Incorporation Within 48h", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("manure_adjustment_bmp", "manure_adjustment_application_setback_shapefile", "Application Setback", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("manure_adjustment_bmp", "manure_adjustment_no_application_on_snow_shapefile", "No Application On Snow", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("manure_adjustment_bmp", "manure_adjustment_spring_rather_than_fall_shapefile", "Spring Rather Than Fall", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("manure_adjustment_bmp", "manure_adjustment_based_on_n_limit_shapefile", "Based On N Limit", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("manure_adjustment_bmp", "manure_adjustment_based_on_p_limit_shapefile", "Based On P Limit", "file", relative_to_input=True, file_filter="Shapefiles (*.shp);;All Files (*)"),
    FieldDefinition("crop_rotation", "method", "Crop Rotation Method", options=("crop_inventory",)),
    FieldDefinition("crop_rotation", "AAFC_crop_inventory_folder", "AAFC Crop Inventory Folder", "folder"),
    FieldDefinition("crop_rotation", "first_year", "First Year"),
    FieldDefinition("crop_rotation", "last_year", "Last Year"),
    FieldDefinition("crop_rotation", "include_grazing", "Include Grazing", "bool"),
    FieldDefinition("model", "model_folder", "Model Folder", "folder", required=True),
]


SCENARIO_FIELDS = [
    FieldDefinition("model", "model_folder", "Model Folder", "folder", required=True),
    FieldDefinition("scenario", "name", "Scenario Name", required=True),
    FieldDefinition("scenario", "model_type", "Model Type", options=("cell", "subarea"), required=True),
    FieldDefinition("scenario", "interval", "Interval", options=("daily", "hourly"), required=True),
    FieldDefinition("scenario", "start_date", "Start Date", "date"),
    FieldDefinition("scenario", "end_date", "End Date", "date"),
    FieldDefinition("climate_station", "P", "Precipitation Station IDs"),
    FieldDefinition("climate_station", "T", "Temperature Station IDs"),
    FieldDefinition("climate_station", "RM", "Relative Humidity Station IDs"),
    FieldDefinition("climate_station", "SR", "Solar Radiation Station IDs"),
    FieldDefinition("climate_station", "WS", "Wind Speed Station IDs"),
    FieldDefinition("climate_station", "WD", "Wind Direction Station IDs"),
    FieldDefinition(
        "climate_interpolation",
        "method",
        "Interpolation Method",
        options=(
            "average_uniform",
            "grid_interpolation",
            "inverse_distance",
            "linear_triangle",
            "thiessen_polygon",
        ),
        required=True,
    ),
    FieldDefinition("climate_interpolation", "radius", "Interpolation Radius"),
]


RUN_ACTIONS = {
    "Generate All": "generate_all",
    "Delineate Watershed": "delineate_watershed",
    "Generate Parameters": "generate_parameters",
    "Update Crop Rotation": "update_crop_rotation",
    "Generate Scenario": "generate_scenario",
    "Generate Subarea Parameter Database": "generate_subarea_parameter_database",
    "Generate Pour Points": "generate_pour_points_based_on_threshold_and_structures",
}
