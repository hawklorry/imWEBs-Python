import logging
from .config import Config

logger = logging.getLogger(__name__)

class ScanrioConfig(Config):
    """Config for scenario creation"""

    def __init__(self, config_file: str = None):
        super().__init__(config_file)

    @property
    def config_variables(self)->str:
        return {"reservoir":["reservoir_parameter_csv"]}

