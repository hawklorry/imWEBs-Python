from __future__ import annotations

from configparser import ConfigParser, Error as ConfigParserError
from functools import lru_cache
from pathlib import Path
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from typing import Callable
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen, urlretrieve

from .definitions import FieldDefinition


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@lru_cache(maxsize=1)
def _load_imwebs_dependencies():
    from imWEBs.config.model_config import ModelConfig
    from imWEBs.config.scenario_config import ScenarioConfig
    from imWEBs.imwebs import imWEBs

    return ModelConfig, ScenarioConfig, imWEBs


LogCallback = Callable[[str], None]
UPDATE_REPO_OWNER = "hawklorry"
UPDATE_REPO_NAME = "imWEBs-Python"



class CallbackLogHandler(logging.Handler):
    def __init__(self, callback: LogCallback):
        super().__init__(level=logging.INFO)
        self._callback = callback
        self.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        self._callback(self.format(record))


class LogCapture:
    def __init__(self, callback: LogCallback):
        self._callback = callback
        self._handler = CallbackLogHandler(callback)
        self._root_logger = logging.getLogger()
        self._previous_level = self._root_logger.level

    def __enter__(self):
        self._root_logger.setLevel(logging.INFO)
        self._root_logger.addHandler(self._handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._root_logger.removeHandler(self._handler)
        self._root_logger.setLevel(self._previous_level)


class ImwebsDesktopService:
    def warm_up_dependencies(self) -> None:
        _load_imwebs_dependencies()

    def create_model_template(self, file_path: str) -> None:
        ModelConfig, _, _ = _load_imwebs_dependencies()
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        ModelConfig().create_template(str(target))

    def create_scenario_template(self, file_path: str) -> None:
        _, ScenarioConfig, _ = _load_imwebs_dependencies()
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        ScenarioConfig().create_template(str(target))

    def ensure_config_exists(self, file_path: str) -> None:
        """Create config file with template structure if it doesn't exist.
        This is called on first save to lazy-initialize config files.
        """
        target = Path(file_path)
        if target.exists():
            return
        
        target.parent.mkdir(parents=True, exist_ok=True)
        ModelConfig, ScenarioConfig, _ = _load_imwebs_dependencies()
        if "model" in file_path.lower():
            ModelConfig().create_template(str(target))
        elif "scenario" in file_path.lower():
            ScenarioConfig().create_template(str(target))

    def load_config_values(self, file_path: str, fields: list[FieldDefinition]) -> dict[tuple[str, str], str]:
        parser = ConfigParser()
        try:
            parser.read(file_path, encoding="utf-8")
        except ConfigParserError:
            parser = ConfigParser()
        values: dict[tuple[str, str], str] = {}
        for field in fields:
            if parser.has_option(field.section, field.name):
                values[(field.section, field.name)] = parser.get(field.section, field.name)
            else:
                values[(field.section, field.name)] = ""
        return values

    def save_config_values(self, file_path: str, fields: list[FieldDefinition], values: dict[tuple[str, str], str]) -> None:
        target = Path(file_path)
        
        if not target.exists():
            self.ensure_config_exists(str(target))
        
        parser = ConfigParser()

        if target.exists():
            try:
                parser.read(target, encoding="utf-8")
            except ConfigParserError:
                parser = ConfigParser()

        for field in fields:
            if field.section not in parser:
                parser[field.section] = {}
            parser[field.section][field.name] = values.get((field.section, field.name), "")

        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as config_file:
            parser.write(config_file)

    def validate_configs(self, model_config_path: str, scenario_config_path: str) -> None:
        ModelConfig, ScenarioConfig, _ = _load_imwebs_dependencies()
        ModelConfig(model_config_path)
        ScenarioConfig(scenario_config_path)

    def get_hydroclimate_date_range(self, db_path: str) -> tuple[str, str] | None:
        """Return (start_date, end_date) strings in yyyy-mm-dd format from the hydroclimate DB.
        Returns None if the file doesn't exist or the DB cannot be read.
        """
        try:
            if not Path(db_path).exists():
                return None
            from imWEBs.database.hydroclimate.hydroclimate_database import HydroClimateDatabase
            db = HydroClimateDatabase(db_path)
            start = db.data_start_date
            end = db.data_end_date
            return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        except Exception:
            return None

    def run_action(self, model_config_path: str, scenario_config_path: str, action: str, log_callback: LogCallback) -> None:
        _, _, imWEBs = _load_imwebs_dependencies()
        if not model_config_path or not scenario_config_path:
            raise ValueError("Both model and scenario config paths are required.")

        if not os.path.exists(model_config_path):
            raise ValueError(f"Model config not found: {model_config_path}")

        if not os.path.exists(scenario_config_path):
            raise ValueError(f"Scenario config not found: {scenario_config_path}")

        with LogCapture(log_callback):
            log_callback(f"Loading model config: {model_config_path}")
            log_callback(f"Loading scenario config: {scenario_config_path}")
            runner = imWEBs(model_config_path, scenario_config_path)
            method = getattr(runner, action)
            log_callback(f"Running action: {action}")
            method()
            log_callback("Workflow completed.")

    def run_model_action(self, model_config_path: str, action: str, log_callback: LogCallback) -> None:
        ModelConfig, _, _ = _load_imwebs_dependencies()
        if not model_config_path:
            raise ValueError("Model config path is required.")

        if not os.path.exists(model_config_path):
            raise ValueError(f"Model config not found: {model_config_path}")

        with LogCapture(log_callback):
            log_callback(f"Loading model config: {model_config_path}")
            model_config = ModelConfig(model_config_path)
            if not hasattr(model_config, action):
                raise ValueError(f"Unsupported model workflow action: {action}")
            method = getattr(model_config, action)
            log_callback(f"Running model workflow: {action}")
            method()
            log_callback("Model workflow completed.")

    def generate_scenario_model_structure(self, scenario_config_path: str, log_callback: LogCallback) -> None:
        _, ScenarioConfig, _ = _load_imwebs_dependencies()
        if not scenario_config_path:
            raise ValueError("Scenario config path is required.")

        if not os.path.exists(scenario_config_path):
            raise ValueError(f"Scenario config not found: {scenario_config_path}")

        with LogCapture(log_callback):
            log_callback(f"Loading scenario config: {scenario_config_path}")
            scenario_config = ScenarioConfig(scenario_config_path)
            log_callback("Generating scenario model structure...")
            scenario_config.generate_model_structure()
            log_callback("Scenario model structure generation completed.")

    @staticmethod
    def _parse_version(version: str) -> tuple[int, ...]:
        cleaned = version.strip().lower().lstrip("v")
        parts = re.findall(r"\d+", cleaned)
        if not parts:
            return (0,)
        return tuple(int(part) for part in parts)

    @classmethod
    def _is_newer_version(cls, candidate: str, current: str) -> bool:
        candidate_tuple = cls._parse_version(candidate)
        current_tuple = cls._parse_version(current)
        max_len = max(len(candidate_tuple), len(current_tuple))
        padded_candidate = candidate_tuple + (0,) * (max_len - len(candidate_tuple))
        padded_current = current_tuple + (0,) * (max_len - len(current_tuple))
        return padded_candidate > padded_current

    def check_for_updates(
        self,
        current_version: str,
        repo_owner: str = UPDATE_REPO_OWNER,
        repo_name: str = UPDATE_REPO_NAME,
    ) -> dict[str, str | bool]:
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        request = Request(api_url, headers={"User-Agent": "imWEBs-Desktop-Updater"})

        try:
            with urlopen(request, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ValueError(f"Update check failed (HTTP {exc.code}).") from exc
        except URLError as exc:
            raise ValueError(f"Update check failed: {exc.reason}") from exc
        except Exception as exc:
            raise ValueError(f"Update check failed: {exc}") from exc

        latest_version = str(payload.get("tag_name", "")).strip() or "0.0.0"
        release_notes = str(payload.get("body", "")).strip()
        release_url = str(payload.get("html_url", "")).strip()

        installer_asset = None
        for asset in payload.get("assets", []):
            name = str(asset.get("name", "")).lower()
            url = str(asset.get("browser_download_url", "")).strip()
            if not url:
                continue
            if name.endswith(".exe") and ("setup" in name or "installer" in name):
                installer_asset = asset
                break

        if installer_asset is None:
            for asset in payload.get("assets", []):
                name = str(asset.get("name", "")).lower()
                url = str(asset.get("browser_download_url", "")).strip()
                if name.endswith(".exe") and url:
                    installer_asset = asset
                    break

        installer_url = ""
        installer_name = ""
        if installer_asset is not None:
            installer_url = str(installer_asset.get("browser_download_url", "")).strip()
            installer_name = str(installer_asset.get("name", "")).strip()

        has_update = bool(installer_url) and self._is_newer_version(latest_version, current_version)
        return {
            "update_available": has_update,
            "current_version": current_version,
            "latest_version": latest_version,
            "installer_url": installer_url,
            "installer_name": installer_name,
            "release_notes": release_notes,
            "release_url": release_url,
        }

    def download_installer(self, installer_url: str, installer_name: str | None = None) -> str:
        if not installer_url:
            raise ValueError("Installer URL is missing.")

        parsed_name = (installer_name or "").strip()
        if not parsed_name:
            parsed_name = Path(installer_url).name or "imwebs-desktop-setup.exe"
        if not parsed_name.lower().endswith(".exe"):
            parsed_name = f"{parsed_name}.exe"

        update_dir = Path(tempfile.gettempdir()) / "imwebs_desktop_updates"
        update_dir.mkdir(parents=True, exist_ok=True)
        target = update_dir / parsed_name

        try:
            urlretrieve(installer_url, target)
        except Exception as exc:
            raise ValueError(f"Failed to download installer: {exc}") from exc

        return str(target)

    def launch_installer(self, installer_path: str) -> None:
        installer = Path(installer_path)
        if not installer.exists():
            raise ValueError(f"Installer not found: {installer_path}")

        try:
            if sys.platform.startswith("win"):
                os.startfile(str(installer))
            else:
                subprocess.Popen([str(installer)])
        except Exception as exc:
            raise ValueError(f"Failed to launch installer: {exc}") from exc


class ProjectManager:
    """Manages imWEBs project files (.imwebsprj) with associated model and scenario configs."""

    PROJECT_EXTENSION = ".imwebsprj"
    RECENT_PROJECTS_FILE = Path.home() / ".imwebs_recent_projects.json"

    @staticmethod
    def _normalize_project_data(project_data: dict, project_path: Path) -> dict:
        project_name = project_data.get("name") or project_path.stem
        scenarios = project_data.get("scenarios")
        if not isinstance(scenarios, list):
            scenarios = []
        normalized_scenarios: list[str] = []
        for name in scenarios:
            if isinstance(name, str):
                trimmed = name.strip()
                if trimmed and trimmed not in normalized_scenarios:
                    normalized_scenarios.append(trimmed)
        if not normalized_scenarios:
            normalized_scenarios = ["scenario1"]

        active_scenario = project_data.get("active_scenario")
        if not isinstance(active_scenario, str) or not active_scenario.strip():
            active_scenario = normalized_scenarios[0]
        else:
            active_scenario = active_scenario.strip()
            if active_scenario not in normalized_scenarios:
                normalized_scenarios.insert(0, active_scenario)

        return {
            "name": project_name,
            "project_path": str(project_path),
            "scenarios": normalized_scenarios,
            "active_scenario": active_scenario,
        }

    @staticmethod
    def create_project(project_path: str) -> dict:
        """Create a new project file (config files are co-located).
        
        Args:
            project_path: Full path to the project file (e.g., /path/to/myproject.imwebsprj)
            
        Returns:
            Project data dict with name and project_path.
        """
        project_path = Path(project_path)
        if not str(project_path).endswith(ProjectManager.PROJECT_EXTENSION):
            project_path = project_path.with_suffix(ProjectManager.PROJECT_EXTENSION)

        project_path.parent.mkdir(parents=True, exist_ok=True)
        project_name = project_path.stem

        project_data = ProjectManager._normalize_project_data(
            {
                "name": project_name,
                "project_path": str(project_path),
                "scenarios": ["scenario1"],
                "active_scenario": "scenario1",
            },
            project_path,
        )

        with project_path.open("w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2)

        ProjectManager._add_recent_project(str(project_path))
        return project_data

    @staticmethod
    def load_project(project_path: str) -> dict:
        """Load an existing project file.
        
        Args:
            project_path: Full path to the project file
            
        Returns:
            Project data dict with model_config and scenario_config paths.
        """
        project_path = Path(project_path)
        if not project_path.exists():
            raise FileNotFoundError(f"Project file not found: {project_path}")

        with project_path.open("r", encoding="utf-8") as f:
            project_data = json.load(f)

        project_data = ProjectManager._normalize_project_data(project_data, project_path)

        ProjectManager._add_recent_project(str(project_path))
        return project_data

    @staticmethod
    def save_project(project_path: str, project_data: dict) -> dict:
        """Persist project metadata to disk and return normalized data."""
        path = Path(project_path)
        normalized = ProjectManager._normalize_project_data(project_data, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(normalized, f, indent=2)
        return normalized

    @staticmethod
    def get_recent_projects() -> list[dict]:
        """Get list of recently opened projects.
        
        Returns:
            List of dicts with 'path' and 'name' keys, sorted by most recent first.
        """
        if not ProjectManager.RECENT_PROJECTS_FILE.exists():
            return []

        try:
            with ProjectManager.RECENT_PROJECTS_FILE.open("r", encoding="utf-8") as f:
                recent = json.load(f)
            
            valid_projects = [p for p in recent if Path(p["path"]).exists()]
            return valid_projects
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def get_last_project_folder() -> str:
        """Get the folder of the last opened project, or Documents folder if none exist.
        
        Returns:
            Full path to the last used project folder, or Documents folder as fallback.
        """
        recent = ProjectManager.get_recent_projects()
        if recent:
            return str(Path(recent[0]["path"]).parent)
        
        documents_folder = Path.home() / "Documents"
        documents_folder.mkdir(parents=True, exist_ok=True)
        return str(documents_folder)

    @staticmethod
    def _add_recent_project(project_path: str) -> None:
        """Add a project to the recent projects list."""
        project_path = str(Path(project_path).resolve())
        recent = ProjectManager.get_recent_projects()

        existing_index = next(
            (i for i, p in enumerate(recent) if p["path"] == project_path), None
        )
        if existing_index is not None:
            recent.pop(existing_index)

        project_name = Path(project_path).stem
        recent.insert(0, {"path": project_path, "name": project_name})

        recent = recent[:10]

        ProjectManager.RECENT_PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with ProjectManager.RECENT_PROJECTS_FILE.open("w", encoding="utf-8") as f:
            json.dump(recent, f, indent=2)

