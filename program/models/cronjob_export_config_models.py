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

class CronjobDBMappingLabel2Column(BaseModel):
  query_label: str
  table_column: str

class CronjobDBMappingConfig(BaseModel):
  id: str
  mapping: list[CronjobDBMappingLabel2Column]

class CronjobDBConnectionConfig(BaseModel):
  host_env: str
  port_env: str
  username_env: str
  password_env: str
  database_env: str
  table: str
  mapping: CronjobDBMappingConfig

class CronjobOutputConfig(BaseModel):
  id: str
  db_type: str
  connection_config: CronjobDBConnectionConfig

class CronjobPipelineConfig(BaseModel):
  id: str
  metadata: dict[str, Any]
  promql_config: CronjobPromqlConfig
  range_config: CronjobRangeConfig
  output_config: CronjobOutputConfig

class CronjobConfig(BaseModel):
  servers: list[CronjobServerConfig]
  pipelines: list[CronjobPipelineConfig]
