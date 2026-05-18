from pydantic import BaseModel
from typing import Optional, Literal

# --- Server Config (server_config.yaml) ---

class AuthConfig(BaseModel):
  type: Literal["none", "bearer", "basic"] = "none"
  token: Optional[str] = None
  username: Optional[str] = None
  password: Optional[str] = None

class ServerConfig(BaseModel):
  id: str
  url: str
  api: str = "api/v1"
  timeout: int = 30
  auth: Optional[AuthConfig] = None
  headers: dict[str, str] = {}

class ServersConfig(BaseModel):
  servers: list[ServerConfig]

# --- Query Config (promql_config.yaml) ---

class QueryConfig(BaseModel):
  id: str
  expr: str
  type: Literal["instant", "range"]
  export_labels: list[str] = []

class QueriesConfig(BaseModel):
  queries: list[QueryConfig]

# --- Range Config (range_config.yaml) ---

class RangeConfig(BaseModel):
  id: str
  backward_amt: str
  backward_steps: int
  query_step: str

class RangesConfig(BaseModel):
  ranges: list[RangeConfig]

# --- Output Config (output_config.yaml) ---

class DbEnvKeys(BaseModel):
  host: str
  port: str
  username: str
  password: str
  database: str

class DbConnectionConfig(BaseModel):
  id: str
  type: Literal["postgres"]
  env_keys: DbEnvKeys

class SchemaLabelMapping(BaseModel):
  query_label: str
  table_column: str

class SchemaLabelsMappingConfig(BaseModel):
  id: str
  mapping: list[SchemaLabelMapping]

class OutputDbConfig(BaseModel):
  connections: str
  table: str

class OutputConfig(BaseModel):
  id: str
  db_config: OutputDbConfig
  mapping_config: str

class OutputsConfig(BaseModel):
  db_connection_configs: list[DbConnectionConfig]
  schema_labels_mapping_configs: list[SchemaLabelsMappingConfig]
  outputs: list[OutputConfig]

# --- Pipeline Config (cronjob_pipeline_config.yaml) ---

class PipelineMetadata(BaseModel):
  cluster_name: str
  environment: str

class PipelineItem(BaseModel):
  id: str
  metadata: PipelineMetadata
  promql_config: str
  output_config: str
  server_configs: list[str]
  range_configs: list[str]

class PipelineConfig(BaseModel):
  config_file_path: str
  pipelines: list[PipelineItem]
