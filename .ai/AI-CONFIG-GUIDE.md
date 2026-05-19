# promql-cronjob-builder — Config Guide
<!-- last human review: -->
<!-- last ai update: 2026-05-19 -->

Maps each YAML config template to its model file, fields, and design decisions.
See `AI-PROGRAM-GUIDE.md` for structure. See `AI-PYTHON-GUIDE.md` for code conventions.

---

## Config Files Map

| YAML template | Model file | Top-level model |
|---|---|---|
| `cronjob_pipeline_config.yaml` | `cronjob_pipeline_config_models.py` | `PipelineConfig` |
| `server_config.yaml` | `server_config_models.py` | `ServerConfigs` |
| `promql_config.yaml` | `promql_config_models.py` | `PromqlConfigs` |
| `range_config.yaml` | `range_config_models.py` | `RangeConfigs` |
| `output_config.yaml` | `output_config_models.py` | `OutputConfigs` |

One YAML template = one model file. Never merge models from different config files.

---

## cronjob_pipeline_config.yaml → `cronjob_pipeline_config_models.py`

Entry point config — passed to `main.py -c`. References all other configs by string ID.

```yaml
cronjob_pipeline_export_file: "./output_pipeline.yaml"  # path to write the built cronjob config

config_files:
  file_path: "./"                          # base dir relative to this file's location
  server_config: "server_config.yaml"
  promql_config: "promql_config.yaml"
  output_config: "output_config.yaml"
  range_config: "range_config.yaml"

server_configs:                            # list[str] — shared across all pipelines
  - server_1

pipelines:
  - id: cpu_query_120_days_back
    metadata:
      cluster_name: REQUEST                # free-form — any key/value accepted
      environment: REQUEST
    promql_config_id: query_range_1        # str — references QueryConfig.id
    output_config_id: output_1             # str — references OutputConfig.id
    range_config_id: range_1              # str — references RangeConfig.id
```

**Models:** `PipelineConfig` → `ConfigFiles` + `server_configs` + `list[PipelineItem]`

`PipelineConfig` fields:

| Field | Type | Note |
|---|---|---|
| `pipeline_file_path` | `Optional[str]` | injected by Processor at runtime — not in YAML |
| `cronjob_pipeline_export_file` | `str` | output file path for the built cronjob YAML |
| `config_files` | `ConfigFiles` | paths to each sub-config YAML file |
| `server_configs` | `list[str]` | shared across all pipelines — list of ServerConfig IDs |
| `pipelines` | `list[PipelineItem]` | pipeline definitions |

`ConfigFiles` fields:

| Field | Type | Note |
|---|---|---|
| `file_path` | `str` | base dir, combined with each filename below |
| `server_config` | `str` | filename of server_config YAML |
| `promql_config` | `str` | filename of promql_config YAML |
| `output_config` | `str` | filename of output_config YAML |
| `range_config` | `str` | filename of range_config YAML |

`PipelineItem` fields:

| Field | Type | Note |
|---|---|---|
| `id` | `str` | unique pipeline identifier |
| `metadata` | `dict[str, Any]` | free-form, no fixed schema |
| `promql_config_id` | `str` | references `QueryConfig.id` |
| `output_config_id` | `str` | references `OutputConfig.id` |
| `range_config_id` | `str` | references `RangeConfig.id` |

---

## server_config.yaml → `server_config_models.py`

Prometheus server connection settings.

```yaml
server_configs:
  - id: server_1
    url: "http://localhost:9090"
    api: "api/v1"        # optional, default api/v1
    timeout: 30          # optional, default 30
    auth:                # optional block
      type: none         # none | bearer | basic
    headers: {}
```

**Models:** `ServerConfigs` → `list[ServerConfig]`

- `auth` is `Optional[AuthConfig]` — has `type` + optional `token` / `username` / `password`
- `headers` defaults to `{}`

---

## promql_config.yaml → `promql_config_models.py`

PromQL range query definitions. This project executes range queries only — no `type` field.

```yaml
promql_configs:
  - id: "query_range_1"
    expr: 'cpu_usage_seconds_total{job="node_exporter"}'   # single-line — never block scalar (|)
    export_labels:
      - "instance"
      - "job"
```

**Models:** `PromqlConfigs` → `list[QueryConfig]`

- `expr` field name — not `query`
- no `type` field — range only
- `export_labels` defaults to `[]`

---

## range_config.yaml → `range_config_models.py`

Time range settings for range queries.

```yaml
range_configs:
  - id: range_1
    backward_amt: 30d    # d=day, m=month, y=year
    backward_steps: 4    # number of steps back
    query_step: 5m       # Prometheus resolution
```

**Models:** `RangeConfigs` → `list[RangeConfig]`

- `backward_amt` and `query_step` are plain `str` — format not validated by pydantic

---

## output_config.yaml → `output_config_models.py`

Output destinations. DB credentials live in K8S secrets — only env key names are stored here.

```yaml
db_connection_configs:
  - id: postgres_1
    type: postgres
    env_keys:
      host: OUTPUT_1_HOST        # env var key name — not the secret value
      port: OUTPUT_1_PORT
      username: OUTPUT_1_USERNAME
      password: OUTPUT_1_PASSWORD
      database: OUTPUT_1_DATABASE

schema_labels_mapping_configs:
  - id: mapping_1
    mapping:
      - query_label: instance
        table_column: instance
      - query_label: job
        table_column: job

output_configs:
  - id: output_1
    db_config:
      connections: postgres_1    # str — references DbConnectionConfig.id
      table: table_1
    mapping_config: mapping_1    # str — references SchemaLabelsMappingConfig.id
```

**Models:** `OutputConfigs` with three sections:

| Section | Model | Note |
|---|---|---|
| `db_connection_configs` | `list[DbConnectionConfig]` | named reusable connection profiles |
| `schema_labels_mapping_configs` | `list[SchemaLabelsMappingConfig]` | label → column mappings |
| `output_configs` | `list[OutputConfig]` | references db_connection and mapping by ID |

**Key design:** `OutputDbConfig.connections` is a `str` ID referencing `DbConnectionConfig.id`.
Never print or log `DbEnvKeys` values — they are env key names that resolve to secrets at runtime.