from pydantic import BaseModel

class RangeConfig(BaseModel):
  id: str
  backward_amt: str
  backward_steps: int
  query_step: str

class RangeConfigs(BaseModel):
  range_configs: list[RangeConfig]
