---
name: mlflow-mlmodels-patterns
description: MLflow and ML Model patterns for Databricks including experiment creation, model training, batch inference, and Unity Catalog integration. Use when implementing ML pipelines, training models with Feature Store, or deploying batch inference jobs. Includes 16 non-negotiable rules covering experiment paths, dataset logging, UC model registration, NaN handling, label binarization, and signature-driven preprocessing.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: ml
---

# MLflow & ML Models Patterns

## Overview

Production-grade patterns for implementing ML pipelines on Databricks using MLflow, Unity Catalog, and Feature Store. Based on production experience with 25 models across 5 domains, achieving 96% inference success rate and 93% reduction in debugging time.

**Pattern Origin:** December 2025 (Updated: January 14, 2026 - v4.0)

---

## When to Use This Skill

Use this skill when:
- **Implementing ML pipelines** on Databricks with MLflow tracking
- **Training models** with Feature Store integration
- **Deploying batch inference** jobs
- **Registering models** to Unity Catalog
- **Troubleshooting** MLflow experiment, model registration, or inference errors
- **Setting up** Databricks Asset Bundle jobs for ML workflows

**Critical for:**
- Ensuring training and inference consistency
- Preventing common MLflow signature errors
- Handling data quality issues (NaN, label binarization, single-class data)
- Configuring serverless ML jobs correctly

---

## Critical Rules (Quick Reference)

