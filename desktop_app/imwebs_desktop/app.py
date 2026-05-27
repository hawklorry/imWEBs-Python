from __future__ import annotations

from collections import OrderedDict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tempfile
import threading
import sys
import time
from typing import Callable

from PySide6.QtCore import QDate, QObject, QThread, Qt, QSize, QTimer, Signal, QUrl, QRect
from PySide6.QtGui import QColor, QPixmap, QDesktopServices, QPainter, QFont, QLinearGradient, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QDialog,
    QFileDialog,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSplashScreen,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from .definitions import MODEL_FIELDS, RUN_ACTIONS, SCENARIO_FIELDS, FieldDefinition, get_field_help_html, get_field_help_text
from .service import ImwebsDesktopService, ProjectManager


def _app_package_root() -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root) / "imwebs_desktop"
    return Path(__file__).resolve().parent


def _app_icon() -> QIcon:
    icon_path = _app_package_root() / "resources" / "app_icon.ico"
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


def _app_logo_pixmap(max_size: int = 96) -> QPixmap:
    logo_path = _app_package_root() / "resources" / "IMWEBsLogo.png"
    if not logo_path.exists():
        return QPixmap()

    pixmap = QPixmap(str(logo_path))
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


class RunWorker(QObject):
    finished = Signal()
    failed = Signal(str)
    log_message = Signal(str)

    def __init__(self, service: ImwebsDesktopService, model_path: str, scenario_path: str, action: str):
        super().__init__()
        self._service = service
        self._model_path = model_path
        self._scenario_path = scenario_path
        self._action = action

    def run(self) -> None:
        try:
            self._service.run_action(
                self._model_path,
                self._scenario_path,
                self._action,
                self.log_message.emit,
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit()


class ModelConfigWorkflowWorker(QObject):
    finished = Signal()
    failed = Signal(str)
    log_message = Signal(str)

    def __init__(self, service: ImwebsDesktopService, model_path: str, action: str):
        super().__init__()
        self._service = service
        self._model_path = model_path
        self._action = action

    def run(self) -> None:
        try:
            self._service.run_model_action(
                self._model_path,
                self._action,
                self.log_message.emit,
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit()


class ScenarioGenerationWorker(QObject):
    finished = Signal()
    failed = Signal(str)
    log_message = Signal(str)

    def __init__(self, service: ImwebsDesktopService, scenario_config_path: str):
        super().__init__()
        self._service = service
        self._scenario_config_path = scenario_config_path

    def run(self) -> None:
        try:
            self._service.generate_scenario_model_structure(
                self._scenario_config_path,
                self.log_message.emit,
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit()


class UpdateCheckWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, service: ImwebsDesktopService, current_version: str):
        super().__init__()
        self._service = service
        self._current_version = current_version

    def run(self) -> None:
        try:
            payload = self._service.check_for_updates(self._current_version)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(payload)


class UpdateDownloadWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, service: ImwebsDesktopService, installer_url: str, installer_name: str):
        super().__init__()
        self._service = service
        self._installer_url = installer_url
        self._installer_name = installer_name

    def run(self) -> None:
        try:
            installer_path = self._service.download_installer(self._installer_url, self._installer_name)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(installer_path)


class DateInput(QWidget):
    value_changed = Signal()

    def __init__(self):
        super().__init__()
        self._has_value = False
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self._on_date_changed)

        clear_button = QPushButton("Clear")
        clear_button.setFixedWidth(52)
        clear_button.clicked.connect(self.clear)

        layout.addWidget(self.date_edit, 1)
        layout.addWidget(clear_button)
        self._sync_visual_state()

    def _on_date_changed(self, _date: QDate) -> None:
        self._has_value = True
        self._sync_visual_state()
        self.value_changed.emit()

    def _sync_visual_state(self) -> None:
        if self._has_value:
            self.date_edit.setStyleSheet("")
            self.date_edit.setToolTip("")
        else:
            self.date_edit.setStyleSheet("color: #64748b;")
            self.date_edit.setToolTip("No date selected. Leave blank to use the database range.")

    def clear(self) -> None:
        self._has_value = False
        self.date_edit.setDate(QDate.currentDate())
        self._sync_visual_state()
        self.value_changed.emit()

    def value(self) -> str:
        if not self._has_value:
            return ""
        return self.date_edit.date().toString("yyyy-MM-dd")

    def set_value(self, value: str) -> None:
        if not value:
            self.clear()
            return
        parsed = QDate.fromString(value, "yyyy-MM-dd")
        if not parsed.isValid():
            parsed = QDate.fromString(value, Qt.ISODate)
        if parsed.isValid():
            self.date_edit.setDate(parsed)
            self._has_value = True
        else:
            self.clear()
        self._sync_visual_state()
        self.value_changed.emit()


class CollapsibleSection(QWidget):
    def __init__(self, title: str, expanded: bool = False):
        super().__init__()
        self._content_builder: Callable[[], None] | None = None
        self._content_built = False
        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(expanded)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.toggle_button.clicked.connect(self._toggle_content)

        self.content_frame = QFrame()
        self.content_frame.setVisible(expanded)

        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(12, 8, 0, 0)
        self.content_layout.setSpacing(10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_frame)

    def set_content_builder(self, builder: Callable[[], None]) -> None:
        self._content_builder = builder
        if self.toggle_button.isChecked():
            self._ensure_content_built()

    def _ensure_content_built(self) -> None:
        if self._content_built or self._content_builder is None:
            return
        self._content_builder()
        self._content_built = True

    def build_content(self) -> None:
        self._ensure_content_built()

    def _toggle_content(self) -> None:
        expanded = self.toggle_button.isChecked()
        if expanded:
            self._ensure_content_built()
        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.content_frame.setVisible(expanded)


