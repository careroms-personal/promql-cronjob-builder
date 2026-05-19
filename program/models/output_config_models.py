from pydantic import BaseModel
from typing import Literal

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

class OutputConfigs(BaseModel):
  db_connection_configs: list[DbConnectionConfig]
  schema_labels_mapping_configs: list[SchemaLabelsMappingConfig]
  output_configs: list[OutputConfig]