| # | Rule | Pattern | Why It Fails Otherwise |
|---|------|---------|----------------------|
| 0 | **Pin Package Versions** | `mlflow==3.7.0` (exact) in training AND inference | Version mismatch warnings, deserialization failures |
| 1 | **Experiment Path** | `/Shared/{project}_ml_{model_name}` | `/Users/...` fails silently if subfolder doesn't exist |
| 2 | **Dataset Logging** | Inside `mlflow.start_run()` context | Won't associate with run, invisible in UI |
| 3 | **Exit Signal** | `dbutils.notebook.exit("SUCCESS")` | Job status unclear, may show SUCCESS on failure |
| 4 | **UC Model Logging** | Use `fe.log_model()` with `output_schema` | Unity Catalog rejects models without output spec |
| 5 | **Feature Store** | Use `FeatureEngineeringClient` for feature tables | Manual joins lose lineage, inference breaks |
| 6 | **NaN Handling** | Clean NaN/Inf at **feature table creation** | sklearn GradientBoosting fails; XGBoost handles NaN but sklearn doesn't |
| 7 | **Label Binarization** | Convert 0-1 rates to binary for classifiers | `XGBoostError: base_score must be in (0,1)` |
| 8 | **Single-Class Check** | Verify label distribution before training | Classifier can't train on all-same labels |
| 9 | **Exclude Labels** | Use `exclude_columns=[LABEL_COLUMN]` | Label included as feature causes inference failure |
| 10 | **Feature Registry** | Query feature table schemas dynamically | Hardcoded feature lists drift out of sync |
| 11 | **Standardized Utils** | Import from `training_base.py` | Custom implementations have inconsistent patterns |
| 12 | **Double Type Casting** | Cast ALL numeric features to DOUBLE in feature tables | MLflow signatures reject DecimalType |
| 13 | **Custom Inference** | Separate task for TF-IDF/NLP models | `fe.score_batch()` can't compute runtime features |
| 14 | **Bundle Path Setup** | Use `sys.path.insert(0, _bundle_root)` pattern | Module imports fail in serverless |
| 15 | **Helper Functions** | ALWAYS inline (don't import) | Asset Bundle notebooks can't import local modules |

---

## Core Patterns (Quick Examples)

### Experiment Setup

```python
# ✅ CORRECT: Always use /Shared/ path
experiment_name = f"/Shared/wanderbricks_ml_{model_name}"
mlflow.set_experiment(experiment_name)
```

**See:** [Experiment Patterns](references/experiment-patterns.md) for full details

### Model Registration with Feature Store

```python
from databricks.feature_engineering import FeatureEngineeringClient
from mlflow.types import ColSpec, DataType, Schema

fe = FeatureEngineeringClient()
mlflow.set_registry_uri("databricks-uc")

# Regression: output_schema = Schema([ColSpec(DataType.double)])
# Classification: output_schema = Schema([ColSpec(DataType.long)])

fe.log_model(
    model=model,
    artifact_path="model",
    flavor=mlflow.sklearn,  # REQUIRED
    training_set=training_set,
    registered_model_name=f"{catalog}.{schema}.{model_name}",
    infer_input_example=True,
    output_schema=output_schema  # REQUIRED for UC
)
```

**See:** [Model Registry](references/model-registry.md) for full patterns by model type

### Feature Table Creation with NaN Cleaning

```python
# ✅ CORRECT: Clean NaN/Inf at source for sklearn compatibility
from pyspark.sql.functions import F, isnan
from pyspark.sql.types import DoubleType

def clean_numeric(col_name):
    return F.when(
        F.col(col_name).isNull() | isnan(F.col(col_name)) |
        (F.col(col_name) == float('inf')) | (F.col(col_name) == float('-inf')),
        F.lit(0.0)
    ).otherwise(F.col(col_name))

# Apply to ALL DoubleType columns
for field in df.schema.fields:
    if isinstance(field.dataType, DoubleType):
        df = df.withColumn(field.name, clean_numeric(field.name))
```

**See:** [Data Quality Patterns](references/data-quality-patterns.md) for full patterns

### Asset Bundle Job Configuration

```yaml
resources:
  jobs:
    ml_training_job:
      environments:
        - environment_key: default
          spec:
            environment_version: "4"
            dependencies:
              - "mlflow==3.7.0"  # Pin exact version
              - "xgboost==2.0.3"
      tasks:
        - task_key: train_model
          notebook_task:
            notebook_path: ../../src/ml/models/train.py
            base_parameters:  # NOT parameters with --flags!
              catalog: ${var.catalog}
              model_name: my_model
      # ❌ DO NOT define experiments in Asset Bundle
```

**See:** [DAB Integration](references/dab-integration.md) for full patterns

---

## Reference Files

Detailed documentation is organized in the `references/` directory:

### **[Experiment Patterns](references/experiment-patterns.md)**
Complete experiment setup, tracking, metric logging, dataset logging, hyperparameter tuning. Covers `/Shared/` vs `/Users/` paths, run context requirements, helper function inlining, exit signals, and common errors.

### **[Model Registry](references/model-registry.md)**
Model registration, versioning, aliases, deployment patterns, serving endpoints. Covers Unity Catalog integration with `fe.log_model()`, output schema patterns by model type (regression, classification, anomaly detection), signature-driven preprocessing, and model loading from UC.

### **[DAB Integration](references/dab-integration.md)**
Asset Bundle integration, notebook patterns, inline helpers, parameter passing. Covers training and inference job configuration, package version pinning, `base_parameters` vs argparse, serverless environment setup, and common deployment errors.

### **[Feature Store Patterns](references/feature-store-patterns.md)**
Feature table creation, feature lookup configuration, column conflict resolution, Feature Registry pattern for dynamic schema querying. Covers training set creation, feature lookups, and inference patterns.

### **[Data Quality Patterns](references/data-quality-patterns.md)**
NaN/Inf handling at feature table source, label binarization for XGBoost classifiers, single-class data detection, feature column exclusion. Covers sklearn vs XGBoost compatibility, preprocessing requirements, and training/inference checklists.

### **[Troubleshooting](references/troubleshooting.md)**
Comprehensive error reference table, schema verification patterns, SCD2 vs regular dimension table handling, pre-development checklist. Covers common MLflow errors, signature issues, and debugging workflows.

---

## Scripts

### **[setup_experiment.py](scripts/setup_experiment.py)**

Utility functions for MLflow experiment setup. **CRITICAL:** These functions should be INLINED in each training notebook, not imported.

**Functions:**
- `setup_mlflow_experiment(model_name)` - Set up experiment with `/Shared/` path
- `log_training_dataset(spark, catalog, schema, table_name)` - Log dataset inside run context
- `get_run_name(model_name, algorithm, version)` - Generate descriptive run names
- `get_standard_tags(...)` - Get standard MLflow tags
- `get_parameters()` - Get job parameters from dbutils widgets

**Usage:**
```python
# Copy these functions into your notebook (don't import)
# See scripts/setup_experiment.py for full implementation
```

---

## Assets

### **[ml-job-config.yaml](assets/templates/ml-job-config.yaml)**

Template for Databricks Asset Bundle ML job configuration. Includes training job template with pinned package versions, batch inference job template, environment configuration, schedule configuration, and tag patterns.

**Usage:**
```yaml
# Copy and customize for your model
# Replace {model_name}, {input_table}, {output_table} placeholders
```

---

## Quick Validation Checklists

### Pre-Development
- [ ] Verify ALL column names against Gold layer YAML schemas
- [ ] Check if dimension tables are SCD2 (has `is_current`?)
- [ ] Confirm data types (DECIMAL, STRING, BOOLEAN, etc.)
- [ ] Identify categorical columns needing encoding
- [ ] Review Feature Store tables if using feature lookups

### MLflow Setup
- [ ] Use `/Shared/wanderbricks_ml_{model_name}` experiment path
- [ ] Do NOT define experiments in Asset Bundle
- [ ] Inline ALL helper functions (no module imports)
- [ ] Set `mlflow.set_registry_uri("databricks-uc")` at module level

### Training Pipeline
- [ ] Log dataset INSIDE `mlflow.start_run()` context
- [ ] Use `fe.log_model()` with `flavor=mlflow.sklearn` and `output_schema`
- [ ] Register model with 3-level name: `catalog.schema.model_name`
- [ ] Add `dbutils.notebook.exit("SUCCESS")` at end
- [ ] **Label Binarization**: Binarize 0-1 rates for XGBClassifier
- [ ] **Single-Class Check**: Verify label has multiple classes
- [ ] **Exclude Labels**: Use `exclude_columns=[LABEL_COLUMN]`

### Feature Table Creation
- [ ] Cast ALL numeric columns to DOUBLE
- [ ] Clean NaN/Inf at source (sklearn compatibility)
- [ ] Filter NULL primary key rows before writing

### Batch Inference
- [ ] Load model signature from registered model
- [ ] Replicate EXACT preprocessing from training
- [ ] Verify feature table has no NaN before inference
- [ ] Test with small batch before full inference

### Job Configuration
- [ ] Use `notebook_task` with `base_parameters` (not argparse)
- [ ] Pin exact package versions (match training and inference)
- [ ] DO NOT define experiments in Asset Bundle

**See:** [Troubleshooting](references/troubleshooting.md) for detailed checklists

---

## Version History

### v4.0 (January 14, 2026)
- Restructured to comply with AgentSkills.io specification
- Split into reference files for better organization
- Extracted scripts and templates

### v3.0 (January 4, 2026)
- NaN handling at feature table source
- Label binarization patterns
- Single-class data detection
- Feature column exclusion

### v2.0 (January 2026)
- `fe.log_model()` and `output_schema` patterns
- Model type to DataType mapping

### v1.0 (December 2025)
- Initial patterns from 5 model implementation

---

## References

### Official Documentation
- [FeatureEngineeringClient.log_model API](https://api-docs.databricks.com/python/feature-engineering/latest/feature_engineering.client.html)
- [MLflow Experiments - Databricks](https://learn.microsoft.com/en-us/azure/databricks/mlflow/experiments)
- [MLflow 3.1 LoggedModel](https://docs.databricks.com/aws/en/mlflow/logged-model)
- [Unity Catalog Model Registry](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/manage-model-lifecycle/)
- [Databricks Feature Store](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/feature-store/)

### Related Skills
- `databricks-python-imports` - sys.path setup for Asset Bundles
- `databricks-asset-bundles` - Infrastructure-as-code patterns
