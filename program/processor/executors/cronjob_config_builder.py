import sys

from models.cronjob_pipeline_config_models import PipelineConfig
from models.server_config_models import ServerConfig
from models.promql_config_models import QueryConfig
from models.range_config_models import RangeConfig
from models.output_config_models import *
from models.cronjob_export_config_models import *
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
      auth=server_config.auth.model_dump() if server_config.auth else {},
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
  
  def _create_cronjob_db_connection_config(self, db_connection_config: DbConnectionConfig, schema_label_mapping_config: SchemaLabelsMappingConfig, output_config: OutputConfig):
    return CronjobOutputConfig(
      id=output_config.id,
      db_type=db_connection_config.type,
      connection_config=CronjobDBConnectionConfig(
        host_env=db_connection_config.env_keys.host,
        port_env=db_connection_config.env_keys.port,
        database_env=db_connection_config.env_keys.database,
        username_env=db_connection_config.env_keys.username,
        password_env=db_connection_config.env_keys.password,
        table=output_config.db_config.table,
        mapping=CronjobDBMappingConfig(
          id=schema_label_mapping_config.id,
          mapping=[
            CronjobDBMappingLabel2Column(
              query_label=m.query_label,
              table_column=m.table_column,
            )
            for m in schema_label_mapping_config.mapping
          ]
        )
      )
    )
  
  def _find_by_id(self, items: list, id: str, config_type: str):
    result = next((item for item in items if item.id == id), None)

    if result is None:
        print(f"❌ {config_type} '{id}' not found in config")
        sys.exit(1)
    return result
  
  def _create_cronjob_pipeline_config(self):
    servers = []

    for s in self.pipeline_config.server_configs:
      server_config = self._find_by_id(
        self.config_model.server_configs.server_configs,
        s,
        "server_config"
      )

      servers.append(self._create_server_config(server_config=server_config))
    

    pipelines = []

    for p in self.pipeline_config.pipelines:
      promql_config = self._find_by_id(
        self.config_model.promql_configs.promql_configs,
        p.promql_config_id,
        "promql_config"
      )

      range_config = self._find_by_id(
        self.config_model.range_configs.range_configs if self.config_model.range_configs else [],
        p.range_config_id,
        "range_config"
      )

      output_config = self._find_by_id(
        self.config_model.output_configs.output_configs,
        p.output_config_id,
        "output_config"
      )

      db_connection_config = self._find_by_id(
        self.config_model.output_configs.db_connection_configs,
        output_config.db_config.connections,
        "db_connection_config"
      )

      schema_label_mapping_config = self._find_by_id(
        self.config_model.output_configs.schema_labels_mapping_configs,
        output_config.mapping_config,
        "schema_label_mapping_config"
      )

      pipelines.append(CronjobPipelineConfig(
        id=p.id,
        metadata=p.metadata,
        promql_config=self._create_cronjob_promql_config(promql_config),
        range_config=self._create_cronjob_range_config(range_config),
        output_config=self._create_cronjob_db_connection_config(
          db_connection_config=db_connection_config,
          schema_label_mapping_config=schema_label_mapping_config,
          output_config=output_config,
        ),
      ))

    return pipelines

 
  def execute(self):
    return self._create_cronjob_pipeline_config()