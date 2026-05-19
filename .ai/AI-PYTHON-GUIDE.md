# promql-cronjob-builder — Python Guide
<!-- last human review: 2026 Mar 24 -->
<!-- last ai update: 2026-05-19 -->

Coding conventions and implementation patterns for this project.
See `AI-PROGRAM-GUIDE.md` for structure. See `AI-CONFIG-GUIDE.md` for config and model reference.

---

## Coding Conventions

- **Indentation:** 2 spaces — never 4 spaces or tabs
- **Error prefix:** `❌` for all fatal errors — `print(f"❌ ...")`
- **Exit:** `sys.exit(1)` on any fatal error — never raise unhandled exceptions
- **YAML parsing:** `yaml.safe_load()` only — `yaml.load()` is forbidden
- **Imports:** explicit named imports — never wildcard `import *`

---

## Model Import Convention

Each YAML config template has exactly one model file. Import only from the matching file.

```python
from models.cronjob_pipeline_config_models import PipelineConfig, PipelineItem
from models.server_config_models import ServersConfig, ServerConfig, AuthConfig
from models.promql_config_models import QueriesConfig, QueryConfig
from models.range_config_models import RangesConfig, RangeConfig
from models.output_config_models import OutputsConfig, OutputConfig, OutputDbConfig, DbEnvKeys
from models.cronjob_export_config_models import CronjobConfig, CronjobPipelineConfig
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

Loads and validates the entry config, then chains executors. No business logic.

```python
import yaml, sys
from pathlib import Path
from pydantic import ValidationError
from models.cronjob_pipeline_config_models import PipelineConfig
from processor.some_executor import SomeExecutor

class Processor:
  def __init__(self, config_path: str):
    self.config = self._load_and_validate_config(config_path)

  def _load_and_validate_config(self, config_path: str) -> PipelineConfig:
    if not Path(config_path).exists():
      print(f"❌ Config file not found: {config_path}")
      sys.exit(1)
    try:
      with open(config_path, 'r') as f:
        yaml_data = yaml.safe_load(f)
      return PipelineConfig(**yaml_data)
    except ValidationError as e:
      print(f"❌ Invalid config file:")
      for error in e.errors():
        print(f"   - {error['loc']}: {error['msg']}")
      sys.exit(1)

  def execute(self):
    self.some_executor = SomeExecutor(self.config)
    self.some_result = self.some_executor.execute()
```

---

### Executor (`<duty>_executor.py`)

One duty per executor. Receives previous result + full config. Returns a typed pydantic model.

```python
from models.cronjob_pipeline_config_models import PipelineConfig
from models.some_result_models import PreviousResult, ThisResult

class SomeExecutor:
  def __init__(self, previous_result: PreviousResult, config: PipelineConfig):
    self.previous_result = previous_result
    self.task_config = config.relevant_section

  def execute(self) -> ThisResult:
    data = self._process(self.previous_result)
    return ThisResult(...)

  def _process(self, input: PreviousResult) -> ...:
    ...
```

**Naming:** `<duty>_executor.py` — describes the duty, not the mechanism.

---

### Config Models

One model file per YAML config template. Each file has a top-level wrapper model and sub-models.

```python
# models/promql_config_models.py
from pydantic import BaseModel
from typing import Literal

class QueryConfig(BaseModel):
  id: str
  expr: str                          # not "query"
  type: Literal["instant", "range"]
  export_labels: list[str] = []

class QueriesConfig(BaseModel):
  queries: list[QueryConfig]
```

Top-level wrapper model = the model used to parse the entire YAML file via `**yaml_data`.

---

### Result Models

Typed outputs passed between executors. Live in `program/models/` alongside config models.

```python
from pydantic import BaseModel

class SomeResult(BaseModel):
  items: list[str]
  count: int
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
  print(f"❌ Invalid config file:")
  for error in e.errors():
    print(f"   - {error['loc']}: {error['msg']}")
  sys.exit(1)

# General fatal error
print(f"❌ <description of what failed>")
sys.exit(1)
```

Never swallow exceptions silently.

---

## Testing

Tests live in `program/test_suits/`. File names must be prefixed with `test_`.
Shared fixtures and constants go in `global_test_config.py`.

```python
# program/test_suits/test_processor.py
import pytest
from processor.processor import Processor

def test_config_not_found():
  with pytest.raises(SystemExit):
    Processor("nonexistent.yaml")
```

Run tests with:
```bash
pytest program/test_suits/
```

---

## Dependencies

Managed in `pyproject.toml` only — never `requirements.txt`.

- `pydantic==2.12.5` — config and result model validation
- `PyYAML==6.0.3` — YAML parsing
- `requests>=2.31.0` — HTTP
- `pytest==9.0.2` — testing
