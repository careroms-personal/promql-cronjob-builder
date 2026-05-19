from pydantic import BaseModel
from typing import Any, Optional

class ConfigFiles(BaseModel):
  file_path: str
  server_config: str
  promql_config: str
  output_config: str
  range_config: str

class PipelineItem(BaseModel):
  id: str
  metadata: dict[str, Any]
  promql_config_id: str
  output_config_id: str
  range_config_id: str

class PipelineConfig(BaseModel):
  pipeline_file_path: Optional[str] = None
  cronjob_pipeline_export_file: str
  config_files: ConfigFiles
  server_configs: list[str]
  pipelines: list[PipelineItem]