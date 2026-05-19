import yaml, sys

from pathlib import Path
from pydantic import ValidationError

from models.cronjob_pipeline_config_models import PipelineConfig
from .executors.cronjob_config_loader import CronjobConfigLoader
from .executors.cronjob_config_builder import CronjobConfigBuilder

class Processor:
  def __init__(self, config_path: str):
    self._load_and_validate_config(config_path=config_path)
    self._set_pipeline_file_path(config_path=config_path)

  def _load_and_validate_config(self, config_path: str):
    if not Path(config_path).exists():
      print(f"❌ Config file not found: {config_path}")
      sys.exit(1)
    
    try:
      with open(config_path, 'r') as f:
        yaml_data = yaml.safe_load(f)

      self.pipeline_config = PipelineConfig(**yaml_data)
    except ValidationError as e:
      print(f"❌ Invalid config file:")

      for error in e.errors():
        print(f"   - {error['loc']}: {error['msg']}")
      
      sys.exit(1)

  def _set_pipeline_file_path(self, config_path: str):
    resolved = str(Path(config_path).resolve().parent)
    self.pipeline_config.pipeline_file_path = resolved

  def execute(self):
    cronjob_config_loader = CronjobConfigLoader(self.pipeline_config)
    cronjob_config_loader_result = cronjob_config_loader.execute()

    cronjob_pipeline_builder = CronjobConfigBuilder(self.pipeline_config, cronjob_config_loader_result)
    cronjob_pipeline_builder_result = cronjob_pipeline_builder.execute()

    print(cronjob_pipeline_builder_result)