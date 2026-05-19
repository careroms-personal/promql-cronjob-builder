# promql-cronjob-builder

A Python CLI tool that reads a pipeline config and builds a structured cronjob YAML from PromQL range queries, Prometheus server settings, time ranges, and database output definitions.

---

## What It Does

1. Reads a **pipeline config** YAML that references sub-config files by path and items by ID
2. Loads and validates each sub-config (server, promql, range, output)
3. Resolves all ID references and builds a single **cronjob config** (`CronjobConfig`)
4. Exports the result as a YAML file for external use

---

## Requirements

- Python >= 3.9
- Dependencies managed via `pyproject.toml`

Install:
```bash
pip install -e .
```

---

## Usage

```bash
python -m app.main -c <path-to-pipeline-config.yaml>
```

Example:
```bash
python -m app.main -c ./test_suits/test_configs/test_cronjob_pipeline_config.yaml
```

On success, the built cronjob YAML is written to the path defined by `cronjob_pipeline_export_file` in the pipeline config.

---

## Config Files

The tool uses five YAML config files. The pipeline config is the entry point — the others are referenced from it.

### 1. Pipeline Config (entry point)

```yaml
cronjob_pipeline_export_file: "./output_pipeline.yaml"

config_files:
  file_path: "./"
  server_config: "server_config.yaml"
  promql_config: "promql_config.yaml"
  output_config: "output_config.yaml"
  range_config: "range_config.yaml"

server_configs:
  - server_1

pipelines:
  - id: cpu_query_30d
    metadata:
      cluster_name: my_cluster
      environment: production
    promql_config_id: cpu_query
    output_config_id: postgres_output
    range_config_id: 30d_4_5m
```

### 2. Server Config

```yaml
server_configs:
  - id: server_1
    url: "http://localhost:9090"
    api: "api/v1"
    timeout: 30
    auth:
      type: none    # none | bearer | basic
    headers: {}
```

### 3. PromQL Config

Range queries only. No `type` field required.

```yaml
promql_configs:
  - id: cpu_query
    expr: 'rate(node_cpu_seconds_total{mode!="idle"}[5m])'
    export_labels:
      - "instance"
      - "job"
```

### 4. Range Config

```yaml
range_configs:
  - id: 30d_4_5m
    backward_amt: 30d     # d=day, m=month, y=year
    backward_steps: 4     # number of steps back
    query_step: 5m        # Prometheus resolution
```

### 5. Output Config

DB credentials are resolved from environment variables at runtime — only the key names are stored here.

```yaml
db_connection_configs:
  - id: postgres_output
    type: postgres
    env_keys:
      host: POSTGRES_HOST
      port: POSTGRES_PORT
      username: POSTGRES_USERNAME
      password: POSTGRES_PASSWORD
      database: POSTGRES_DATABASE

schema_labels_mapping_configs:
  - id: label_mapping
    mapping:
      - query_label: instance
        table_column: instance

output_configs:
  - id: postgres_output
    db_config:
      connections: postgres_output
      table: cpu_metrics
    mapping_config: label_mapping
```

---

## Output

The exported YAML (`cronjob_pipeline_export_file`) contains the fully resolved `CronjobConfig` — servers, and per-pipeline promql, range, and output settings — ready for downstream consumption.

---

## Project Structure

```
program/
├── app/main.py                         # CLI entry point
├── models/                             # pydantic models (one file per config template)
├── processor/
│   ├── processor.py                    # orchestrator
│   └── executors/
│       ├── cronjob_config_loader.py    # loads sub-config YAMLs
│       ├── cronjob_config_builder.py   # resolves IDs, builds CronjobConfig
│       └── cronjob_config_exporter.py  # exports CronjobConfig to YAML
└── config_templates/                   # YAML templates for each config file
```

---

## Running Tests

```bash
pytest program/test_suits/
```