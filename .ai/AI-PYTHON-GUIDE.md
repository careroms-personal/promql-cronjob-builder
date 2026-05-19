# promql-cronjob-builder — Python Guide
<!-- last human review: 2026 Mar 24 -->
<!-- last ai update: 2026-05-19 -->

Coding conventions and implementation patterns for this project.
See `AI-PROGRAM-GUIDE.md` for structure. See `AI-CONFIG-GUIDE.md` for config and model reference.

---

## Coding Conventions

- **Indentation:** 2 spaces — never 4 spaces or tabs
- **Error prefix:** `❌` for all fatal errors — `print(f"❌ ...")`
- **Success prefix:** `✅` for completion messages
- **Exit:** `sys.exit(1)` on any fatal error — never raise unhandled exceptions
- **YAML parsing:** `yaml.safe_load()` only — `yaml.load()` is forbidden
- **Imports:** explicit named imports — never wildcard `import *`

---

## Model Import Convention

Each YAML config template has exactly one model file. Import only from the matching file.

```python
from models.cronjob_pipeline_config_models import PipelineConfig, PipelineItem, ConfigFiles
from models.server_config_models import ServerConfigs, ServerConfig, AuthConfig
from models.promql_config_models import PromqlConfigs, QueryConfig
from models.range_config_models import RangeConfigs, RangeConfig
from models.output_config_models import OutputConfigs, OutputConfig, DbConnectionConfig, OutputDbConfig
from models.cronjob_export_config_models import CronjobConfig, CronjobPipelineConfig
from models.cronjob_config_loader_models import ConfigLoadModel
```

Never cross-import models between config model files.

---

## Core Patterns

### CLI Entry Point (`main.py`)

No logic — only wires CLI args to Processor.

```python
import argparse
from processor.processor import Processor

def main():
  parser = argparse.ArgumentParser(description="Build cronjob configs from PromQL pipeline config")
  parser.add_argument("-c", "--config", required=True, help="Path to config Yaml file")
  args = parser.parse_args()

  processor = Processor(args.config)
  processor.execute()

if __name__ == "__main__":
  main()
```

---

### Processor (`processor.py`)

Loads and validates the entry config, injects the resolved file path, then chains executors.

```python
class Processor:
  def __init__(self, config_path: str):
    self._load_and_validate_config(config_path)
    self._set_pipeline_file_path(config_path)

  def _set_pipeline_file_path(self, config_path: str):
    resolved = str(Path(config_path).resolve().parent)
    self.pipeline_config.pipeline_file_path = resolved

  def execute(self):
    loader = CronjobConfigLoader(self.pipeline_config)
    loader_result = loader.execute()

    builder = CronjobConfigBuilder(self.pipeline_config, loader_result)
    builder_result = builder.execute()

    exporter = CronjobConfigExporter(self.pipeline_config, builder_result)
    exporter.execute()
```

---

### Executor (`<duty>_executor.py`)

One duty per executor. Receives previous result + full config. Returns a typed pydantic model.

```python
class SomeExecutor:
  def __init__(self, previous_result: PreviousResult, config: PipelineConfig):
    self.previous_result = previous_result
    self.config = config

  def execute(self) -> ThisResult:
    ...
    return ThisResult(...)
```

**Naming:** `<duty>_executor.py` — e.g., `cronjob_config_loader.py`, `cronjob_config_builder.py`

---

### Sub-config Loading Pattern

Used in `CronjobConfigLoader` — loads a YAML file and validates it against a model.

```python
def _load_and_validate_subconfig(self, file_path: Path, model: type) -> Any:
  if not file_path.exists():
    print(f"❌ Config file not found: {file_path}")
    sys.exit(1)
  try:
    with open(file_path, 'r') as f:
      yaml_data = yaml.safe_load(f)
    return model(**yaml_data)
  except ValidationError as e:
    print(f"❌ Invalid config file: {file_path}")
    for error in e.errors():
      print(f"   - {error['loc']}: {error['msg']}")
    sys.exit(1)
```

Base path resolution: `Path(pipeline_file_path) / config_files.file_path / config_files.<name>`

---

### ID Resolution Pattern

Used in `CronjobConfigBuilder` — looks up a config item by `id` in a list.

```python
def _find_by_id(self, items: list, id: str, config_type: str):
  result = next((item for item in items if item.id == id), None)
  if result is None:
    print(f"❌ {config_type} '{id}' not found in config")
    sys.exit(1)
  return result
```

Always pass the inner list, not the wrapper model:
- ✅ `self.config_model.server_configs.server_configs`
- ❌ `self.config_model.server_configs`

---

### YAML Export Pattern

Used in `CronjobConfigExporter` — dumps a pydantic model to YAML.

```python
with open(export_file_path, 'w') as f:
  yaml.dump(
    result.model_dump(exclude_none=True),
    f,
    default_flow_style=False,
    allow_unicode=True,
    sort_keys=False
  )
print(f"✅ Exported to {export_file_path}")
```

---

## Error Handling

```python
# File not found
if not Path(config_path).exists():
  print(f"❌ Config file not found: {config_path}")
  sys.exit(1)

# Pydantic validation failure
except ValidationError as e:
  print(f"❌ Invalid config file: {file_path}")
  for error in e.errors():
    print(f"   - {error['loc']}: {error['msg']}")
  sys.exit(1)

# ID not found
print(f"❌ {config_type} '{id}' not found in config")
sys.exit(1)
```

Never swallow exceptions silently.

---

## Testing

Tests live in `program/test_suits/`. File names must be prefixed with `test_`.
Test YAML configs live in `program/test_suits/test_configs/`.
Shared fixtures and constants go in `global_test_config.py`.

Run tests with:
```bash
pytest program/test_suits/
```

---

## Dependencies

Managed in `pyproject.toml` only — never `requirements.txt`.

- `pydantic==2.12.5` — config and result model validation
- `PyYAML==6.0.3` — YAML parsing and export
- `requests>=2.31.0` — HTTP
- `pytest==9.0.2` — testing