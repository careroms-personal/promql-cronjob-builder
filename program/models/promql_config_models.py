from pydantic import BaseModel

class QueryConfig(BaseModel):
  id: str
  expr: str
  export_labels: list[str] = []

class PromqlConfigs(BaseModel):
  promql_configs: list[QueryConfig]