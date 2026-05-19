from models.server_config_models import ServerConfigs
from models.output_config_models import OutputConfigs
from models.promql_config_models import PromqlConfigs
from models.range_config_models import RangeConfigs

from pydantic import BaseModel

class ConfigLoadModel(BaseModel):
  server_configs: ServerConfigs
  output_configs: OutputConfigs
  promql_configs: PromqlConfigs
  range_configs: RangeConfigs | None