class ConfigForm(QWidget):
    def __init__(
        self,
        title: str,
        fields: list[FieldDefinition],
        service: ImwebsDesktopService,
        config_path: str,
        input_folder_provider: Callable[[], str] | None = None,
        group_by_section: bool = True,
        on_change: Callable[[], None] | None = None,
        on_field_change: Callable[[str, str], None] | None = None,
    ):
        super().__init__()
        self._title = title
        self._fields = fields
        self._service = service
        self._config_path = config_path
        self._input_folder_provider = input_folder_provider
        self._group_by_section = group_by_section
        self._on_change = on_change
        self._on_field_change = on_field_change
        self._inputs: dict[tuple[str, str], QWidget] = {}
        self._status_labels: dict[tuple[str, str], QLabel] = {}
        self._pending_values: dict[tuple[str, str], str] = {}
        self._pending_errors: dict[tuple[str, str], str] = {}
        self._sections: list[CollapsibleSection] = []
        self._prefetch_section_index = 0
        self._suspend_path_validation = False

        root_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)

        if self._group_by_section:
            grouped_fields: OrderedDict[str, list[FieldDefinition]] = OrderedDict()
            for field in fields:
                grouped_fields.setdefault(field.section, []).append(field)

            for section, section_fields in grouped_fields.items():
                box = CollapsibleSection(section.replace("_", " ").title(), expanded=False)
                self._sections.append(box)

                def build_section(fields_in_section: list[FieldDefinition] = section_fields, target_box: CollapsibleSection = box) -> None:
                    section_form_widget = QWidget()
                    box_layout = QFormLayout(section_form_widget)
                    box_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
                    for section_field in fields_in_section:
                        widget = self._create_input(section_field)
                        label = section_field.label + (" *" if section_field.required else "")
                        box_layout.addRow(label, widget)
                    target_box.content_layout.addWidget(section_form_widget)

                box.set_content_builder(build_section)
                form_layout.addWidget(box)
        else:
            flat_form = QWidget()
            flat_layout = QFormLayout(flat_form)
            flat_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
            for field in fields:
                widget = self._create_input(field)
                label = field.label + (" *" if field.required else "")
                flat_layout.addRow(label, widget)
            form_layout.addWidget(flat_form)

        form_layout.addStretch(1)
        scroll.setWidget(form_container)
        root_layout.addWidget(scroll, 1)

    def _create_input(self, field: FieldDefinition) -> QWidget:
        help_text = get_field_help_text(field)
        help_html = get_field_help_html(field)
        key = (field.section, field.name)

        if field.kind == "bool":
            combo = QComboBox()
            if field.options:
                combo.addItems(list(field.options))
            else:
                combo.addItems(["Yes", "No"])
            if key == ("marginal_crop_land", "marginal_crop_land_simulation"):
                combo.setCurrentText("No")
            if key == ("pasture_crop_land", "pasture_crop_land_simulation"):
                combo.setCurrentText("No")
            combo.currentTextChanged.connect(lambda _text, f=field: self._on_field_value_changed(f))
            self._inputs[key] = combo
            wrapped = self._wrap_field_widget(field, combo, help_text, help_html, add_status=True)
            if key in self._pending_values:
                self.set_value(field.section, field.name, self._pending_values.pop(key))
            if key in self._pending_errors:
                self._set_field_error(field.section, field.name, self._pending_errors.pop(key))
            self._validate_single_field(field)
            return wrapped

        if field.kind == "date":
            date_input = DateInput()
            date_input.value_changed.connect(lambda f=field: self._on_field_value_changed(f))
            self._inputs[key] = date_input
            wrapped = self._wrap_field_widget(field, date_input, help_text, help_html, add_status=True)
            if key in self._pending_values:
                self.set_value(field.section, field.name, self._pending_values.pop(key))
            if key in self._pending_errors:
                self._set_field_error(field.section, field.name, self._pending_errors.pop(key))
            self._validate_single_field(field)
            return wrapped

        if field.options:
            combo = QComboBox()
            combo.addItem("")
            for option in field.options:
                combo.addItem(option)
            if key == ("climate_interpolation", "method"):
                combo.setCurrentText("inverse_distance")
            if key == ("scenario", "model_type"):
                combo.setCurrentText("subarea")
            if key == ("scenario", "interval"):
                combo.setCurrentText("daily")
            combo.currentTextChanged.connect(lambda _text, f=field: self._on_field_value_changed(f))
            self._inputs[key] = combo
            wrapped = self._wrap_field_widget(field, combo, help_text, help_html, add_status=True)
            if key in self._pending_values:
                self.set_value(field.section, field.name, self._pending_values.pop(key))
            if key in self._pending_errors:
                self._set_field_error(field.section, field.name, self._pending_errors.pop(key))
            self._validate_single_field(field)
            return wrapped

        line_edit = QLineEdit()
        line_edit.setClearButtonEnabled(True)

        if field.kind in {"file", "folder"}:
            browse_button = QPushButton("...")
            browse_button.setFixedWidth(36)
            browse_button.clicked.connect(lambda: self._browse_for_field(field, line_edit))
            self._inputs[key] = line_edit
            line_edit.textChanged.connect(lambda _text, f=field: self._on_field_value_changed(f))
            wrapped = self._wrap_field_widget(field, line_edit, help_text, help_html, browse_button, add_status=True)
            if key in self._pending_values:
                self.set_value(field.section, field.name, self._pending_values.pop(key))
            if key in self._pending_errors:
                self._set_field_error(field.section, field.name, self._pending_errors.pop(key))
            self._validate_single_field(field)
            return wrapped

        line_edit.textChanged.connect(lambda _text, f=field: self._on_field_value_changed(f))
        self._inputs[key] = line_edit
        wrapped = self._wrap_field_widget(field, line_edit, help_text, help_html, add_status=True)
        if key == ("scenario", "name"):
            line_edit.setText("scenario1")
        if key in self._pending_values:
            self.set_value(field.section, field.name, self._pending_values.pop(key))
        if key in self._pending_errors:
            self._set_field_error(field.section, field.name, self._pending_errors.pop(key))
        self._validate_single_field(field)
        return wrapped

    def _wrap_field_widget(
        self,
        field: FieldDefinition,
        main_widget: QWidget,
        help_text: str,
        help_html: str,
        extra_widget: QWidget | None = None,
        add_status: bool = False,
    ) -> QWidget:
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(main_widget, 1)
        if extra_widget is not None:
            layout.addWidget(extra_widget)

        if add_status:
            status_label = QLabel("!")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setFixedSize(18, 18)
            status_label.setStyleSheet(
                "QLabel { color: #ffffff; background: #b91c1c; border-radius: 9px; font-weight: 700; }"
            )
            status_label.hide()
            self._status_labels[(field.section, field.name)] = status_label
            layout.addWidget(status_label)

        info_button = QToolButton()
        info_button.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        info_button.setToolTip(help_text)
        info_button.setAutoRaise(True)
        info_button.clicked.connect(
            lambda checked=False, button=info_button, html=help_html: self._show_help_tooltip(button, html)
        )
        layout.addWidget(info_button)
        return wrapper

    def _show_help_tooltip(self, button: QToolButton, help_html: str) -> None:
        rich_text = (
            "<qt><div style='max-width:560px; white-space:normal;'>"
            f"{help_html}"
            "</div></qt>"
        )
        QToolTip.showText(button.mapToGlobal(button.rect().bottomLeft()), rich_text, button, button.rect(), 25000)

    def _on_field_value_changed(self, field: FieldDefinition) -> None:
        if self._suspend_path_validation:
            return

        key = (field.section, field.name)
        if key == ("reach_bmp", "reservoir_shapefile"):
            reservoir_shapefile = self.get_value("reach_bmp", "reservoir_shapefile").strip()
            routing_method = self.get_value("reservoir", "reservoir_flow_routing").strip()
            if reservoir_shapefile and not routing_method:
                self.set_value("reservoir", "reservoir_flow_routing", "RAT_RES")

        self._validate_single_field(field)
        
        # Reservoir cross-field revalidation
        reservoir_keys = {
            ("reach_bmp", "reservoir_shapefile"),
            ("reservoir", "reservoir_flow_routing"),
            ("reservoir", "reservoir_flow_data_folder"),
        }
        if key in reservoir_keys:
            for section, name in [
                ("reach_bmp", "reservoir_shapefile"),
                ("reservoir", "reservoir_flow_routing"),
                ("reservoir", "reservoir_flow_data_folder"),
            ]:
                dependent_field = next((f for f in self._fields if f.section == section and f.name == name), None)
                if dependent_field is not None:
                    self._validate_single_field(dependent_field)
        
        # Point Source cross-field revalidation
        pointsource_keys = {
            ("reach_bmp", "point_source_shapefile"),
        }
        if key in pointsource_keys:
            dependent_field = next((f for f in self._fields if f.section == "reach_bmp" and f.name == "point_source_shapefile"), None)
            if dependent_field is not None:
                self._validate_single_field(dependent_field)
        
        # Grass Waterway cross-field revalidation
        grasswaterway_keys = {
            ("reach_bmp", "grass_waterway_shapefile"),
        }
        if key in grasswaterway_keys:
            dependent_field = next((f for f in self._fields if f.section == "reach_bmp" and f.name == "grass_waterway_shapefile"), None)
            if dependent_field is not None:
                self._validate_single_field(dependent_field)
        
        # WASCOB cross-field revalidation
        wascob_keys = {
            ("structure_bmp", "wascob_shapefile"),
        }
        if key in wascob_keys:
            dependent_field = next((f for f in self._fields if f.section == "structure_bmp" and f.name == "wascob_shapefile"), None)
            if dependent_field is not None:
                self._validate_single_field(dependent_field)
        
        # Tile Drain cross-field revalidation
        tiledrain_keys = {
            ("structure_bmp", "tile_drain_boundary_shapefile"),
            ("structure_bmp", "tile_drain_outlet_shapefile"),
        }
        if key in tiledrain_keys:
            for section, name in [
                ("structure_bmp", "tile_drain_boundary_shapefile"),
                ("structure_bmp", "tile_drain_outlet_shapefile"),
            ]:
                dependent_field = next((f for f in self._fields if f.section == section and f.name == name), None)
                if dependent_field is not None:
                    self._validate_single_field(dependent_field)

        # Manure feedlot/catch basin/storage cross-field revalidation
        manure_keys = {
            ("reach_bmp", "manure_catch_basin_shapefile"),
            ("non_structure_bmp", "manure_feedlot_boundary_shapefile"),
            ("non_structure_bmp", "manure_feedlot_outlet_shapefile"),
            ("non_structure_bmp", "manure_storage_boundary_shapefile"),
        }
        if key in manure_keys:
            for section, name in [
                ("reach_bmp", "manure_catch_basin_shapefile"),
                ("non_structure_bmp", "manure_feedlot_boundary_shapefile"),
                ("non_structure_bmp", "manure_feedlot_outlet_shapefile"),
                ("non_structure_bmp", "manure_storage_boundary_shapefile"),
            ]:
                dependent_field = next((f for f in self._fields if f.section == section and f.name == name), None)
                if dependent_field is not None:
                    self._validate_single_field(dependent_field)

        # Marginal crop land simulation/shapefile cross-field revalidation
        marginal_keys = {
            ("marginal_crop_land", "marginal_crop_land_simulation"),
            ("marginal_crop_land", "marginal_crop_land_shapefile"),
        }
        if key in marginal_keys:
            for section, name in [
                ("marginal_crop_land", "marginal_crop_land_simulation"),
                ("marginal_crop_land", "marginal_crop_land_shapefile"),
            ]:
                dependent_field = next((f for f in self._fields if f.section == section and f.name == name), None)
                if dependent_field is not None:
                    self._validate_single_field(dependent_field)

        # Pasture crop land simulation dependent revalidation
        pasture_keys = {
            ("pasture_crop_land", "pasture_crop_land_simulation"),
            ("pasture_crop_land", "pasture_crop_land_shapefile"),
            ("pasture_crop_land", "pasture_crop_land_landuse_ids"),
        }
        if key in pasture_keys:
            for section, name in [
                ("pasture_crop_land", "pasture_crop_land_simulation"),
                ("pasture_crop_land", "pasture_crop_land_shapefile"),
                ("pasture_crop_land", "pasture_crop_land_landuse_ids"),
            ]:
                dependent_field = next((f for f in self._fields if f.section == section and f.name == name), None)
                if dependent_field is not None:
                    self._validate_single_field(dependent_field)
        if self._on_field_change is not None:
            self._on_field_change(field.section, field.name)
        if self._on_change is not None:
            self._on_change()

    def _validate_single_field(self, field: FieldDefinition) -> str | None:
        key = (field.section, field.name)
        if key in self._inputs:
            value = self.get_value(field.section, field.name).strip()
        else:
            value = self._pending_values.get(key, "").strip()

        error = self._validate_field_value(field, value)
        if error is None:
            self._clear_field_error(field.section, field.name)
        else:
            self._set_field_error(field.section, field.name, error)
        return error

    def _validate_field_value(self, field: FieldDefinition, value: str) -> str | None:
        def _validate_comma_separated_ints(raw_value: str) -> str | None:
            parts = [part.strip() for part in raw_value.split(",")]
            if any(part == "" for part in parts):
                return "value must be integers separated by comma (for example: 1,2,3)."
            try:
                for part in parts:
                    int(part)
            except ValueError:
                return "value must be integers separated by comma (for example: 1,2,3)."
            return None

        if (field.section, field.name) == ("marginal_crop_land", "marginal_crop_land_shapefile"):
            simulation = self.get_value("marginal_crop_land", "marginal_crop_land_simulation").strip().lower()
            if simulation in {"yes", "true"} and not value:
                return "value is required when Marginal Crop Land Simulation is Yes."

        if (field.section, field.name) == ("pasture_crop_land", "pasture_crop_land_shapefile"):
            simulation = self.get_value("pasture_crop_land", "pasture_crop_land_simulation").strip().lower()
            if simulation in {"yes", "true"} and not value:
                return "value is required when Pasture Crop Land Simulation is Yes."

        if (field.section, field.name) == ("pasture_crop_land", "pasture_crop_land_landuse_ids"):
            simulation = self.get_value("pasture_crop_land", "pasture_crop_land_simulation").strip().lower()
            if simulation in {"yes", "true"} and not value:
                return "value is required when Pasture Crop Land Simulation is Yes."

        if (field.section, field.name) in {
            ("marginal_crop_land", "marginal_crop_land_non_agriculture_landuse_ids"),
            ("pasture_crop_land", "pasture_crop_land_landuse_ids"),
        } and value:
            int_list_error = _validate_comma_separated_ints(value)
            if int_list_error:
                return int_list_error

        if field.section == "climate_station" and value:
            int_list_error = _validate_comma_separated_ints(value)
            if int_list_error:
                return int_list_error

        if (field.section, field.name) == ("reservoir", "reservoir_flow_routing"):
            reservoir_shapefile = self.get_value("reach_bmp", "reservoir_shapefile").strip()
            if reservoir_shapefile and not value:
                return "value is required when Reservoir Shapefile is provided."

        if (field.section, field.name) == ("reservoir", "reservoir_flow_data_folder"):
            routing_method = self.get_value("reservoir", "reservoir_flow_routing").strip()
            methods_requiring_data_folder = {"RAT_RES", "MDO_RES", "MMO_RES"}
            if routing_method in methods_requiring_data_folder and not value:
                return "value is required for selected reservoir flow routing method."

        reservoir_validation_error = self._validate_reservoir_inputs(field)
        if reservoir_validation_error:
            return reservoir_validation_error

        pointsource_validation_error = self._validate_pointsource_inputs(field)
        if pointsource_validation_error:
            return pointsource_validation_error

        grasswaterway_validation_error = self._validate_grasswaterway_inputs(field)
        if grasswaterway_validation_error:
            return grasswaterway_validation_error

        wascob_validation_error = self._validate_wascob_inputs(field)
        if wascob_validation_error:
            return wascob_validation_error

        tiledrain_validation_error = self._validate_tiledrain_inputs(field)
        if tiledrain_validation_error:
            return tiledrain_validation_error

        manure_validation_error = self._validate_manure_feedlot_inputs(field)
        if manure_validation_error:
            return manure_validation_error

        if field.required and not value:
            return "value is required."

        if not value:
            return None

        if field.kind in {"file", "folder"}:
            resolved_path, path_error = self._resolve_field_path(field, value)
            if path_error:
                return path_error
            if field.kind == "file" and not resolved_path.is_file():
                return f"file does not exist ({resolved_path})."
            if field.kind == "folder" and not resolved_path.is_dir():
                return f"folder does not exist ({resolved_path})."
            unique_id_validation_error = self._validate_step4_shapefile_unique_id(field, resolved_path)
            if unique_id_validation_error:
                return unique_id_validation_error
            raster_validation_error = self._validate_raster_against_dem(field, resolved_path)
            if raster_validation_error:
                return raster_validation_error

        return None

    def _validate_reservoir_inputs(self, field: FieldDefinition) -> str | None:
        reservoir_keys = {
            ("reach_bmp", "reservoir_shapefile"),
            ("reservoir", "reservoir_flow_routing"),
            ("reservoir", "reservoir_flow_data_folder"),
        }
        if (field.section, field.name) not in reservoir_keys:
            return None

        reservoir_shapefile = self.get_value("reach_bmp", "reservoir_shapefile").strip()
        if not reservoir_shapefile:
            return None

        reservoir_field = next(
            (f for f in self._fields if f.section == "reach_bmp" and f.name == "reservoir_shapefile"),
            None,
        )
        if reservoir_field is None:
            return None

        reservoir_path, reservoir_path_error = self._resolve_field_path(reservoir_field, reservoir_shapefile)
        if reservoir_path_error:
            return reservoir_path_error
        if not reservoir_path.is_file():
            return f"file does not exist ({reservoir_path})."

        flow_method = self.get_value("reservoir", "reservoir_flow_routing").strip() or None

        flow_data_folder = self.get_value("reservoir", "reservoir_flow_data_folder").strip()
        flow_data_folder_path: str | None = None
        if flow_data_folder:
            flow_data_folder_field = next(
                (f for f in self._fields if f.section == "reservoir" and f.name == "reservoir_flow_data_folder"),
                None,
            )
            if flow_data_folder_field is not None:
                resolved_flow_data_folder, flow_data_folder_error = self._resolve_field_path(flow_data_folder_field, flow_data_folder)
                if flow_data_folder_error:
                    return flow_data_folder_error
                flow_data_folder_path = str(resolved_flow_data_folder)

        try:
            from whitebox_workflows import WbEnvironment
            from imWEBs.bmp.bmp_reach_reservoir import ReachBMPReservoir

            wbe = WbEnvironment()
            reservoir_vector = wbe.read_vector(str(reservoir_path))
            ReachBMPReservoir.validate(
                reservoir_vector,
                flow_method=flow_method,
                flow_data_folder=flow_data_folder_path,
            )
        except Exception as exc:
            return str(exc)

        return None

    def _validate_pointsource_inputs(self, field: FieldDefinition) -> str | None:
        pointsource_keys = {
            ("reach_bmp", "point_source_shapefile"),
        }
        if (field.section, field.name) not in pointsource_keys:
            return None

        pointsource_shapefile = self.get_value("reach_bmp", "point_source_shapefile").strip()
        if not pointsource_shapefile:
            return None

        pointsource_field = next(
            (f for f in self._fields if f.section == "reach_bmp" and f.name == "point_source_shapefile"),
            None,
        )
        if pointsource_field is None:
            return None

        pointsource_path, pointsource_path_error = self._resolve_field_path(pointsource_field, pointsource_shapefile)
        if pointsource_path_error:
            return pointsource_path_error
        if not pointsource_path.is_file():
            return f"file does not exist ({pointsource_path})."

        hydroclimate_db = self.get_value("database", "hydroclimate").strip()
        hydroclimate_path: str | None = None
        if hydroclimate_db:
            hydroclimate_field = next(
                (f for f in self._fields if f.section == "database" and f.name == "hydroclimate"),
                None,
            )
            if hydroclimate_field is not None:
                resolved_db, db_error = self._resolve_field_path(hydroclimate_field, hydroclimate_db)
                if db_error:
                    return db_error
                if not resolved_db.is_file():
                    return f"hydroclimate database file does not exist ({resolved_db})."
                hydroclimate_path = str(resolved_db)

        try:
            from whitebox_workflows import WbEnvironment
            from imWEBs.bmp.bmp_reach_point_source import ReachBMPPointSource
            from imWEBs.database.hydroclimate.hydroclimate_database import HydroClimateDatabase

            wbe = WbEnvironment()
            pointsource_vector = wbe.read_vector(str(pointsource_path))
            hydroclimate_database = None
            if hydroclimate_path:
                hydroclimate_database = HydroClimateDatabase(hydroclimate_path)
            ReachBMPPointSource.validate(pointsource_vector, hydroclimate_database)
        except Exception as exc:
            return str(exc)

        return None

    def _validate_grasswaterway_inputs(self, field: FieldDefinition) -> str | None:
        grasswaterway_keys = {
            ("reach_bmp", "grass_waterway_shapefile"),
        }
        if (field.section, field.name) not in grasswaterway_keys:
            return None

        grasswaterway_shapefile = self.get_value("reach_bmp", "grass_waterway_shapefile").strip()
        if not grasswaterway_shapefile:
            return None

        grasswaterway_field = next(
            (f for f in self._fields if f.section == "reach_bmp" and f.name == "grass_waterway_shapefile"),
            None,
        )
        if grasswaterway_field is None:
            return None

        grasswaterway_path, grasswaterway_path_error = self._resolve_field_path(grasswaterway_field, grasswaterway_shapefile)
        if grasswaterway_path_error:
            return grasswaterway_path_error
        if not grasswaterway_path.is_file():
            return f"file does not exist ({grasswaterway_path})."

        try:
            from whitebox_workflows import WbEnvironment
            from imWEBs.bmp.bmp_reach_grass_waterway import ReachBMPGrassWaterWay

            wbe = WbEnvironment()
            grasswaterway_vector = wbe.read_vector(str(grasswaterway_path))
            ReachBMPGrassWaterWay.validate(grasswaterway_vector)
        except Exception as exc:
            return str(exc)

        return None

    def _validate_wascob_inputs(self, field: FieldDefinition) -> str | None:
        wascob_keys = {
            ("structure_bmp", "wascob_shapefile"),
        }
        if (field.section, field.name) not in wascob_keys:
            return None

        wascob_shapefile = self.get_value("structure_bmp", "wascob_shapefile").strip()
        if not wascob_shapefile:
            return None

        wascob_field = next(
            (f for f in self._fields if f.section == "structure_bmp" and f.name == "wascob_shapefile"),
            None,
        )
        if wascob_field is None:
            return None

        wascob_path, wascob_path_error = self._resolve_field_path(wascob_field, wascob_shapefile)
        if wascob_path_error:
            return wascob_path_error
        if not wascob_path.is_file():
            return f"file does not exist ({wascob_path})."

        try:
            from whitebox_workflows import WbEnvironment
            from imWEBs.bmp.bmp_structure_wascob import StructureBMPWascob

            wbe = WbEnvironment()
            wascob_vector = wbe.read_vector(str(wascob_path))
            StructureBMPWascob.validate(wascob_vector)
        except Exception as exc:
            return str(exc)

        return None

    def _validate_tiledrain_inputs(self, field: FieldDefinition) -> str | None:
        tiledrain_keys = {
            ("structure_bmp", "tile_drain_boundary_shapefile"),
            ("structure_bmp", "tile_drain_outlet_shapefile"),
        }
        if (field.section, field.name) not in tiledrain_keys:
            return None

        tiledrain_boundary = self.get_value("structure_bmp", "tile_drain_boundary_shapefile").strip()
        if not tiledrain_boundary:
            return None

        tiledrain_boundary_field = next(
            (f for f in self._fields if f.section == "structure_bmp" and f.name == "tile_drain_boundary_shapefile"),
            None,
        )
        if tiledrain_boundary_field is None:
            return None

        tiledrain_boundary_path, tiledrain_boundary_error = self._resolve_field_path(tiledrain_boundary_field, tiledrain_boundary)
        if tiledrain_boundary_error:
            return tiledrain_boundary_error
        if not tiledrain_boundary_path.is_file():
            return f"file does not exist ({tiledrain_boundary_path})."

        tiledrain_outlet = self.get_value("structure_bmp", "tile_drain_outlet_shapefile").strip()
        tiledrain_outlet_path: str | None = None
        if tiledrain_outlet:
            tiledrain_outlet_field = next(
                (f for f in self._fields if f.section == "structure_bmp" and f.name == "tile_drain_outlet_shapefile"),
                None,
            )
            if tiledrain_outlet_field is not None:
                resolved_outlet, outlet_error = self._resolve_field_path(tiledrain_outlet_field, tiledrain_outlet)
                if outlet_error:
                    return outlet_error
                if not resolved_outlet.is_file():
                    return f"file does not exist ({resolved_outlet})."
                tiledrain_outlet_path = str(resolved_outlet)

        try:
            from whitebox_workflows import WbEnvironment
            from imWEBs.bmp.bmp_structure_tile_drain import StructureBMPTileDrain

            wbe = WbEnvironment()
            tiledrain_boundary_vector = wbe.read_vector(str(tiledrain_boundary_path))
            tiledrain_outlet_vector = None
            if tiledrain_outlet_path:
                tiledrain_outlet_vector = wbe.read_vector(tiledrain_outlet_path)
            StructureBMPTileDrain.validate(tiledrain_boundary_vector, tiledrain_outlet_vector)
        except Exception as exc:
            return str(exc)

        return None

    def _validate_manure_feedlot_inputs(self, field: FieldDefinition) -> str | None:
        manure_keys = {
            ("reach_bmp", "manure_catch_basin_shapefile"),
            ("non_structure_bmp", "manure_feedlot_boundary_shapefile"),
            ("non_structure_bmp", "manure_feedlot_outlet_shapefile"),
            ("non_structure_bmp", "manure_storage_boundary_shapefile"),
        }
        if (field.section, field.name) not in manure_keys:
            return None

        field_specs = [
            ("reach_bmp", "manure_catch_basin_shapefile"),
            ("non_structure_bmp", "manure_feedlot_boundary_shapefile"),
            ("non_structure_bmp", "manure_feedlot_outlet_shapefile"),
            ("non_structure_bmp", "manure_storage_boundary_shapefile"),
        ]

        resolved_paths: dict[tuple[str, str], Path] = {}
        for section, name in field_specs:
            raw_value = self.get_value(section, name).strip()
            if not raw_value:
                continue

            current_field = next((f for f in self._fields if f.section == section and f.name == name), None)
            if current_field is None:
                continue

            resolved_path, path_error = self._resolve_field_path(current_field, raw_value)
            if path_error:
                return path_error
            if not resolved_path.is_file():
                return f"file does not exist ({resolved_path})."
            resolved_paths[(section, name)] = resolved_path

        if not resolved_paths:
            return None

        try:
            from whitebox_workflows import WbEnvironment
            from imWEBs.bmp.bmp_manure_feedlot_validation import ManureFeedlotCatchBasinStorageValidator

            wbe = WbEnvironment()
            catch_basin_vector = None
            if ("reach_bmp", "manure_catch_basin_shapefile") in resolved_paths:
                catch_basin_vector = wbe.read_vector(str(resolved_paths[("reach_bmp", "manure_catch_basin_shapefile")]))

            feedlot_boundary_vector = None
            if ("non_structure_bmp", "manure_feedlot_boundary_shapefile") in resolved_paths:
                feedlot_boundary_vector = wbe.read_vector(str(resolved_paths[("non_structure_bmp", "manure_feedlot_boundary_shapefile")]))

            feedlot_outlet_vector = None
            if ("non_structure_bmp", "manure_feedlot_outlet_shapefile") in resolved_paths:
                feedlot_outlet_vector = wbe.read_vector(str(resolved_paths[("non_structure_bmp", "manure_feedlot_outlet_shapefile")]))

            manure_storage_boundary_vector = None
            if ("non_structure_bmp", "manure_storage_boundary_shapefile") in resolved_paths:
                manure_storage_boundary_vector = wbe.read_vector(str(resolved_paths[("non_structure_bmp", "manure_storage_boundary_shapefile")]))

            issues = ManureFeedlotCatchBasinStorageValidator.validate_issues(
                catch_basin_vector=catch_basin_vector,
                feedlot_boundary_vector=feedlot_boundary_vector,
                feedlot_outlet_vector=feedlot_outlet_vector,
                manure_storage_boundary_vector=manure_storage_boundary_vector,
            )

            if not issues:
                return None

            field_key_map = {
                "manure_catch_basin_shapefile": ("reach_bmp", "manure_catch_basin_shapefile"),
                "manure_feedlot_boundary_shapefile": ("non_structure_bmp", "manure_feedlot_boundary_shapefile"),
                "manure_feedlot_outlet_shapefile": ("non_structure_bmp", "manure_feedlot_outlet_shapefile"),
                "manure_storage_boundary_shapefile": ("non_structure_bmp", "manure_storage_boundary_shapefile"),
            }
            reverse_field_key_map = {v: k for k, v in field_key_map.items()}
            current_field_key = reverse_field_key_map.get((field.section, field.name))
            if current_field_key is None:
                return None

            current_messages = [
                issue.message
                for issue in issues
                if current_field_key in issue.fields
            ]
            if current_messages:
                return "\n".join(current_messages)
        except Exception as exc:
            return str(exc)

        return None

    def _validate_raster_against_dem(self, field: FieldDefinition, resolved_path: Path) -> str | None:
        if field.section != "watershed" or "raster" not in field.name or field.name == "dem_raster":
            return None

        dem_value = self.get_value("watershed", "dem_raster").strip()
        if not dem_value:
            return "Set DEM Raster first."

        dem_field = next(
            (f for f in self._fields if f.section == "watershed" and f.name == "dem_raster"),
            None,
        )
        if dem_field is None:
            return None

        dem_path, dem_error = self._resolve_field_path(dem_field, dem_value)
        if dem_error:
            return dem_error
        if not dem_path.is_file():
            return f"DEM raster file does not exist ({dem_path})."

        try:
            from whitebox_workflows import WbEnvironment
            from imWEBs.raster_extension import RasterExtension

            wbe = WbEnvironment()
            dem_raster = wbe.read_raster(str(dem_path))
            current_raster = wbe.read_raster(str(resolved_path))
            raster_list = {
                "dem_raster": dem_raster,
                field.name: current_raster,
            }
            RasterExtension.check_rasters(raster_list)
        except Exception as exc:
            return str(exc)

        return None

    def _validate_step4_shapefile_unique_id(self, field: FieldDefinition, resolved_path: Path) -> str | None:
        step4_sections = {
            "reach_bmp",
            "structure_bmp",
            "non_structure_bmp",
            "reservoir",
            "marginal_crop_land",
            "pasture_crop_land",
            "manure_adjustment_bmp",
        }
        if field.section not in step4_sections or "shapefile" not in field.name:
            return None

        try:
            from whitebox_workflows import WbEnvironment
            from imWEBs.vector_extension import VectorExtension

            wbe = WbEnvironment()
            vector = wbe.read_vector(str(resolved_path))
            exist, _, _ = VectorExtension.check_unique_id(vector)
            if not exist:
                return f"ID column was not found in {vector.file_name}."
        except Exception as exc:
            return str(exc)

        return None

    def _update_path_status(self, field: FieldDefinition, target: QLineEdit) -> None:
        del target
        self._validate_single_field(field)

    def _resolve_field_path(self, field: FieldDefinition, raw_value: str) -> tuple[Path, str | None]:
        value_path = Path(raw_value)
        if value_path.is_absolute():
            return value_path, None

        if field.relative_to_input:
            input_folder = self._get_input_folder_value()
            if not input_folder:
                return value_path, "Set Input Folder first for relative paths."
            return Path(input_folder) / value_path, None

        return value_path, None

    def _mark_invalid(self, status_label: QLabel, message: str) -> None:
        status_label.setToolTip(message)
        status_label.show()

    def _mark_valid(self, status_label: QLabel) -> None:
        status_label.setToolTip("")
        status_label.hide()

    def validate_path_fields(self) -> None:
        for field in self._fields:
            self._validate_single_field(field)

    def begin_bulk_update(self) -> None:
        self._suspend_path_validation = True

    def end_bulk_update(self, validate_path_status: bool = False) -> None:
        self._suspend_path_validation = False
        if validate_path_status:
            self.validate_path_fields()
        else:
            # Values loaded during suspended validation may leave stale error markers.
            self.clear_errors()

    def set_config_path(self, config_path: str) -> None:
        self._config_path = config_path

    def get_config_path(self) -> str:
        return self._config_path

    def _browse_for_field(self, field: FieldDefinition, target: QLineEdit) -> None:
        base_dir = self._resolve_base_dir(field)
        if field.kind == "folder":
            selected = QFileDialog.getExistingDirectory(self, f"Select {field.label}", base_dir)
        else:
            selected, _ = QFileDialog.getOpenFileName(
                self,
                f"Select {field.label}",
                base_dir,
                field.file_filter,
            )

        if not selected:
            return

        if field.relative_to_input:
            input_folder = self._get_input_folder_value()
            if input_folder:
                try:
                    selected = str(Path(selected).resolve().relative_to(Path(input_folder).resolve()))
                except ValueError:
                    selected = selected

        target.setText(selected)

    def _resolve_base_dir(self, field: FieldDefinition) -> str:
        if field.relative_to_input:
            input_folder = self._get_input_folder_value()
            if input_folder:
                return input_folder

        current_value = self.get_value(field.section, field.name)
        if current_value:
            current_path = Path(current_value)
            if current_path.exists():
                return str(current_path if current_path.is_dir() else current_path.parent)

        config_path = self._config_path
        if config_path:
            return str(Path(config_path).resolve().parent)
        return str(Path.cwd())

    def _get_input_folder_value(self) -> str:
        if self._input_folder_provider is not None:
            value = self._input_folder_provider().strip()
            if value:
                return value
        if ("default", "input_folder") in self._inputs:
            return self.get_value("default", "input_folder")
        return ""

    def get_value(self, section: str, name: str) -> str:
        key = (section, name)
        widget = self._inputs.get(key)
        if widget is None:
            return self._pending_values.get(key, "").strip()
        if isinstance(widget, QComboBox):
            return widget.currentText()
        if isinstance(widget, DateInput):
            return widget.value()
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        return ""

    def set_value(self, section: str, name: str, value: str) -> None:
        key = (section, name)
        if key == ("climate_interpolation", "method") and not value:
            value = "inverse_distance"
        if key == ("scenario", "model_type") and not value:
            value = "subarea"
        if key == ("scenario", "interval") and not value:
            value = "daily"
        if key == ("scenario", "name") and not value:
            value = "scenario1"
        if key == ("delineation", "stream_threshold_area_ha") and not value:
            value = "10"
        if key == ("delineation", "use_all_pour_points_from_stream_threshold") and not value:
            value = "No"
        if key == ("delineation", "wetland_min_area_ha") and not value:
            value = "0.1"
        if key == ("crop_rotation", "method") and not value:
            value = "crop_inventory"
        if key == ("crop_rotation", "include_grazing") and not value:
            value = "No"
        if key == ("marginal_crop_land", "marginal_crop_land_simulation") and not value:
            value = "No"
        if key == ("pasture_crop_land", "pasture_crop_land_simulation") and not value:
            value = "No"
        if key == ("marginal_crop_land", "marginal_crop_land_buffer_size_m") and not value:
            value = "100"
        if key == ("marginal_crop_land", "marginal_crop_land_slope_threshold_percentage") and not value:
            value = "7"
        if key == ("marginal_crop_land", "marginal_crop_land_grass_type") and not value:
            value = "36"
        if key == ("pasture_crop_land", "pasture_crop_land_grass_type") and not value:
            value = "36"
        if key == ("reservoir", "reservoir_flow_routing") and not value:
            reservoir_shapefile = self.get_value("reach_bmp", "reservoir_shapefile").strip()
            if reservoir_shapefile:
                value = "RAT_RES"
        if key in (("database", "hydroclimate"), ("lookup", "soil_lookup")) and not value:
            default_filename = "HydroClimate.db3" if key == ("database", "hydroclimate") else "SoilLookup.csv"
            input_folder = self._get_input_folder_value()
            if input_folder and (Path(input_folder) / default_filename).exists():
                value = default_filename
        if not value:
            file_defaults = {
                ("watershed", "dem_raster"): "dem.tif",
                ("watershed", "soil_raster"): "soil.tif",
                ("watershed", "landuse_raster"): "landuse.tif",
                ("watershed", "stream_shapefile"): "river_network.shp",
                ("watershed", "field_shapefile"): "field.shp",
            }
            default_filename = file_defaults.get(key)
            if default_filename is not None:
                input_folder = self._get_input_folder_value()
                if input_folder and (Path(input_folder) / default_filename).exists():
                    value = default_filename
        widget = self._inputs.get(key)
        if widget is None:
            self._pending_values[key] = value
            return
        if isinstance(widget, QComboBox):
            index = widget.findText(value)
            if index < 0 and value:
                for i in range(widget.count()):
                    if widget.itemText(i).lower() == value.lower():
                        index = i
                        break
            if index < 0:
                widget.addItem(value)
                index = widget.findText(value)
            widget.setCurrentIndex(index)
            return
        if isinstance(widget, DateInput):
            widget.set_value(value)
            return
        if isinstance(widget, QLineEdit):
            widget.setText(value)

    def collect_values(self) -> dict[tuple[str, str], str]:
        result: dict[tuple[str, str], str] = {}
        for field in self._fields:
            key = (field.section, field.name)
            if key in self._inputs:
                result[key] = self.get_value(*key)
            elif key in self._pending_values:
                result[key] = self._pending_values[key]
            else:
                result[key] = ""
        return result

    def validate_form(self) -> list[str]:
        errors: list[str] = []
        self.clear_errors()

        for field in self._fields:
            message = self._validate_single_field(field)
            if message:
                errors.append(f"{field.label}: {message}")

        return errors

    def clear_errors(self) -> None:
        self._pending_errors.clear()
        for status_label in self._status_labels.values():
            self._mark_valid(status_label)

    def _clear_field_error(self, section: str, name: str) -> None:
        key = (section, name)
        self._pending_errors.pop(key, None)
        status_label = self._status_labels.get(key)
        if status_label is not None:
            self._mark_valid(status_label)

    def _set_field_error(self, section: str, name: str, message: str) -> None:
        key = (section, name)
        status_label = self._status_labels.get(key)
        if status_label is None:
            self._pending_errors[key] = message
            return
        self._mark_invalid(status_label, message)

    def prefetch_one_section(self) -> bool:
        """Build one collapsed section in the background.

        Returns True if there may be more sections to prefetch.
        """
        while self._prefetch_section_index < len(self._sections):
            section = self._sections[self._prefetch_section_index]
            self._prefetch_section_index += 1
            section.build_content()
            return self._prefetch_section_index < len(self._sections)
        return False

    def load_values(self, config_path: str | None = None, validate_path_status: bool = True) -> None:
        if config_path is None:
            config_path = self._config_path
        if not config_path:
            return
        if not Path(config_path).exists():
            return
        values = self._service.load_config_values(config_path, self._fields)
        self.begin_bulk_update()
        try:
            for (section, name), value in values.items():
                self.set_value(section, name, value)
        finally:
            self.end_bulk_update(validate_path_status=validate_path_status)

    def save_values(self, config_path: str | None = None) -> None:
        if config_path is None:
            config_path = self._config_path
        if not config_path:
            return
        self._service.save_config_values(config_path, self._fields, self.collect_values())


