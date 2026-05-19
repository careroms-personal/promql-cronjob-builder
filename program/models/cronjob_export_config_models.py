from pydantic import BaseModel
from typing import Any

class CronjobServerConfig(BaseModel):
  id: str
  url: str
  api: str
  timeout: int = 30
  auth: dict
  headers: dict

class CronjobRangeConfig(BaseModel):
  id: str
  backward_amt: str
  backward_steps: int
  query_step: str

class CronjobPromqlConfig(BaseModel):
  id: str
  expr: str
  export_labels: list[str]

class CronjobPipelineConfig(BaseModel):
  id: str
  metadata: dict[str, Any]
  promql_config: CronjobPromqlConfig
  range_config: CronjobRangeConfig

class CronjobConfig(BaseModel):
  servers: list[CronjobServerConfig]
  pipelines: list[CronjobPipelineConfig]