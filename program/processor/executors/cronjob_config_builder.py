import sys
import itertools

from models.cronjob_pipeline_config_models import PipelineConfig
from models.server_config_models import ServerConfig
from models.promql_config_models import QueryConfig
from models.range_config_models import RangeConfig
from models.cronjob_export_config_models import CronjobConfig, CronjobPipelineConfig, CronjobServerConfig, CronjobPromqlConfig, CronjobRangeConfig
from models.cronjob_config_loader_models import ConfigLoadModel

class CronjobConfigBuilder:
  def __init__(self, pipeline_config: PipelineConfig, config_model: ConfigLoadModel):
    self.pipeline_config = pipeline_config
    self.config_model = config_model

  def _create_server_config(self, server_config: ServerConfig):
    return CronjobServerConfig(
      id=server_config.id,
      url=server_config.url,
      api=server_config.api,
      timeout=server_config.timeout,
      auth=server_config.auth.model_dump(exclude_none=True) if server_config.auth else {},
      headers=server_config.headers,
    )

  def _create_cronjob_promql_config(self, promql_config: QueryConfig):
    return CronjobPromqlConfig(
      id=promql_config.id,
      expr=promql_config.expr,
      export_labels=promql_config.export_labels,
    )

  def _create_cronjob_range_config(self, range_config: RangeConfig):
    return CronjobRangeConfig(
      id=range_config.id,
      backward_amt=range_config.backward_amt,
      backward_steps=range_config.backward_steps,
      query_step=range_config.query_step,
    )

  def _find_by_id(self, items: list, id: str, config_type: str):
    result = next((item for item in items if item.id == id), None)
    if result is None:
      print(f"❌ {config_type} '{id}' not found in config")
      sys.exit(1)
    return result

  def _build(self):
    servers = [
      self._create_server_config(
        self._find_by_id(self.config_model.server_configs.server_configs, s, "server_config")
      )
      for s in self.pipeline_config.server_configs
    ]

    pipelines = []
    for p in self.pipeline_config.pipelines:
      promql_configs = [
        self._find_by_id(
          self.config_model.promql_configs.promql_configs, pid, "promql_config"
        )
        for pid in p.promql_config_ids
      ]
      range_configs = [
        self._find_by_id(
          self.config_model.range_configs.range_configs if self.config_model.range_configs else [],
          rid, "range_config"
        )
        for rid in p.range_config_ids
      ]

      for promql_config, range_config in itertools.product(promql_configs, range_configs):
        pipelines.append(CronjobPipelineConfig(
          id=f"{p.id}__{promql_config.id}__{range_config.id}",
          metadata=p.metadata,
          promql_config=self._create_cronjob_promql_config(promql_config),
          range_config=self._create_cronjob_range_config(range_config),
        ))

    return CronjobConfig(servers=servers, pipelines=pipelines)

  def execute(self):
    return self._build()