class ProjectDialog(QDialog):
    """Dialog for creating or opening an imWEBs project."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowIcon(_app_icon())
        self.setWindowTitle("imWEBs Desktop - Project Manager")
        self.resize(600, 400)
        self.selected_project: dict | None = None

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Welcome to imWEBs Desktop")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        description = QLabel("Choose an option to begin:")
        description.setStyleSheet("color: #475569;")
        layout.addWidget(description)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(16)

        new_button = QPushButton()
        new_button.setIconSize(QSize(48, 48))
        new_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        new_button.setText("Create New Project")
        new_button.setToolTip("Create a new imWEBs project")
        new_button.clicked.connect(self._on_create_project)
        new_button.setMinimumHeight(80)
        options_layout.addWidget(new_button)

        open_button = QPushButton()
        open_button.setIconSize(QSize(48, 48))
        open_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        open_button.setText("Open Existing Project")
        open_button.setToolTip("Open an existing imWEBs project")
        open_button.clicked.connect(self._on_open_project)
        open_button.setMinimumHeight(80)
        options_layout.addWidget(open_button)

        layout.addLayout(options_layout)

        recent_label = QLabel("Recent Projects:")
        recent_label.setStyleSheet("font-weight: bold; margin-top: 16px;")
        layout.addWidget(recent_label)

        self.recent_list = QListWidget()
        self.recent_list.itemDoubleClicked.connect(self._on_recent_project_selected)
        recent_projects = ProjectManager.get_recent_projects()
        for project in recent_projects:
            item = QListWidgetItem(project["name"])
            item.setData(Qt.UserRole, project["path"])
            self.recent_list.addItem(item)

        if not recent_projects:
            self.recent_list.addItem("(No recent projects)")
            self.recent_list.item(0).setFlags(self.recent_list.item(0).flags() & ~Qt.ItemIsSelectable)

        layout.addWidget(self.recent_list)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        close_button = QPushButton("Exit")
        close_button.clicked.connect(self.reject)
        button_row.addWidget(close_button)
        layout.addLayout(button_row)

    def _on_create_project(self) -> None:
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setDefaultSuffix("imwebsprj")
        file_dialog.setNameFilter("imWEBs Project Files (*.imwebsprj);;All Files (*)")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDirectory(ProjectManager.get_last_project_folder())

        if file_dialog.exec() != QFileDialog.Accepted:
            return

        file_paths = file_dialog.selectedFiles()
        if not file_paths:
            return

        project_path = file_paths[0]
        try:
            self.selected_project = ProjectManager.create_project(project_path)
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Create Project Failed", str(exc))

    def _on_open_project(self) -> None:
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("imWEBs Project Files (*.imwebsprj);;All Files (*)")
        file_dialog.setDirectory(ProjectManager.get_last_project_folder())

        if file_dialog.exec() != QFileDialog.Accepted:
            return

        file_paths = file_dialog.selectedFiles()
        if not file_paths:
            return

        project_path = file_paths[0]
        try:
            self.selected_project = ProjectManager.load_project(project_path)
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Open Project Failed", str(exc))

    def _on_recent_project_selected(self, item: QListWidgetItem) -> None:
        project_path = item.data(Qt.UserRole)
        if not project_path:
            return

        try:
            self.selected_project = ProjectManager.load_project(project_path)
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Open Project Failed", str(exc))


class MainWindow(QMainWindow):
    def __init__(self, project_data: dict, startup_logger: Callable[[str], None] | None = None):
        super().__init__()
        self.setWindowIcon(_app_icon())
        self._service = ImwebsDesktopService()
        self._run_thread: QThread | None = None
        self._run_worker: QObject | None = None
        self._update_thread: QThread | None = None
        self._update_worker: QObject | None = None
        self._pending_update_download: dict[str, str | bool] | None = None
        self._project_data = project_data
        self._startup_logger = startup_logger
        self._has_unsaved_changes = False
        self._suspend_dirty_tracking = True
        self._switching_project = False
        self._prefetch_queue: list[ConfigForm] = []
        self._prefetch_active = False
        self._queued_form_ids: set[int] = set()
        self._active_model_workflow_action = ""
        self._model_workflow_buttons: list[QPushButton] = []
        
        project_path = Path(project_data["project_path"])
        project_name = project_data["name"]
        self._project_path = project_path
        self._project_name = project_name
        self._model_config_path = str(project_path.parent / f"{project_name}_model.ini")
        self._scenario_names = [str(name) for name in project_data.get("scenarios", []) if str(name).strip()]
        if not self._scenario_names:
            self._scenario_names = ["scenario1"]
        self._active_scenario_name = str(project_data.get("active_scenario", self._scenario_names[0])).strip() or self._scenario_names[0]
        if self._active_scenario_name not in self._scenario_names:
            self._scenario_names.insert(0, self._active_scenario_name)
        self._scenario_config_path = self._scenario_config_path_for(self._active_scenario_name)
        
        self._step_titles = [
            "Project Location",
            "imWEBs Structure",
            "Delineation and Rotation",
            "BMP",
            "Model Config Workflows",
            "Scenarios",
        ]

        self._project_model_fields = self._fields_by_sections(MODEL_FIELDS, ["default", "model"])
        self._structure_model_fields = self._fields_by_sections(MODEL_FIELDS, ["lookup", "database"])
        self._delineation_rotation_fields = self._fields_by_sections(MODEL_FIELDS, ["watershed", "delineation", "crop_rotation"])
        self._bmp_fields = self._fields_by_sections(
            MODEL_FIELDS,
            ["reach_bmp", "structure_bmp", "non_structure_bmp", "reservoir", "marginal_crop_land", "pasture_crop_land", "manure_adjustment_bmp"],
        )
        self._scenario_fields = self._fields_by_sections(
            SCENARIO_FIELDS,
            ["scenario", "climate_station", "climate_interpolation"],
        )
        self._scenario_model_folder_field = self._fields_by_sections(SCENARIO_FIELDS, ["model"])

        project_name = project_data.get("name", "Unknown Project")
        self.setWindowTitle(f"imWEBs Desktop - {project_name}")
        self.resize(1280, 900)
        self.statusBar().hide()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.step_label = QLabel()
        self.step_label.setStyleSheet("font-size: 14px; color: #475569;")
        layout.addWidget(self.step_label)

        actions_row = QHBoxLayout()
        actions_row.addStretch(1)
        layout.addLayout(actions_row)

        self.project_form = ConfigForm(
            "Project Location",
            self._project_model_fields,
            self._service,
            self._model_config_path,
            group_by_section=False,
            on_change=self._mark_dirty,
        )
        self.structure_form: ConfigForm | None = None
        self.delineation_rotation_form: ConfigForm | None = None
        self.bmp_form: ConfigForm | None = None
        self.scenario_form: ConfigForm | None = None
        self._model_workflow_step_widget: QWidget | None = None
        self._model_workflow_log_output: QPlainTextEdit | None = None
        self._scenario_list_widget: QListWidget | None = None
        self._scenario_step_widget: QWidget | None = None
        self._generate_scenario_button: QPushButton | None = None
        self._scenario_generation_output: QPlainTextEdit | None = None

        self.workflow_stack = QStackedWidget()
        self._step_pages: dict[int, QWidget] = {}
        self._step_layouts: dict[int, QVBoxLayout] = {}
        for index in range(6):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            self._step_pages[index] = page
            self._step_layouts[index] = page_layout
            self.workflow_stack.addWidget(page)
        self._step_layouts[0].addWidget(self.project_form, 1)
        layout.addWidget(self.workflow_stack, 1)

        navigation_row = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_to_previous_step)
        self.help_button = QPushButton("?")
        self.help_button.setMaximumWidth(40)
        self.help_button.clicked.connect(self._open_help)
        self.projects_button = QPushButton("Projects")
        self.projects_button.clicked.connect(self.open_project_dialog)
        self.check_update_button = QPushButton("Check Update")
        self.check_update_button.clicked.connect(self.check_for_updates)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(lambda checked=False: self.save_state(notify=True))
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.go_to_next_step)
        navigation_row.addWidget(self.back_button)
        navigation_row.addWidget(self.help_button)
        navigation_row.addWidget(self.projects_button)
        navigation_row.addWidget(self.check_update_button)
        navigation_row.addStretch(1)
        navigation_row.addWidget(self.save_button)
        navigation_row.addWidget(self.next_button)
        layout.addLayout(navigation_row)

        self._update_step_ui()
        self._load_project_config()
        self._schedule_hybrid_prefetch()
        self._suspend_dirty_tracking = False

    def _load_project_config(self) -> None:
        """Load config values if they exist. Config files are created on first save."""
        model_config_path = self._model_config_path

        if Path(model_config_path).exists():
            self.project_form.load_values(model_config_path, validate_path_status=False)

        # Build current step lazily without running full path validation.
        QTimer.singleShot(0, lambda: self._ensure_step_form(self.workflow_stack.currentIndex()))

    def _set_step_placeholder(self, step_index: int, message: str) -> None:
        layout = self._step_layouts.get(step_index)
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        placeholder = QLabel(message)
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #64748b; font-size: 14px;")
        layout.addWidget(placeholder, 1)
        QApplication.processEvents()

    def _swap_step_form(self, step_index: int, form: ConfigForm) -> None:
        layout = self._step_layouts[step_index]
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        layout.addWidget(form, 1)

    def _swap_step_widget(self, step_index: int, widget: QWidget) -> None:
        layout = self._step_layouts[step_index]
        while layout.count():
            item = layout.takeAt(0)
            old_widget = item.widget()
            if old_widget is not None:
                old_widget.deleteLater()
        layout.addWidget(widget, 1)

    def _scenario_config_path_for(self, scenario_name: str) -> str:
        return str(self._project_path.parent / f"{self._project_name}_{scenario_name}.ini")

    def _ensure_scenario_file_exists(self, scenario_name: str) -> None:
        scenario_path = Path(self._scenario_config_path_for(scenario_name))
        if scenario_path.exists():
            return

        legacy_path = self._project_path.parent / f"{self._project_name}_scenario.ini"
        if scenario_name == "scenario1" and legacy_path.exists():
            values = self._service.load_config_values(str(legacy_path), self._scenario_fields)
            self._service.save_config_values(str(scenario_path), self._scenario_fields, values)
            return

        self._service.create_scenario_template(str(scenario_path))

    def _persist_project_metadata(self) -> None:
        self._project_data["scenarios"] = list(self._scenario_names)
        self._project_data["active_scenario"] = self._active_scenario_name
        self._project_data = ProjectManager.save_project(self._project_data["project_path"], self._project_data)

    def _build_scenario_step_widget(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Scenario"))

        self._scenario_list_widget = QListWidget()
        self._scenario_list_widget.setMaximumHeight(110)
        self._scenario_list_widget.itemSelectionChanged.connect(self._on_scenario_selection_changed)

        add_button = QPushButton("Add Scenario")
        add_button.clicked.connect(self._add_scenario)
        remove_button = QPushButton("Remove Scenario")
        remove_button.clicked.connect(self._remove_scenario)
        self._generate_scenario_button = QPushButton("Generate Model Structure")
        self._generate_scenario_button.clicked.connect(self._run_scenario_generation)

        toolbar.addWidget(add_button)
        toolbar.addWidget(remove_button)
        toolbar.addWidget(self._generate_scenario_button)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)
        layout.addWidget(self._scenario_list_widget)

        # Create side-by-side layout for form and output
        content_layout = QHBoxLayout()

        self.scenario_form = ConfigForm(
            "Scenario",
            self._scenario_fields,
            self._service,
            self._scenario_config_path,
            input_folder_provider=self._current_input_folder,
            on_change=self._mark_dirty,
            on_field_change=self._on_scenario_field_changed,
        )
        content_layout.addWidget(self.scenario_form, 1)

        self._scenario_generation_output = QPlainTextEdit()
        self._scenario_generation_output.setReadOnly(True)
        self._scenario_generation_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout.addWidget(self._scenario_generation_output, 1)

        layout.addLayout(content_layout, 1)

        self._populate_scenario_list_widget()
        return wrapper

    def _build_model_workflow_step_widget(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)

        info_box = QGroupBox("Create Model Files")
        info_layout = QVBoxLayout(info_box)
        info_text = QLabel(
            "Run model-configuration workflows before entering the scenario step. "
            "These actions use the current model config values from previous steps."
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        button_row = QHBoxLayout()
        workflow_buttons = [
            ("Delineate Watershed", "delineate_watershed"),
            ("Generate Parameters", "generate_parameters"),
            ("Update Crop Rotation", "update_crop_rotation"),
        ]
        for label, action in workflow_buttons:
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, action_name=action: self._run_model_config_workflow(action_name))
            self._model_workflow_buttons.append(button)
            button_row.addWidget(button)
        button_row.addStretch(1)
        info_layout.addLayout(button_row)
        layout.addWidget(info_box)

        log_box = QGroupBox("Workflow Messages")
        log_layout = QVBoxLayout(log_box)
        self._model_workflow_log_output = QPlainTextEdit()
        self._model_workflow_log_output.setReadOnly(True)
        self._model_workflow_log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        log_layout.addWidget(self._model_workflow_log_output, 1)
        layout.addWidget(log_box, 1)

        return wrapper

    def _populate_scenario_list_widget(self) -> None:
        if self._scenario_list_widget is None:
            return
        self._scenario_list_widget.blockSignals(True)
        self._scenario_list_widget.clear()
        for scenario_name in self._scenario_names:
            self._scenario_list_widget.addItem(QListWidgetItem(scenario_name))
        matches = self._scenario_list_widget.findItems(self._active_scenario_name, Qt.MatchExactly)
        if matches:
            self._scenario_list_widget.setCurrentItem(matches[0])
        self._scenario_list_widget.blockSignals(False)

    def _save_current_scenario_values(self) -> None:
        if self.scenario_form is None:
            return
        scenario_values = self.scenario_form.collect_values()
        scenario_values[("scenario", "name")] = self._active_scenario_name
        self._service.save_config_values(
            self._scenario_config_path,
            self._scenario_fields,
            scenario_values,
        )
        self._sync_model_folder_to_scenario()

    def _activate_scenario(self, scenario_name: str, *, save_current: bool = True) -> None:
        if scenario_name == self._active_scenario_name:
            return
        if save_current:
            self._save_current_scenario_values()
        self._active_scenario_name = scenario_name
        self._scenario_config_path = self._scenario_config_path_for(scenario_name)
        self._persist_project_metadata()
        if self.scenario_form is not None:
            self.scenario_form.set_config_path(self._scenario_config_path)
            self._ensure_scenario_file_exists(scenario_name)
            self.scenario_form.load_values(self._scenario_config_path, validate_path_status=False)
            self.scenario_form.set_value("scenario", "name", self._active_scenario_name)
            self._apply_hydroclimate_date_defaults(self.scenario_form, force=True)
            self._apply_crop_rotation_year_defaults(force=False)

    def _on_scenario_selection_changed(self) -> None:
        if self._scenario_list_widget is None:
            return
        item = self._scenario_list_widget.currentItem()
        if item is None:
            return
        scenario_name = item.text().strip()
        if not scenario_name:
            return
        self._activate_scenario(scenario_name)

    def _add_scenario(self) -> None:
        scenario_name, ok = QInputDialog.getText(self, "Add Scenario", "Scenario name:")
        if not ok:
            return
        scenario_name = scenario_name.strip()
        if not scenario_name:
            QMessageBox.warning(self, "Add Scenario", "Scenario name cannot be empty.")
            return
        invalid_chars = set('<>:"/\\|?*')
        if any(char in invalid_chars for char in scenario_name):
            QMessageBox.warning(self, "Add Scenario", "Scenario name contains invalid filename characters.")
            return
        if scenario_name in self._scenario_names:
            QMessageBox.warning(self, "Add Scenario", "Scenario already exists.")
            return
        self._scenario_names.append(scenario_name)
        self._persist_project_metadata()
        self._populate_scenario_list_widget()
        self._activate_scenario(scenario_name)
        self._has_unsaved_changes = True

    def _remove_scenario(self) -> None:
        if len(self._scenario_names) <= 1:
            QMessageBox.warning(self, "Remove Scenario", "At least one scenario must remain.")
            return
        if self._scenario_list_widget is None or self._scenario_list_widget.currentItem() is None:
            return
        scenario_name = self._scenario_list_widget.currentItem().text().strip()
        if not scenario_name:
            return
        response = QMessageBox.question(
            self,
            "Remove Scenario",
            f"Remove scenario '{scenario_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if response != QMessageBox.Yes:
            return

        if scenario_name == self._active_scenario_name:
            fallback = next((name for name in self._scenario_names if name != scenario_name), None)
            if fallback is None:
                return
            self._activate_scenario(fallback, save_current=True)

        self._scenario_names = [name for name in self._scenario_names if name != scenario_name]
        scenario_path = Path(self._scenario_config_path_for(scenario_name))
        if scenario_path.exists():
            try:
                scenario_path.unlink()
            except OSError:
                pass
        self._persist_project_metadata()
        self._populate_scenario_list_widget()
        self._has_unsaved_changes = True

    def _ensure_step_form(self, step_index: int) -> None:
        if step_index == 1 and self.structure_form is None:
            self._suspend_dirty_tracking = True
            t0 = time.perf_counter()
            self._set_step_placeholder(step_index, "Loading imWEBs Structure...")
            self.structure_form = ConfigForm(
                "imWEBs Structure",
                self._structure_model_fields,
                self._service,
                self._model_config_path,
                input_folder_provider=self._current_input_folder,
                on_change=self._mark_dirty,
                on_field_change=self._on_structure_field_changed,
            )
            self._swap_step_form(step_index, self.structure_form)
            if Path(self._model_config_path).exists():
                self._load_fields_from_file(self.structure_form, self._model_config_path, self._structure_model_fields)
            if self._startup_logger is not None:
                self._startup_logger(f"Step 2 first load ({time.perf_counter() - t0:.3f}s)")
            self._suspend_dirty_tracking = False

        if step_index == 2 and self.delineation_rotation_form is None:
            self._suspend_dirty_tracking = True
            t0 = time.perf_counter()
            self._set_step_placeholder(step_index, "Loading Delineation and Rotation...")
            self.delineation_rotation_form = ConfigForm(
                "Delineation and Rotation",
                self._delineation_rotation_fields,
                self._service,
                self._model_config_path,
                input_folder_provider=self._current_input_folder,
                on_change=self._mark_dirty,
            )
            self._swap_step_form(step_index, self.delineation_rotation_form)
            if Path(self._model_config_path).exists():
                self.delineation_rotation_form.load_values(self._model_config_path, validate_path_status=False)
            self._apply_crop_rotation_year_defaults(force=True)
            if self._startup_logger is not None:
                self._startup_logger(f"Step 3 first load ({time.perf_counter() - t0:.3f}s)")
            self._suspend_dirty_tracking = False

        if step_index == 3 and self.bmp_form is None:
            self._suspend_dirty_tracking = True
            t0 = time.perf_counter()
            self._set_step_placeholder(step_index, "Loading BMP...")
            self.bmp_form = ConfigForm(
                "BMP",
                self._bmp_fields,
                self._service,
                self._model_config_path,
                input_folder_provider=self._current_input_folder,
                on_change=self._mark_dirty,
            )
            self._swap_step_form(step_index, self.bmp_form)
            if Path(self._model_config_path).exists():
                self.bmp_form.load_values(self._model_config_path, validate_path_status=False)
            if self._startup_logger is not None:
                self._startup_logger(f"Step 4 first load ({time.perf_counter() - t0:.3f}s)")
            self._suspend_dirty_tracking = False

        if step_index == 4 and self._model_workflow_step_widget is None:
            self._suspend_dirty_tracking = True
            t0 = time.perf_counter()
            self._set_step_placeholder(step_index, "Loading Model Config Workflows...")
            self._model_workflow_step_widget = self._build_model_workflow_step_widget()
            self._swap_step_widget(step_index, self._model_workflow_step_widget)
            if self._startup_logger is not None:
                self._startup_logger(f"Step 5 first load ({time.perf_counter() - t0:.3f}s)")
            self._suspend_dirty_tracking = False

        if step_index == 5 and self.scenario_form is None:
            self._suspend_dirty_tracking = True
            t0 = time.perf_counter()
            self._set_step_placeholder(step_index, "Loading Scenarios...")
            self._scenario_step_widget = self._build_scenario_step_widget()
            self._swap_step_widget(step_index, self._scenario_step_widget)
            self._ensure_scenario_file_exists(self._active_scenario_name)
            self.scenario_form.load_values(self._scenario_config_path, validate_path_status=False)
            self.scenario_form.set_value("scenario", "name", self._active_scenario_name)
            self._apply_hydroclimate_date_defaults(self.scenario_form, force=True)
            self._apply_crop_rotation_year_defaults(force=True)
            if self._startup_logger is not None:
                self._startup_logger(f"Step 6 first load ({time.perf_counter() - t0:.3f}s)")
            self._suspend_dirty_tracking = False

    def _on_structure_field_changed(self, section: str, name: str) -> None:
        if (section, name) == ("database", "hydroclimate") and self.scenario_form is not None:
            self._apply_hydroclimate_date_defaults(self.scenario_form, force=False)

    def _on_scenario_field_changed(self, section: str, name: str) -> None:
        if (section, name) in (("scenario", "start_date"), ("scenario", "end_date")):
            self._apply_crop_rotation_year_defaults(force=False)
        if (section, name) == ("scenario", "name") and self.scenario_form is not None:
            # Scenario file identity comes from scenario manager selection.
            if self.scenario_form.get_value("scenario", "name") != self._active_scenario_name:
                self.scenario_form.set_value("scenario", "name", self._active_scenario_name)

    def _current_hydroclimate_value(self) -> str:
        if self.structure_form is None:
            return ""
        return self.structure_form.get_value("database", "hydroclimate")

    def _apply_hydroclimate_date_defaults(self, form: ConfigForm, *, force: bool = True) -> None:
        """Set default start/end dates from the hydroclimate DB.

        When force=True (initial load), only fills blank date fields.
        When force=False (hydroclimate field changed by user), overwrites both dates.
        """
        start_blank = not form.get_value("scenario", "start_date")
        end_blank = not form.get_value("scenario", "end_date")
        if not force and not start_blank and not end_blank:
            return
        if force and not start_blank and not end_blank:
            return
        hydroclimate_value = self._current_hydroclimate_value()
        if not hydroclimate_value:
            return
        input_folder = self._current_input_folder()
        db_path = str(Path(input_folder) / hydroclimate_value) if input_folder else hydroclimate_value
        date_range = self._service.get_hydroclimate_date_range(db_path)
        if date_range is None:
            return
        start_date, end_date = date_range
        if force:
            if start_blank:
                form.set_value("scenario", "start_date", start_date)
            if end_blank:
                form.set_value("scenario", "end_date", end_date)
        else:
            form.set_value("scenario", "start_date", start_date)
            form.set_value("scenario", "end_date", end_date)

    def _extract_year(self, date_value: str) -> str:
        date_value = date_value.strip()
        if len(date_value) >= 4 and date_value[:4].isdigit():
            return date_value[:4]
        return ""

    def _apply_crop_rotation_year_defaults(self, *, force: bool = True) -> None:
        """Default crop rotation first/last year from scenario start/end dates.

        When force=True, fills blank year fields during initial form load.
        When force=False, still only fills blank fields after scenario date edits.
        """
        if self.scenario_form is None or self.delineation_rotation_form is None:
            return

        start_year = self._extract_year(self.scenario_form.get_value("scenario", "start_date"))
        end_year = self._extract_year(self.scenario_form.get_value("scenario", "end_date"))
        if not start_year and not end_year:
            return

        first_year_blank = not self.delineation_rotation_form.get_value("crop_rotation", "first_year")
        last_year_blank = not self.delineation_rotation_form.get_value("crop_rotation", "last_year")
        if not first_year_blank and not last_year_blank:
            return

        if start_year and first_year_blank:
            self.delineation_rotation_form.set_value("crop_rotation", "first_year", start_year)
        if end_year and last_year_blank:
            self.delineation_rotation_form.set_value("crop_rotation", "last_year", end_year)

    def _mark_dirty(self) -> None:
        if self._suspend_dirty_tracking:
            return
        self._has_unsaved_changes = True

    def _form_for_step(self, step_index: int) -> ConfigForm | None:
        if step_index == 0:
            return self.project_form
        if step_index == 1:
            return self.structure_form
        if step_index == 2:
            return self.delineation_rotation_form
        if step_index == 3:
            return self.bmp_form
        if step_index == 5:
            return self.scenario_form
        return None

    def _enqueue_prefetch(self, form: ConfigForm | None) -> None:
        if form is None:
            return
        form_id = id(form)
        if form_id in self._queued_form_ids:
            return
        self._queued_form_ids.add(form_id)
        self._prefetch_queue.append(form)
        if not self._prefetch_active:
            self._prefetch_active = True
            QTimer.singleShot(40, self._run_prefetch_tick)

    def _run_prefetch_tick(self) -> None:
        if not self._prefetch_queue:
            self._prefetch_active = False
            return

        form = self._prefetch_queue.pop(0)
        self._queued_form_ids.discard(id(form))
        has_more = form.prefetch_one_section()
        if has_more:
            self._enqueue_prefetch(form)

        QTimer.singleShot(30, self._run_prefetch_tick)

    def _schedule_hybrid_prefetch(self) -> None:
        current_step = self.workflow_stack.currentIndex()
        target_steps = [current_step]
        if current_step + 1 <= 5:
            target_steps.append(current_step + 1)

        for step in target_steps:
            self._ensure_step_form(step)
            self._enqueue_prefetch(self._form_for_step(step))

    def _refresh_visible_path_indicators(self) -> None:
        step_index = self.workflow_stack.currentIndex()
        self._ensure_step_form(step_index)
        step_forms = {
            0: [self.project_form],
            1: [self.structure_form] if self.structure_form is not None else [],
            2: [self.delineation_rotation_form] if self.delineation_rotation_form is not None else [],
            3: [self.bmp_form] if self.bmp_form is not None else [],
            4: [],
            5: [self.scenario_form] if self.scenario_form is not None else [],
        }
        for form in step_forms.get(step_index, []):
            form.validate_path_fields()

    def _fields_by_sections(self, fields: list[FieldDefinition], sections: list[str]) -> list[FieldDefinition]:
        section_set = set(sections)
        return [field for field in fields if field.section in section_set]

    def _current_input_folder(self) -> str:
        try:
            return self.project_form.get_value("default", "input_folder")
        except KeyError:
            return ""

    def _build_step_page(self, title: str, forms: list[ConfigForm]) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        for form in forms:
            layout.addWidget(form, 1)
        return page

    def _refresh_path_indicators(self) -> None:
        for form in [self.project_form, self.structure_form, self.delineation_rotation_form, self.bmp_form, self.scenario_form]:
            if form is not None:
                form.validate_path_fields()

    def _load_fields_from_file(self, form: ConfigForm, file_path: str, fields: list[FieldDefinition]) -> None:
        values = self._service.load_config_values(file_path, fields)
        form.begin_bulk_update()
        try:
            for (section, name), value in values.items():
                form.set_value(section, name, value)
        finally:
            form.end_bulk_update(validate_path_status=False)

    def _update_step_ui(self) -> None:
        step_index = self.workflow_stack.currentIndex()
        total_steps = len(self._step_titles)
        self.step_label.setText(f"Step {step_index + 1} of {total_steps}: {self._step_titles[step_index]}")
        self.back_button.setEnabled(step_index > 0 and self._run_thread is None)
        self.projects_button.setEnabled(self._run_thread is None)
        self.check_update_button.setEnabled(self._run_thread is None and self._update_thread is None)
        self.next_button.setVisible(step_index < total_steps - 1)
        self.next_button.setEnabled(self._run_thread is None)
        self._ensure_step_form(step_index)
        self._schedule_hybrid_prefetch()

    def _current_version(self) -> str:
        try:
            return version("imwebs-desktop")
        except PackageNotFoundError:
            return "0.1.1"

    def check_for_updates(self) -> None:
        if self._run_thread is not None:
            QMessageBox.information(self, "Check Update", "Please wait for current workflow to finish.")
            return
        if self._update_thread is not None:
            QMessageBox.information(self, "Check Update", "Update check is already running.")
            return

        self._pending_update_download = None
        self.check_update_button.setEnabled(False)

        self._update_thread = QThread(self)
        self._update_worker = UpdateCheckWorker(self._service, self._current_version())
        self._update_worker.moveToThread(self._update_thread)
        self._update_thread.started.connect(self._update_worker.run)
        self._update_worker.finished.connect(self._on_update_check_finished)
        self._update_worker.failed.connect(self._on_update_check_failed)
        self._update_worker.finished.connect(self._update_thread.quit)
        self._update_worker.failed.connect(self._update_thread.quit)
        self._update_thread.finished.connect(self._cleanup_update)
        self._update_thread.start()

    def _on_update_check_finished(self, payload: object) -> None:
        if not isinstance(payload, dict):
            QMessageBox.warning(self, "Check Update", "Unexpected response while checking for updates.")
            return

        update_available = bool(payload.get("update_available", False))
        latest_version = str(payload.get("latest_version", ""))
        current_version = str(payload.get("current_version", ""))
        installer_url = str(payload.get("installer_url", ""))
        release_notes = str(payload.get("release_notes", ""))

        if not update_available:
            QMessageBox.information(
                self,
                "Check Update",
                f"You are up to date. Current version: {current_version}.",
            )
            return

        if not installer_url:
            QMessageBox.warning(
                self,
                "Update Available",
                f"Version {latest_version} is available, but no Windows installer was found in the release assets.",
            )
            return

        summary_lines = [
            f"Current version: {current_version}",
            f"Latest version: {latest_version}",
            "",
            "Do you want to download and install the update now?",
        ]
        if release_notes:
            preview = "\n".join(release_notes.splitlines()[:10]).strip()
            if preview:
                summary_lines.extend(["", "Release notes:", preview])

        response = QMessageBox.question(
            self,
            "Update Available",
            "\n".join(summary_lines),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if response == QMessageBox.Yes:
            self._pending_update_download = payload

    def _on_update_check_failed(self, message: str) -> None:
        QMessageBox.warning(self, "Check Update", f"Could not check for updates.\n\n{message}")

    def _start_update_download(self, payload: dict[str, str | bool]) -> None:
        installer_url = str(payload.get("installer_url", ""))
        installer_name = str(payload.get("installer_name", ""))
        if not installer_url:
            QMessageBox.warning(self, "Update", "No installer URL is available for this release.")
            return

        self.check_update_button.setEnabled(False)
        self._update_thread = QThread(self)
        self._update_worker = UpdateDownloadWorker(self._service, installer_url, installer_name)
        self._update_worker.moveToThread(self._update_thread)
        self._update_thread.started.connect(self._update_worker.run)
        self._update_worker.finished.connect(self._on_update_download_finished)
        self._update_worker.failed.connect(self._on_update_download_failed)
        self._update_worker.finished.connect(self._update_thread.quit)
        self._update_worker.failed.connect(self._update_thread.quit)
        self._update_thread.finished.connect(self._cleanup_update)
        self._update_thread.start()

    def _on_update_download_finished(self, installer_path: str) -> None:
        response = QMessageBox.question(
            self,
            "Install Update",
            "The update installer has been downloaded. Launch installer now?\n"
            "The application will close after launching the installer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if response != QMessageBox.Yes:
            QMessageBox.information(self, "Install Update", f"Installer downloaded to:\n{installer_path}")
            return

        try:
            self._service.launch_installer(installer_path)
        except Exception as exc:
            QMessageBox.critical(self, "Install Update", str(exc))
            return

        QApplication.instance().quit()

    def _on_update_download_failed(self, message: str) -> None:
        QMessageBox.warning(self, "Install Update", f"Could not download update installer.\n\n{message}")

    def _confirm_unsaved_before_switch(self) -> bool:
        if not self._has_unsaved_changes:
            return True
        response = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Save before switching projects?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        if response == QMessageBox.Save:
            return self.save_state(notify=False)
        if response == QMessageBox.Discard:
            return True
        return False

    def open_project_dialog(self) -> None:
        if self._run_thread is not None:
            QMessageBox.information(self, "Run In Progress", "Please wait for the workflow to finish before switching projects.")
            return
        if not self._confirm_unsaved_before_switch():
            return

        dialog = ProjectDialog(self)
        if dialog.exec() != QDialog.Accepted or not dialog.selected_project:
            return

        new_window = MainWindow(dialog.selected_project, startup_logger=self._startup_logger)
        new_window.showMaximized()
        QApplication.instance().setProperty("imwebs_active_window", new_window)
        self._switching_project = True
        self._has_unsaved_changes = False
        self.close()

    def _open_help(self) -> None:
        """Open help documentation for the current step."""
        step_index = self.workflow_stack.currentIndex()
        
        # Base documentation URL (GitHub Pages)
        base_url = "https://hawklorry.github.io/imWEBs-Python/"
        
        # Map steps to help pages
        help_urls = {
            0: base_url,  # Project Location -> main index
            1: base_url,  # Structure -> main index
            2: base_url + "user-guide/model_config.html",  # Delineation and Rotation
            3: base_url + "user-guide/model_config.html",  # BMP
            4: base_url + "user-guide/model_config.html",  # Model Config Workflows
            5: base_url + "user-guide/scenario_config.html",  # Scenarios
        }
        
        url = help_urls.get(step_index, base_url)
        QDesktopServices.openUrl(QUrl(url))

    def _validate_current_step(self) -> bool:
        step_index = self.workflow_stack.currentIndex()
        self._ensure_step_form(step_index)
        forms: list[ConfigForm] = []

        if step_index == 0:
            forms = [self.project_form]
        elif step_index == 1 and self.structure_form is not None:
            forms = [self.structure_form]
        elif step_index == 2 and self.delineation_rotation_form is not None:
            forms = [self.delineation_rotation_form]
        elif step_index == 3 and self.bmp_form is not None:
            forms = [self.bmp_form]
        elif step_index == 5 and self.scenario_form is not None:
            forms = [self.scenario_form]

        errors: list[str] = []
        for form in forms:
            errors.extend(form.validate_form())

        if errors:
            shown_errors = errors[:10]
            details = "\n".join(shown_errors)
            if len(errors) > len(shown_errors):
                details += f"\n... and {len(errors) - len(shown_errors)} more errors."
            QMessageBox.warning(self, "Step Validation Failed", details)
            self.append_log(f"Step validation failed with {len(errors)} error(s).")
            return False

        return True

    def go_to_next_step(self) -> None:
        if not self._validate_current_step():
            return
        next_index = min(self.workflow_stack.currentIndex() + 1, self.workflow_stack.count() - 1)
        self.workflow_stack.setCurrentIndex(next_index)
        self._update_step_ui()

    def go_to_previous_step(self) -> None:
        previous_index = max(self.workflow_stack.currentIndex() - 1, 0)
        self.workflow_stack.setCurrentIndex(previous_index)
        self._update_step_ui()

    def save_state(self, notify: bool = True) -> bool:
        try:
            self._save_forms(ensure_all_forms=True)
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
            return False
        self._has_unsaved_changes = False
        self.append_log("Configuration saved to configuration files.")
        if notify:
            QMessageBox.information(self, "Save", "State saved to configuration files.")
        return True

    def append_log(self, message: str) -> None:
        """Legacy logging method - kept for compatibility but no longer used."""
        pass

    def create_templates(self) -> None:
        self._service.create_model_template(self._model_config_path)
        self._service.create_scenario_template(self._scenario_config_path)
        self.project_form.load_values(self._model_config_path)
        self._ensure_step_form(1)
        self._ensure_step_form(2)
        self._ensure_step_form(3)
        self._ensure_step_form(4)
        self._ensure_step_form(5)
        if self.structure_form is not None:
            self._load_fields_from_file(self.structure_form, self._model_config_path, self._structure_model_fields)
        if self.delineation_rotation_form is not None:
            self.delineation_rotation_form.load_values(self._model_config_path)
        if self.bmp_form is not None:
            self.bmp_form.load_values(self._model_config_path)
        if self.scenario_form is not None:
            self.scenario_form.load_values(self._scenario_config_path, validate_path_status=False)
            self.scenario_form.set_value("scenario", "name", self._active_scenario_name)
        self._sync_model_folder_to_scenario()
        self.append_log("Reset field values from blank templates.")
        QMessageBox.information(self, "Reset Fields", "Fields were reset to template defaults.")

    def _append_model_workflow_log(self, message: str) -> None:
        if self._model_workflow_log_output is not None:
            self._model_workflow_log_output.appendPlainText(message)
            self._model_workflow_log_output.verticalScrollBar().setValue(
                self._model_workflow_log_output.verticalScrollBar().maximum()
            )

    def _append_scenario_generation_log(self, message: str) -> None:
        if self._scenario_generation_output is not None:
            self._scenario_generation_output.appendPlainText(message)
            self._scenario_generation_output.verticalScrollBar().setValue(
                self._scenario_generation_output.verticalScrollBar().maximum()
            )

    def _run_model_config_workflow(self, action: str) -> None:
        if self._run_thread is not None:
            QMessageBox.information(self, "Run Workflow", "A workflow is already running.")
            return

        self._ensure_step_form(1)
        self._ensure_step_form(2)
        self._ensure_step_form(3)

        model_forms: list[ConfigForm] = [
            self.project_form,
            self.structure_form,
            self.delineation_rotation_form,
            self.bmp_form,
        ]

        errors: list[str] = []
        for form in model_forms:
            if form is not None:
                errors.extend(form.validate_form())

        if errors:
            shown_errors = errors[:12]
            details = "\n".join(shown_errors)
            if len(errors) > len(shown_errors):
                details += f"\n... and {len(errors) - len(shown_errors)} more errors."
            QMessageBox.warning(self, "Validation Failed", details)
            self._append_model_workflow_log(f"Workflow blocked by {len(errors)} validation error(s).")
            return

        try:
            self._save_model_forms(ensure_model_forms=True)
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
            return

        self._has_unsaved_changes = False
        self._append_model_workflow_log(f"Starting model workflow: {action}")

        self._active_model_workflow_action = action
        self._run_thread = QThread(self)
        self._run_worker = ModelConfigWorkflowWorker(self._service, self._model_config_path, action)
        self._run_worker.moveToThread(self._run_thread)
        self._run_thread.started.connect(self._run_worker.run)
        self._run_worker.log_message.connect(self._append_model_workflow_log)
        self._run_worker.finished.connect(self._on_model_workflow_finished)
        self._run_worker.failed.connect(self._on_model_workflow_failed)
        self._run_worker.finished.connect(self._run_thread.quit)
        self._run_worker.failed.connect(self._run_thread.quit)
        self._run_thread.finished.connect(self._cleanup_run)
        self._set_running_state(True)
        self._run_thread.start()

    def _on_model_workflow_finished(self) -> None:
        action = self._active_model_workflow_action
        self._active_model_workflow_action = ""
        self._append_model_workflow_log(f"Model workflow finished successfully: {action}")
        QMessageBox.information(self, "Model Workflow", f"Workflow completed successfully: {action}")

    def _on_model_workflow_failed(self, message: str) -> None:
        action = self._active_model_workflow_action
        self._active_model_workflow_action = ""
        self._append_model_workflow_log(f"Model workflow failed ({action}): {message}")
        QMessageBox.critical(self, "Model Workflow", message)

    def _run_scenario_generation(self) -> None:
        if self._run_thread is not None:
            QMessageBox.information(self, "Scenario Generation", "A workflow is already running.")
            return

        self._ensure_step_form(5)

        if self.scenario_form is not None:
            errors = self.scenario_form.validate_form()
            if errors:
                shown_errors = errors[:12]
                details = "\n".join(shown_errors)
                if len(errors) > len(shown_errors):
                    details += f"\n... and {len(errors) - len(shown_errors)} more errors."
                QMessageBox.warning(self, "Validation Failed", details)
                self._append_scenario_generation_log(f"Scenario generation blocked by {len(errors)} validation error(s).")
                return

        try:
            self._save_current_scenario_values()
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
            return

        self._has_unsaved_changes = False
        self._append_scenario_generation_log(f"Starting scenario structure generation for: {self._active_scenario_name}")

        self._run_thread = QThread(self)
        self._run_worker = ScenarioGenerationWorker(self._service, self._scenario_config_path)
        self._run_worker.moveToThread(self._run_thread)
        self._run_thread.started.connect(self._run_worker.run)
        self._run_worker.log_message.connect(self._append_scenario_generation_log)
        self._run_worker.finished.connect(self._on_scenario_generation_finished)
        self._run_worker.failed.connect(self._on_scenario_generation_failed)
        self._run_worker.finished.connect(self._run_thread.quit)
        self._run_worker.failed.connect(self._run_thread.quit)
        self._run_thread.finished.connect(self._cleanup_run)
        self._set_running_state(True)
        self._run_thread.start()

    def _on_scenario_generation_finished(self) -> None:
        self._append_scenario_generation_log("Scenario structure generation completed successfully!")
        QMessageBox.information(self, "Scenario Generation", "Model structure files generated successfully!")

    def _on_scenario_generation_failed(self, message: str) -> None:
        self._append_scenario_generation_log(f"Scenario generation failed: {message}")
        QMessageBox.critical(self, "Scenario Generation", message)

    def _save_model_forms(self, ensure_model_forms: bool = False) -> None:
        if ensure_model_forms:
            self._ensure_step_form(1)
            self._ensure_step_form(2)
            self._ensure_step_form(3)
        self._service.save_config_values(
            self._model_config_path,
            self._project_model_fields,
            self.project_form.collect_values(),
        )
        if self.structure_form is not None:
            self._service.save_config_values(
                self._model_config_path,
                self._structure_model_fields,
                {
                    key: value
                    for key, value in self.structure_form.collect_values().items()
                    if key in {(field.section, field.name) for field in self._structure_model_fields}
                },
            )
        if self.delineation_rotation_form is not None:
            self._service.save_config_values(
                self._model_config_path,
                self._delineation_rotation_fields,
                self.delineation_rotation_form.collect_values(),
            )
        if self.bmp_form is not None:
            self._service.save_config_values(
                self._model_config_path,
                self._bmp_fields,
                self.bmp_form.collect_values(),
            )

    def _save_forms(self, ensure_all_forms: bool = False) -> None:
        if ensure_all_forms:
            self._ensure_step_form(1)
            self._ensure_step_form(2)
            self._ensure_step_form(3)
            self._ensure_step_form(4)
            self._ensure_step_form(5)
        self._save_model_forms(ensure_model_forms=ensure_all_forms)
        if self.scenario_form is not None:
            scenario_values = self.scenario_form.collect_values()
            scenario_values[("scenario", "name")] = self._active_scenario_name
            self._service.save_config_values(
                self._scenario_config_path,
                self._scenario_fields,
                scenario_values,
            )
        self._sync_model_folder_to_scenario()
        self._persist_project_metadata()
        self._refresh_path_indicators()

    def _sync_model_folder_to_scenario(self) -> None:
        model_folder = self.project_form.get_value("model", "model_folder")
        if not model_folder:
            return
        for scenario_name in self._scenario_names:
            scenario_path = self._scenario_config_path_for(scenario_name)
            self._service.save_config_values(
                scenario_path,
                self._scenario_model_folder_field,
                {("model", "model_folder"): model_folder},
            )

    def _set_running_state(self, running: bool) -> None:
        for button in self._model_workflow_buttons:
            button.setEnabled(not running)
        self._generate_scenario_button.setEnabled(not running)
        self.back_button.setEnabled(not running and self.workflow_stack.currentIndex() > 0)
        self.projects_button.setEnabled(not running)
        self.check_update_button.setEnabled((not running) and self._update_thread is None)
        self.save_button.setEnabled(not running)
        self.next_button.setEnabled(not running and self.workflow_stack.currentIndex() < self.workflow_stack.count() - 1)

    def _on_run_finished(self) -> None:
        """Legacy method - kept for compatibility but no longer used."""
        QMessageBox.information(self, "Run Workflow", "Workflow completed successfully.")

    def _on_run_failed(self, message: str) -> None:
        """Legacy method - kept for compatibility but no longer used."""
        QMessageBox.critical(self, "Run Workflow", message)

    def _cleanup_run(self) -> None:
        self._set_running_state(False)
        if self._run_worker is not None:
            self._run_worker.deleteLater()
            self._run_worker = None
        if self._run_thread is not None:
            self._run_thread.deleteLater()
            self._run_thread = None
        self._update_step_ui()

    def _cleanup_update(self) -> None:
        if self._update_worker is not None:
            self._update_worker.deleteLater()
            self._update_worker = None
        if self._update_thread is not None:
            self._update_thread.deleteLater()
            self._update_thread = None

        pending_download = self._pending_update_download
        self._pending_update_download = None
        if pending_download is not None:
            self._start_update_download(pending_download)
            return

        self._update_step_ui()

    def closeEvent(self, event) -> None:
        if self._switching_project:
            event.accept()
            return

        if self._run_thread is not None:
            QMessageBox.information(self, "Run In Progress", "Please wait for the workflow to finish before closing.")
            event.ignore()
            return

        if self._update_thread is not None:
            QMessageBox.information(self, "Update In Progress", "Please wait for the update process to finish before closing.")
            event.ignore()
            return

        if not self._has_unsaved_changes:
            event.accept()
            return

        response = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Save before closing?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        if response == QMessageBox.Save:
            if self.save_state(notify=False):
                event.accept()
            else:
                event.ignore()
        elif response == QMessageBox.Discard:
            event.accept()
        else:
            event.ignore()


def _create_splash_screen_pixmap(width: int = 600, height: int = 300) -> QPixmap:
    """Create a visually appealing splash screen with gradient background and branding."""
    pixmap = QPixmap(width, height)
    painter = QPainter(pixmap)
    
    # Create gradient background
    gradient = QLinearGradient(0, 0, 0, height)
    gradient.setColorAt(0, QColor("#0f172a"))  # Dark blue top
    gradient.setColorAt(0.5, QColor("#1e293b"))  # Slate middle
    gradient.setColorAt(1, QColor("#0f172a"))  # Dark blue bottom
    painter.fillRect(pixmap.rect(), gradient)
    
    # Draw decorative top accent bar
    painter.fillRect(0, 0, width, 4, QColor("#3b82f6"))  # Blue accent

    logo = _app_logo_pixmap(96)
    if not logo.isNull():
        logo_x = 40
        logo_y = 28
        painter.drawPixmap(logo_x, logo_y, logo)
    
    # Draw title
    title_font = QFont("Segoe UI", 42, QFont.Bold)
    painter.setFont(title_font)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(QRect(140, 50, width - 180, 100), Qt.AlignLeft | Qt.AlignVCenter, "imWEBs")
    
    # Draw subtitle
    subtitle_font = QFont("Segoe UI", 14)
    subtitle_font.setItalic(True)
    painter.setFont(subtitle_font)
    painter.setPen(QColor("#cbd5e1"))
    painter.drawText(QRect(140, 130, width - 180, 50), Qt.AlignLeft | Qt.AlignVCenter, "Integrated Model for Watershed Evaluation of BMPs")
    
    # Draw version/footer
    footer_font = QFont("Segoe UI", 10)
    painter.setFont(footer_font)
    painter.setPen(QColor("#94a3b8"))
    painter.drawText(QRect(40, height - 35, width - 80, 25), Qt.AlignCenter, "University of Guelph")
    
    painter.end()
    return pixmap


def main(argv: list[str] | None = None) -> int:
    startup_t0 = time.perf_counter()
    startup_log_dir = Path(tempfile.gettempdir()) / "imwebs_desktop"
    startup_log_dir.mkdir(parents=True, exist_ok=True)
    startup_log_path = startup_log_dir / "startup_timing.log"

    def _rotate_startup_log(max_lines: int = 600) -> None:
        if not startup_log_path.exists():
            return
        try:
            lines = startup_log_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return
        if len(lines) <= max_lines:
            return
        trimmed = "\n".join(lines[-max_lines:]) + "\n"
        try:
            startup_log_path.write_text(trimmed, encoding="utf-8")
        except OSError:
            return

    _rotate_startup_log()

    def _log_startup(stage: str) -> None:
        elapsed = time.perf_counter() - startup_t0
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | +{elapsed:7.3f}s | {stage}"
        with startup_log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    app = QApplication(argv or sys.argv)
    app_icon = _app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    _log_startup("QApplication created")

    service = ImwebsDesktopService()
    warmup_done = threading.Event()
    warmup_error: list[Exception] = []

    def _warm_dependencies() -> None:
        try:
            _log_startup("Warm-up thread started")
            service.warm_up_dependencies()
            _log_startup("Warm-up thread completed")
        except Exception as exc:
            warmup_error.append(exc)
            _log_startup(f"Warm-up thread failed: {exc}")
        finally:
            warmup_done.set()

    threading.Thread(target=_warm_dependencies, daemon=True).start()
    _log_startup("Warm-up launched (background)")

    project_dialog = ProjectDialog()
    _log_startup("Project dialog created")

    dialog_t0 = time.perf_counter()
    dialog_result = project_dialog.exec()
    _log_startup(f"Project dialog closed (result={dialog_result}, duration={time.perf_counter() - dialog_t0:.3f}s)")
    if dialog_result != QDialog.Accepted or not project_dialog.selected_project:
        _log_startup("Startup ended: dialog cancelled")
        return 0

    if not warmup_done.is_set():
        wait_t0 = time.perf_counter()
        splash_pixmap = _create_splash_screen_pixmap()
        splash = QSplashScreen(splash_pixmap)
        splash.showMessage("Finalizing startup...", Qt.AlignBottom | Qt.AlignHCenter, QColor("#cbd5e1"))
        splash.show()
        while not warmup_done.wait(0.05):
            app.processEvents()
        splash.close()
        _log_startup(f"Waited for warm-up after selection ({time.perf_counter() - wait_t0:.3f}s)")
    else:
        _log_startup("Warm-up already done when dialog closed")

    if warmup_error:
        _log_startup("Startup failed due to warm-up error")
        QMessageBox.critical(None, "Startup Failed", f"Failed to load imWEBs dependencies: {warmup_error[0]}")
        return 1

    init_t0 = time.perf_counter()
    window = MainWindow(project_dialog.selected_project, startup_logger=_log_startup)
    _log_startup(f"MainWindow initialized ({time.perf_counter() - init_t0:.3f}s)")
    window.showMaximized()
    _log_startup("MainWindow shown (startup complete)")
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())