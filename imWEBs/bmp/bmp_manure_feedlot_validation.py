from dataclasses import dataclass

from whitebox_workflows import Vector

from ..names import Names
from ..vector_extension import VectorExtension


@dataclass(frozen=True)
class ManureValidationIssue:
    fields: tuple[str, ...]
    message: str


class ManureFeedlotCatchBasinStorageValidator:
    FIELD_CATCH_BASIN = "manure_catch_basin_shapefile"
    FIELD_FEEDLOT_BOUNDARY = "manure_feedlot_boundary_shapefile"
    FIELD_FEEDLOT_OUTLET = "manure_feedlot_outlet_shapefile"
    FIELD_STORAGE_BOUNDARY = "manure_storage_boundary_shapefile"

    @staticmethod
    def _is_empty_reference(value) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed == "" or trimmed == "0"
        return value == 0

    @staticmethod
    def _append_issue(
        issues: list[ManureValidationIssue],
        fields: tuple[str, ...],
        message: str,
    ) -> None:
        issues.append(ManureValidationIssue(fields=fields, message=message))

    @staticmethod
    def validate_issues(
        catch_basin_vector: Vector = None,
        feedlot_boundary_vector: Vector = None,
        feedlot_outlet_vector: Vector = None,
        manure_storage_boundary_vector: Vector = None,
    ) -> list[ManureValidationIssue]:
        issues: list[ManureValidationIssue] = []

        if feedlot_boundary_vector is None:
            if feedlot_outlet_vector is not None:
                ManureFeedlotCatchBasinStorageValidator._append_issue(
                    issues,
                    (
                        ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_BOUNDARY,
                        ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_OUTLET,
                    ),
                    "Manure Feedlot Boundary Shapefile is required when Manure Feedlot Outlet Shapefile is provided.",
                )
            if manure_storage_boundary_vector is not None:
                ManureFeedlotCatchBasinStorageValidator._append_issue(
                    issues,
                    (
                        ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_BOUNDARY,
                        ManureFeedlotCatchBasinStorageValidator.FIELD_STORAGE_BOUNDARY,
                    ),
                    "Manure Feedlot Boundary Shapefile is required when Manure Storage Boundary Shapefile is provided.",
                )
            return issues

        try:
            VectorExtension.check_fields_in_vector(feedlot_boundary_vector, Names.fields_feedlot)
        except Exception as exc:
            ManureFeedlotCatchBasinStorageValidator._append_issue(
                issues,
                (ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_BOUNDARY,),
                str(exc),
            )
            return issues

        try:
            feedlot_ids = set(VectorExtension.get_unique_ids(feedlot_boundary_vector))
        except Exception as exc:
            ManureFeedlotCatchBasinStorageValidator._append_issue(
                issues,
                (ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_BOUNDARY,),
                str(exc),
            )
            return issues

        if feedlot_outlet_vector is not None:
            try:
                feedlot_outlet_ids = set(VectorExtension.get_unique_ids(feedlot_outlet_vector))
            except Exception as exc:
                ManureFeedlotCatchBasinStorageValidator._append_issue(
                    issues,
                    (ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_OUTLET,),
                    str(exc),
                )
                feedlot_outlet_ids = None

            if feedlot_outlet_ids is not None:
                missing_outlets = sorted(feedlot_ids - feedlot_outlet_ids)
                extra_outlets = sorted(feedlot_outlet_ids - feedlot_ids)
                if missing_outlets or extra_outlets:
                    ManureFeedlotCatchBasinStorageValidator._append_issue(
                        issues,
                        (
                            ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_BOUNDARY,
                            ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_OUTLET,
                        ),
                        "The ids in manure feedlot boundary and manure feedlot outlet do not match. "
                        "Each feedlot should have only one feedlot outlet.",
                    )

        if catch_basin_vector is not None:
            try:
                catch_basin_ids = set(VectorExtension.get_unique_ids(catch_basin_vector))
                feedlot_catch_basin_ids = VectorExtension.get_unique_field_value(
                    feedlot_boundary_vector,
                    Names.field_name_feedlot_catch_basin,
                )
            except Exception as exc:
                ManureFeedlotCatchBasinStorageValidator._append_issue(
                    issues,
                    (
                        ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_BOUNDARY,
                        ManureFeedlotCatchBasinStorageValidator.FIELD_CATCH_BASIN,
                    ),
                    str(exc),
                )
                catch_basin_ids = None
                feedlot_catch_basin_ids = {}

            if catch_basin_ids is not None:
                missing_catch_basins: list[object] = []
                for catch_basin in feedlot_catch_basin_ids.values():
                    if ManureFeedlotCatchBasinStorageValidator._is_empty_reference(catch_basin):
                        continue
                    if catch_basin not in catch_basin_ids:
                        missing_catch_basins.append(catch_basin)

                if missing_catch_basins:
                    missing_catch_basins = sorted(set(missing_catch_basins))
                    ManureFeedlotCatchBasinStorageValidator._append_issue(
                        issues,
                        (
                            ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_BOUNDARY,
                            ManureFeedlotCatchBasinStorageValidator.FIELD_CATCH_BASIN,
                        ),
                        "Could not find manure catch basin ids referenced by manure feedlot boundary: "
                        f"{missing_catch_basins}.",
                    )

        if manure_storage_boundary_vector is not None:
            try:
                manure_storage_feedlot_ids = VectorExtension.get_unique_field_value(
                    manure_storage_boundary_vector,
                    Names.field_name_feedlot,
                )
            except Exception as exc:
                ManureFeedlotCatchBasinStorageValidator._append_issue(
                    issues,
                    (ManureFeedlotCatchBasinStorageValidator.FIELD_STORAGE_BOUNDARY,),
                    str(exc),
                )
                manure_storage_feedlot_ids = {}

            missing_feedlots: list[object] = []
            for feedlot in manure_storage_feedlot_ids.values():
                if ManureFeedlotCatchBasinStorageValidator._is_empty_reference(feedlot):
                    continue
                if feedlot not in feedlot_ids:
                    missing_feedlots.append(feedlot)

            if missing_feedlots:
                missing_feedlots = sorted(set(missing_feedlots))
                ManureFeedlotCatchBasinStorageValidator._append_issue(
                    issues,
                    (
                        ManureFeedlotCatchBasinStorageValidator.FIELD_FEEDLOT_BOUNDARY,
                        ManureFeedlotCatchBasinStorageValidator.FIELD_STORAGE_BOUNDARY,
                    ),
                    "Could not find manure feedlot ids referenced by manure storage boundary: "
                    f"{missing_feedlots}.",
                )

        return issues

    @staticmethod
    def validate(
        catch_basin_vector: Vector = None,
        feedlot_boundary_vector: Vector = None,
        feedlot_outlet_vector: Vector = None,
        manure_storage_boundary_vector: Vector = None,
    ):
        issues = ManureFeedlotCatchBasinStorageValidator.validate_issues(
            catch_basin_vector=catch_basin_vector,
            feedlot_boundary_vector=feedlot_boundary_vector,
            feedlot_outlet_vector=feedlot_outlet_vector,
            manure_storage_boundary_vector=manure_storage_boundary_vector,
        )
        if not issues:
            return

        messages = [issue.message for issue in issues]
        raise ValueError("\n".join(messages))
