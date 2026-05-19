# promql-cronjob-builder — Program Guide
<!-- last human review: -->
<!-- last ai update: 2026-05-19 -->

Architecture, project structure, and executor chain.
See `AI-PYTHON-GUIDE.md` for coding conventions. See `AI-CONFIG-GUIDE.md` for config and model reference.

---

## Project Purpose

Reads a pipeline config YAML, loads referenced sub-configs (server, promql, range), builds a resolved `CronjobConfig` describing **what to query**, and exports it as a YAML file for the cronjob consumer to execute. Output/storage handling is intentionally left to the consumer.

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
    │   ├── cronjob_pipeline_config_models.py   # PipelineConfig, PipelineItem, ConfigFiles
    │   ├── server_config_models.py             # ServerConfigs, ServerConfig, AuthConfig
    │   ├── promql_config_models.py             # PromqlConfigs, QueryConfig
    │   ├── range_config_models.py              # RangeConfigs, RangeConfig
    │   ├── cronjob_export_config_models.py     # CronjobConfig, CronjobPipelineConfig,
    │   │                                       #   CronjobServerConfig, CronjobPromqlConfig,
    │   │                                       #   CronjobRangeConfig
    │   └── cronjob_config_loader_models.py     # ConfigLoadModel
    ├── processor/
    │   ├── processor.py                        # orchestrator: config load + executor chain
    │   └── executors/
    │       ├── cronjob_config_loader.py        # loads + validates server/promql/range YAMLs
    │       ├── cronjob_config_builder.py       # resolves IDs, builds CronjobConfig
    │       └── cronjob_config_exporter.py      # dumps CronjobConfig to YAML file
    ├── global_config.py                        # reserved — do not add models here
    ├── config_templates/
    │   ├── cronjob_pipeline_config.yaml        # entry point config template
    │   ├── server_config.yaml
    │   ├── promql_config.yaml
    │   ├── range_config.yaml
    │   └── output_config.yaml                  # standalone reference only — not loaded by pipeline
    └── test_suits/
        ├── global_test_config.py
        └── test_configs/
            ├── test_cronjob_pipeline_config.yaml
            ├── test_server_config.yaml
            ├── test_promql_config.yaml
            └── test_range_config.yaml
```

---

## Executor Chain

```
cronjob_pipeline_config.yaml
        ↓
    Processor.__init__
    ├── _load_and_validate_config()  →  PipelineConfig
    └── _set_pipeline_file_path()   →  PipelineConfig.pipeline_file_path (injected)
        ↓
    Processor.execute()
    ├── CronjobConfigLoader(pipeline_config)
    │       → resolves base: pipeline_file_path / config_files.file_path
    │       → loads + validates server_config, promql_config, range_config YAMLs
    │       → returns ConfigLoadModel
    │
    ├── CronjobConfigBuilder(pipeline_config, config_load_model)
    │       → resolves server IDs → list[CronjobServerConfig]
    │       → per pipeline: resolves promql_config_id + range_config_id
    │       → returns CronjobConfig
    │
    └── CronjobConfigExporter(pipeline_config, cronjob_config)
            → writes CronjobConfig.model_dump() as YAML
            → output path: pipeline_file_path / cronjob_pipeline_export_file
            → prints ✅ on success
```

---

## How to Look Things Up

| What you need | Where to look |
|---|---|
| CLI entry point | `program/app/main.py` |
| Executor chain | `program/processor/processor.py` |
| Config loader executor | `program/processor/executors/cronjob_config_loader.py` |
| Config builder executor | `program/processor/executors/cronjob_config_builder.py` |
| Config exporter executor | `program/processor/executors/cronjob_config_exporter.py` |
| Pipeline config model | `program/models/cronjob_pipeline_config_models.py` |
| Server config model | `program/models/server_config_models.py` |
| PromQL config model | `program/models/promql_config_models.py` |
| Range config model | `program/models/range_config_models.py` |
| Export output model | `program/models/cronjob_export_config_models.py` |
| Loader result model | `program/models/cronjob_config_loader_models.py` |
| YAML config templates | `program/config_templates/` |
| Test YAML configs | `program/test_suits/test_configs/` |
| Dependencies | `pyproject.toml` |