# promql-cronjob-builder — Program Guide
<!-- last human review: -->
<!-- last ai update: 2026-05-19 -->

Architecture, project structure, and executor chain.
See `AI-PYTHON-GUIDE.md` for coding conventions. See `AI-CONFIG-GUIDE.md` for config and model reference.

---

## Project Purpose

Reads a pipeline config YAML, loads referenced sub-configs (server, promql, range, output), builds a structured cronjob config (`CronjobConfig`), and exports it.

---

## Project Structure

```
promql-cronjob-builder/
├── vibe-code-rule.yaml                          # AI instruction manifest — read first
├── pyproject.toml                               # dependencies (only place for deps)
├── .ai/
│   ├── AI-PRINCIPLE-GUIDE.md                   # design principles
│   ├── AI-PYTHON-GUIDE.md                      # coding conventions and patterns
│   ├── AI-CONFIG-GUIDE.md                      # config YAML + model reference
│   └── AI-PROGRAM-GUIDE.md                     # this file
└── program/
    ├── app/
    │   └── main.py                             # CLI entry — do not add logic here
    ├── models/
    │   ├── cronjob_pipeline_config_models.py   # PipelineConfig, PipelineItem
    │   ├── server_config_models.py             # ServersConfig, ServerConfig, AuthConfig
    │   ├── promql_config_models.py             # QueriesConfig, QueryConfig
    │   ├── range_config_models.py              # RangesConfig, RangeConfig
    │   ├── output_config_models.py             # OutputsConfig, OutputConfig, DbConnectionConfig,
    │   │                                       #   DbEnvKeys, SchemaLabelsMappingConfig, OutputDbConfig
    │   └── cronjob_export_config_models.py     # CronjobConfig, CronjobPipelineConfig,
    │                                           #   CronjobServerConfig, CronjobPromqlConfig,
    │                                           #   CronjobRangeConfig, CronjobOutputConfig,
    │                                           #   CronjobDBConnectionConfig, CronjobDBMappingConfig
    ├── processor/
    │   ├── processor.py                        # orchestrator: config load + executor chain
    │   └── executors/
    │       └── cronjob_config_builder.py       # builds CronjobConfig from PipelineConfig
    ├── global_config.py                        # reserved — do not add models here
    ├── config_templates/
    │   ├── cronjob_pipeline_config.yaml        # entry point config template
    │   ├── server_config.yaml
    │   ├── promql_config.yaml
    │   ├── range_config.yaml
    │   └── output_config.yaml
    └── test_suits/
        ├── global_test_config.py
        └── test_configs/
            ├── test_cronjob_pipeline_config.yaml
            ├── test_server_config.yaml
            ├── test_promql_config.yaml
            ├── test_range_config.yaml
            └── test_output_config.yaml
```

---

## Executor Chain

```
cronjob_pipeline_config.yaml
        ↓
    Processor.__init__
    └── _load_and_validate_config()  →  PipelineConfig
        ↓
    Processor.execute()
    └── CronjobConfigBuilder(pipeline_config)
            → resolves ID references across sub-configs
            → builds CronjobConfig
            → returns CronjobConfig  [WIP]
```

---

## How to Look Things Up

| What you need | Where to look |
|---|---|
| CLI entry point | `program/app/main.py` |
| Executor chain and flow | `program/processor/processor.py` |
| Cronjob builder executor | `program/processor/executors/cronjob_config_builder.py` |
| Pipeline config model | `program/models/cronjob_pipeline_config_models.py` |
| Server config model | `program/models/server_config_models.py` |
| PromQL config model | `program/models/promql_config_models.py` |
| Range config model | `program/models/range_config_models.py` |
| Output config model | `program/models/output_config_models.py` |
| Export output model | `program/models/cronjob_export_config_models.py` |
| YAML config templates | `program/config_templates/` |
| Test YAML configs | `program/test_suits/test_configs/` |
| Dependencies | `pyproject.toml` |
