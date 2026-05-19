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

`output_config.yaml` exists as a standalone reference template but is NOT part of the pipeline — output handling is left to the cronjob consumer.

One YAML template = one model file. Never merge models from different config files.

---

## cronjob_pipeline_config.yaml → `cronjob_pipeline_config_models.py`

Entry point config — passed to `main.py -c`. Defines what to query (server + promql + range only).

```yaml
cronjob_pipeline_export_file: "./query_pipeline.yaml"  # output path for the built cronjob YAML

config_files:
  file_path: "./"                    # base dir relative to this file's location
  server_config: "server_config.yaml"
  promql_config: "promql_config.yaml"
  range_config: "range_config.yaml"

server_configs:                      # list[str] — shared across all pipelines
  - server_1

pipelines:
  - id: cpu_query_120_days_back
    metadata:
      cluster_name: REQUEST          # free-form — any key/value accepted
      environment: REQUEST
    promql_config_ids:               # list[str] — one or more QueryConfig IDs
      - query_range_1
    range_config_ids:                # list[str] — one or more RangeConfig IDs
      - range_1
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
| `range_config` | `str` | filename of range_config YAML |

`PipelineItem` fields:

| Field | Type | Note |
|---|---|---|
| `id` | `str` | unique pipeline identifier |
| `metadata` | `dict[str, Any]` | free-form, no fixed schema |
| `promql_config_ids` | `list[str]` | one or more `QueryConfig.id` references |
| `range_config_ids` | `list[str]` | one or more `RangeConfig.id` references |

Each pipeline expands to `len(promql_config_ids) × len(range_config_ids)` entries via `itertools.product`. Each gets id `{pipeline_id}__{promql_id}__{range_id}`.

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

PromQL range query definitions. Range queries only — no `type` field.

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