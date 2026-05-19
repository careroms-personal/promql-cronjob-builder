import yaml

from models.cronjob_pipeline_config_models import PipelineConfig
from models.cronjob_export_config_models import CronjobConfig

from pathlib import Path

class CronjobConfigExporter:
  def __init__(self, pipeline_config: PipelineConfig, cronjob_build_result: CronjobConfig):
    self.pipeline_config = pipeline_config
    self.cronjob_build_result = cronjob_build_result

  def _export_cronjob_yaml(self):
    export_file_path = Path(self.pipeline_config.pipeline_file_path) / self.pipeline_config.cronjob_pipeline_export_file

    with open(export_file_path, 'w') as f:
      yaml.dump(
        self.cronjob_build_result.model_dump(exclude_none=True),
        f,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
      )
    
    print(f"✅ Exported to {export_file_path}")

  def execute(self):
    self._export_cronjob_yaml()