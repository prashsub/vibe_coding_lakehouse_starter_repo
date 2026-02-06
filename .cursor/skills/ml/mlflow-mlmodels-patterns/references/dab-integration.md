# Databricks Asset Bundle Integration Patterns

## Training Job Pattern

```yaml
# resources/ml/ml_training_orchestrator_job.yml
resources:
  jobs:
    ml_training_orchestrator_job:
      name: "[${bundle.target}] ML Training Orchestrator"
      description: "Trains all ML models with MLflow 3.1+ LoggedModel tracking"
      
      # Shared environment for all tasks
      environments:
        - environment_key: default
          spec:
            environment_version: "4"
            dependencies:
              - "mlflow>=3.1"
              - "databricks-feature-engineering>=0.6.0"
              - "xgboost==2.0.3"
              - "scikit-learn==1.3.2"
              - "pandas==2.1.4"
              - "numpy==1.26.2"
      
      # Tasks run in PARALLEL (no depends_on)
      tasks:
        - task_key: train_demand_predictor
          environment_key: default
          notebook_task:
            notebook_path: ../../src/wanderbricks_ml/models/demand_predictor/train.py
            base_parameters:  # NOT parameters with --flags!
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
              feature_schema: ${var.ml_schema}
              model_name: demand_predictor
          timeout_seconds: 3600
        
        - task_key: train_conversion_predictor
          environment_key: default
          notebook_task:
            notebook_path: ../../src/wanderbricks_ml/models/conversion_predictor/train.py
            base_parameters:
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
              feature_schema: ${var.ml_schema}
              model_name: conversion_predictor
          timeout_seconds: 3600
      
      # Schedule: Weekly retraining
      schedule:
        quartz_cron_expression: "0 0 2 ? * SUN"
        timezone_id: "America/Los_Angeles"
        pause_status: PAUSED  # Enable in production
      
      timeout_seconds: 14400  # 4 hours total
      
      # ❌ DO NOT define experiments in Asset Bundle - creates duplicates!
      # experiments:
      #   my_experiment:
      #     name: /Shared/my_experiment  # Don't do this!
      
      tags:
        environment: ${bundle.target}
        project: wanderbricks
        layer: ml
        job_type: training
```

---

## Batch Inference Job Pattern

```yaml
resources:
  jobs:
    ml_batch_inference_job:
      name: "[${bundle.target}] ML Batch Inference"
      
      environments:
        - environment_key: default
          spec:
            environment_version: "4"
            dependencies:
              - "mlflow>=3.1"
              - "databricks-feature-engineering>=0.6.0"
              - "xgboost==2.0.3"
              - "pandas==2.1.4"
      
      tasks:
        - task_key: score_demand_predictor
          environment_key: default
          notebook_task:
            notebook_path: ../../src/wanderbricks_ml/inference/batch_inference_fixed.py
            base_parameters:
              catalog: ${var.catalog}
              model_name: demand_predictor
              input_table: ${var.catalog}.${var.gold_schema}.fact_booking_daily
              output_table: ${var.catalog}.${var.ml_schema}.demand_predictions
              model_version: latest
              feature_schema: ${var.ml_schema}
```

---

## Critical Asset Bundle Rules

### 1. Use `notebook_task` with `base_parameters` (NOT argparse)

```yaml
# ✅ CORRECT: Use base_parameters dict
notebook_task:
  notebook_path: ../../src/ml/models/train.py
  base_parameters:
    catalog: ${var.catalog}
    model_name: my_model

# ❌ WRONG: CLI-style parameters don't work
notebook_task:
  notebook_path: ../../src/ml/models/train.py
  parameters:
    --catalog: ${var.catalog}  # This won't work!
```

### 2. Use `dbutils.widgets.get()` in Notebooks (NOT argparse)

```python
# ✅ CORRECT: Use widgets in notebook
catalog = dbutils.widgets.get("catalog")
model_name = dbutils.widgets.get("model_name")

# ❌ WRONG: argparse doesn't work in Databricks notebooks
import argparse
parser = argparse.ArgumentParser()
args = parser.parse_args()  # Will fail!
```

### 3. DO NOT Define Experiments in Asset Bundle

```yaml
# ❌ WRONG: Creates duplicates with [dev username] prefix
experiments:
  my_experiment:
    name: /Shared/my_experiment

# ✅ CORRECT: Create experiments in notebook code
# Use setup_mlflow_experiment() helper function
```

### 4. Pin Package Versions Consistently

```yaml
# ✅ CORRECT: Pin exact versions in both training and inference
environments:
  - environment_key: default
    spec:
      environment_version: "4"
      dependencies:
        - "mlflow==3.7.0"        # Pin exact version
        - "scikit-learn==1.3.2"  # Pin exact version
        - "xgboost==2.0.3"      # Pin exact version

# ❌ WRONG: Loose version constraints cause mismatches
dependencies:
  - "mlflow>=3.0.0"  # Training may get 3.7.0, inference may get 3.8.1
```

---

## Job Configuration Checklist

- [ ] Use `notebook_task` with `base_parameters` (not argparse)
- [ ] Use `dbutils.widgets.get()` for parameters (not argparse)
- [ ] Include all required dependencies in environment
- [ ] Set appropriate timeout
- [ ] DO NOT define experiments in Asset Bundle
- [ ] Pin exact package versions (match training and inference)
- [ ] Use relative paths for notebook_path (from bundle root)

---

## Common Asset Bundle Errors

| Error | Root Cause | Solution |
|-------|------------|----------|
| `ModuleNotFoundError: No module named 'src'` | Serverless path resolution | Add `sys.path` setup block to notebook |
| `ModuleNotFoundError` for helpers | Import from local module | Inline all helper functions in each script |
| Duplicate experiments with `[dev username]` prefix | Asset Bundle experiment definitions | Remove experiments from Asset Bundle YAML |
| Job SUCCESS but actually failed | No exit signal | Add `dbutils.notebook.exit("SUCCESS")` |
| Job timeout | Long-running training | Increase `timeout_seconds` in job YAML |
| Parameter not found | Using argparse instead of widgets | Use `dbutils.widgets.get()` |

---

## Bundle Path Setup Pattern

```python
# Add this at the top of each notebook for serverless compatibility
import sys
from pathlib import Path

# Get bundle root (adjust path based on your structure)
_bundle_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_bundle_root))

# Now imports work (but still prefer inline helpers for critical functions)
```

**Note:** Even with path setup, prefer inline helpers for critical functions like `setup_mlflow_experiment()` to avoid import issues.
