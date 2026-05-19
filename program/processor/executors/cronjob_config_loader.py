import sys, yaml

from models.cronjob_config_loader_models import ConfigLoadModel
from models.server_config_models import ServerConfigs
from models.promql_config_models import PromqlConfigs
from models.range_config_models import RangeConfigs
from models.cronjob_pipeline_config_models import PipelineConfig

from pathlib import Path
from typing import Any
from pydantic import ValidationError

class CronjobConfigLoader:
  def __init__(self, pipeline_config: PipelineConfig):
    self.pipeline_config = pipeline_config

  def _load_and_validate_subconfig(self, file_path: Path, model: type) -> Any:
    if not file_path.exists():
      print(f"❌ Config file not found: {file_path}")
      sys.exit(1)

    try:
      with open(file_path, 'r') as f:
        yaml_data = yaml.safe_load(f)
      return model(**yaml_data)

    except ValidationError as e:
      print(f"❌ Invalid config file: {file_path}")
      for error in e.errors():
        print(f"   - {error['loc']}: {error['msg']}")
      sys.exit(1)

  def _load_config_model(self):
    base = Path(self.pipeline_config.pipeline_file_path) / self.pipeline_config.config_files.file_path

    return ConfigLoadModel(
      server_configs=self._load_and_validate_subconfig(base / self.pipeline_config.config_files.server_config, ServerConfigs),
      promql_configs=self._load_and_validate_subconfig(base / self.pipeline_config.config_files.promql_config, PromqlConfigs),
      range_configs=self._load_and_validate_subconfig(base / self.pipeline_config.config_files.range_config, RangeConfigs),
    )

  def execute(self):
    return self._load_config_model()