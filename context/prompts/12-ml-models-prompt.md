# ML Models Implementation Prompt

## 🚀 Quick Start (4-6 hours)

**Goal:** Build production-ready ML pipelines with MLflow 3.1+, Unity Catalog Model Registry, and Databricks Feature Store

**What You'll Create:**
1. `feature_store/setup_feature_tables.py` - Feature tables for ML models
2. `models/{model_name}/train.py` - Training pipelines (one per model)
3. `inference/batch_inference.py` - Batch scoring pipeline
4. Asset Bundle jobs for orchestration

**Fast Track:**
```bash
# 1. Setup Feature Store
databricks bundle run ml_feature_store_setup_job -t dev

# 2. Train all models (parallel)
databricks bundle run ml_training_orchestrator_job -t dev

# 3. Run batch inference
databricks bundle run ml_batch_inference_job -t dev
```

**⚠️ 5 Non-Negotiable Rules:**

| Rule | Pattern | Why It Fails Otherwise |
|------|---------|------------------------|
| 1. Experiment Path | `/Shared/{project}_ml_{model_name}` | `/Users/...` fails silently if subfolder doesn't exist |
| 2. Dataset Logging | Inside `mlflow.start_run()` context | Won't associate with run, invisible in UI |
| 3. Helper Functions | ALWAYS inline (no imports) | `ModuleNotFoundError` in serverless |
| 4. Exit Signal | `dbutils.notebook.exit("SUCCESS")` | Job status unclear, may show SUCCESS on failure |
| 5. UC Signature | BOTH input AND output | Unity Catalog rejects models without output spec |

**Output:** Trained models in Unity Catalog, prediction tables, feature tables

📖 **Full guide below** for detailed implementation →

---

## Quick Reference

**Use this prompt to create ML pipelines with feature engineering, model training, and batch inference.**

**Prerequisites:** Gold layer tables must exist (data source for features and training).

**Reference Implementation:** [Wanderbricks ML](https://github.com/databricks/wanderbricks/src/wanderbricks_ml)

---

## 📋 Your Requirements (Fill These In First)

### Project Context
- **Project Name:** _________________ (e.g., customer_analytics)
- **Gold Schema:** _________________ (e.g., my_project_gold)
- **ML Schema:** _________________ (e.g., my_project_ml)
- **Catalog:** _________________ (e.g., my_catalog)

### Model Inventory

| Model Name | Type | Algorithm | Target Variable | Use Case |
|------------|------|-----------|-----------------|----------|
| ___________ | Regression/Classification | XGBoost/Prophet/etc | ___________ | ___________ |
| ___________ | ___________ | ___________ | ___________ | ___________ |
| ___________ | ___________ | ___________ | ___________ | ___________ |

### Feature Tables

| Feature Table | Entity Key | Features | Refresh |
|---------------|------------|----------|---------|
| ___________ | ___________ | ___________ | Daily/Hourly |
| ___________ | ___________ | ___________ | ___________ |

### Performance Targets

| Model | Metric | Target |
|-------|--------|--------|
| ___________ | MAPE/RMSE/AUC-ROC | <___% |
| ___________ | ___________ | ___________ |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          Gold Layer                              │
│   (fact_tables, dim_tables - source for feature engineering)    │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Feature Store (Unity Catalog)                  │
│  ┌───────────────────┐ ┌──────────────────┐ ┌─────────────────┐ │
│  │ entity1_features  │ │  entity2_features │ │ entity3_        │ │
│  │ • Attributes      │ │  • Demographics   │ │   features      │ │
│  │ • Historical      │ │  • Behavior       │ │ • Engagement    │ │
│  │ • Aggregations    │ │  • Transaction    │ │ • Rolling       │ │
│  └───────────────────┘ └──────────────────┘ └─────────────────┘ │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Training Pipelines                            │
│  ┌─────────────┐ ┌────────────┐ ┌─────────────┐ ┌────────────┐  │
│  │   Model 1   │ │   Model 2   │ │   Model 3   │ │  Model N   │  │
│  └─────────────┘ └────────────┘ └─────────────┘ └────────────┘  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│             Unity Catalog Model Registry (MLflow 3.1+)           │
│         catalog.{ml_schema}.{model_name}                         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Inference Layer                             │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐ │
│  │  Batch Inference         │  │  Model Serving Endpoints     │ │
│  │  (Daily scheduled jobs)  │  │  (Real-time REST APIs)       │ │
│  └──────────────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
src/{project}_ml/
├── feature_store/
│   └── setup_feature_tables.py     # Feature table creation
├── models/
│   ├── {model_1}/
│   │   └── train.py                # Training pipeline
│   ├── {model_2}/
│   │   └── train.py
│   └── {model_n}/
│       └── train.py
├── inference/
│   └── batch_inference.py          # Batch scoring pipeline
└── README.md

resources/ml/
├── ml_feature_store_setup_job.yml  # Feature Store setup job
├── ml_training_orchestrator_job.yml # Training orchestrator
└── ml_batch_inference_job.yml      # Batch inference job
```

---

## Step 1: Feature Store Setup

### Feature Engineering Pattern

```python
# Databricks notebook source
"""
{Project} Feature Store Setup

Creates feature tables in Unity Catalog for ML model training.
Uses Databricks Feature Engineering Client.

SCHEMA-GROUNDED: All column references verified against Gold layer YAML schemas.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from databricks.feature_engineering import FeatureEngineeringClient
from datetime import datetime, timedelta


def get_parameters():
    """Get job parameters from dbutils widgets (NEVER use argparse)."""
    catalog = dbutils.widgets.get("catalog")
    gold_schema = dbutils.widgets.get("gold_schema")
    feature_schema = dbutils.widgets.get("feature_schema")
    
    print(f"Catalog: {catalog}")
    print(f"Gold Schema: {gold_schema}")
    print(f"Feature Schema: {feature_schema}")
    
    return catalog, gold_schema, feature_schema


def create_catalog_and_schema(spark: SparkSession, catalog: str, feature_schema: str):
    """Ensures the Unity Catalog schema exists for feature tables and models."""
    print(f"Ensuring catalog '{catalog}' and schema '{feature_schema}' exist...")
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{feature_schema}")
    
    # Enable predictive optimization at schema level
    try:
        spark.sql(f"ALTER SCHEMA {catalog}.{feature_schema} ENABLE PREDICTIVE OPTIMIZATION")
        print(f"✓ Enabled predictive optimization for {catalog}.{feature_schema}")
    except Exception as e:
        print(f"⚠ Could not enable predictive optimization: {e}")
    
    print(f"✓ Schema {catalog}.{feature_schema} ready for feature tables")


def create_{entity}_features(
    spark: SparkSession,
    catalog: str,
    gold_schema: str,
    feature_schema: str,
    fe: FeatureEngineeringClient
):
    """
    Create {entity}-level features for ML models.
    
    Schema grounded in: gold_layer_design/yaml/{domain}/dim_{entity}.yaml
    
    Features include:
    - Attributes: {list attribute features}
    - Historical: {list historical aggregations}
    - Engagement: {list engagement metrics}
    """
    print("\n" + "="*80)
    print(f"Creating {entity}_features table")
    print("="*80)
    
    # Load Gold layer tables
    dim_{entity} = spark.table(f"{catalog}.{gold_schema}.dim_{entity}")
    fact_table = spark.table(f"{catalog}.{gold_schema}.fact_{entity}_activity")
    
    # Calculate historical metrics (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
    
    # Aggregate metrics from fact table
    historical_metrics = (
        fact_table
        .filter(col("activity_date") >= lit(thirty_days_ago))
        .groupBy("{entity}_id")
        .agg(
            count("*").alias("activity_count_30d"),
            sum("amount").alias("total_amount_30d"),
            avg("amount").alias("avg_amount_30d")
        )
    )
    
    # Combine all features
    # ⚠️ GROUNDED: Only columns from Gold layer YAML schema
    {entity}_features = (
        dim_{entity}
        .filter(col("is_current") == True)  # If SCD2 table
        .select(
            "{entity}_id",
            # Select columns that exist in Gold layer
        )
        .join(historical_metrics, "{entity}_id", "left")
        .fillna(0, subset=["activity_count_30d", "total_amount_30d", "avg_amount_30d"])
        .withColumn("feature_timestamp", current_timestamp())
    )
    
    # Create feature table
    feature_table_name = f"{catalog}.{feature_schema}.{entity}_features"
    
    fe.create_table(
        name=feature_table_name,
        primary_keys=["{entity}_id"],  # Single or composite key
        df={entity}_features,
        description="{Entity}-level features for ML models"
    )
    
    record_count = {entity}_features.count()
    print(f"✓ Created {entity}_features with {record_count} records")


def main():
    """Main entry point for feature store setup."""
    
    catalog, gold_schema, feature_schema = get_parameters()
    
    spark = SparkSession.builder.appName("Feature Store Setup").getOrCreate()
    fe = FeatureEngineeringClient()
    
    try:
        create_catalog_and_schema(spark, catalog, feature_schema)
        
        # Create feature tables (schema-grounded)
        create_{entity1}_features(spark, catalog, gold_schema, feature_schema, fe)
        create_{entity2}_features(spark, catalog, gold_schema, feature_schema, fe)
        # ... additional feature tables
        
        print("\n" + "="*80)
        print("✓ Feature Store setup completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during feature store setup: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
```

### Feature Table Creation Rules

```python
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

# ✅ CORRECT: Primary keys without timestamp_keys
fe.create_table(
    name=f"{catalog}.{feature_schema}.{entity}_features",
    primary_keys=["{entity}_id"],  # Single key
    df=features_df,
    description="Description for discoverability"
)

# ✅ CORRECT: Composite primary key for time-series features
fe.create_table(
    name=f"{catalog}.{feature_schema}.{entity}_daily_features",
    primary_keys=["{entity}_id", "feature_date"],  # Composite key
    df=daily_features_df,
    description="Daily features with composite key"
)

# ❌ WRONG: timestamp_keys was removed in newer versions
fe.create_table(
    name=feature_table_name,
    primary_keys=["{entity}_id"],
    timestamp_keys=["feature_date"],  # ❌ Not supported anymore
    df=features_df
)
```

---

## Step 2: Model Training Pipeline

### Standard Training Template

**⚠️ CRITICAL: All helper functions MUST be inlined. Module imports fail in serverless.**

```python
# Databricks notebook source
"""
{Model Name} Training Pipeline

Trains a {model_type} model for {use_case}.
Uses {algorithm} with MLflow 3.1+ best practices.

Reference: https://learn.microsoft.com/en-us/azure/databricks/mlflow/mlflow-3-install
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup
import mlflow
from mlflow.models import infer_signature
import pandas as pd
import numpy as np
from xgboost import XGBRegressor  # or XGBClassifier
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime

# =============================================================================
# MLflow Configuration (at module level)
# =============================================================================
mlflow.set_registry_uri("databricks-uc")


# =============================================================================
# INLINE HELPER FUNCTIONS (NEVER import - copy to each script)
# =============================================================================
def setup_mlflow_experiment(model_name: str) -> str:
    """
    Set up MLflow experiment using /Shared/ path.
    
    ⚠️ CRITICAL: Do NOT move this to a shared module!
    Asset Bundle notebooks can't reliably import local modules.
    
    ⚠️ NEVER use /Users/{user}/... paths - they fail silently if subfolder doesn't exist.
    """
    print("\n" + "="*80)
    print(f"Setting up MLflow Experiment: {model_name}")
    print("="*80)
    
    # ✅ CORRECT: /Shared/ path always works
    experiment_name = f"/Shared/{project}_ml_{model_name}"
    
    try:
        experiment = mlflow.set_experiment(experiment_name)
        print(f"✓ Experiment set: {experiment_name}")
        print(f"  Experiment ID: {experiment.experiment_id}")
        return experiment_name
    except Exception as e:
        print(f"❌ Experiment setup failed: {e}")
        return None


def log_training_dataset(spark, catalog: str, schema: str, table_name: str) -> bool:
    """
    Log training dataset for MLflow lineage.
    
    ⚠️ CRITICAL: MUST be called inside mlflow.start_run() context!
    """
    full_table_name = f"{catalog}.{schema}.{table_name}"
    try:
        print(f"  Logging dataset: {full_table_name}")
        training_df = spark.table(full_table_name)
        dataset = mlflow.data.from_spark(
            df=training_df, 
            table_name=full_table_name,
            version="latest"
        )
        mlflow.log_input(dataset, context="training")
        print(f"✓ Dataset logged: {full_table_name}")
        return True
    except Exception as e:
        print(f"⚠️  Dataset logging failed: {e}")
        return False


def get_run_name(model_name: str, algorithm: str, version: str = "v1") -> str:
    """Generate descriptive run name for MLflow tracking."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{model_name}_{algorithm}_{version}_{timestamp}"


def get_standard_tags(model_name: str, domain: str, model_type: str, 
                      algorithm: str, use_case: str, training_table: str,
                      feature_store_enabled: bool = False) -> dict:
    """Get standard MLflow run tags for consistent organization."""
    return {
        "project": "{project}",
        "domain": domain,
        "model_name": model_name,
        "model_type": model_type,  # "regression" or "classification"
        "algorithm": algorithm,     # "xgboost", "gradient_boosting", "prophet"
        "layer": "ml",
        "team": "data_science",
        "use_case": use_case,
        "feature_store_enabled": str(feature_store_enabled).lower(),
        "training_data": training_table
    }


def get_parameters():
    """Get job parameters from dbutils widgets (NEVER use argparse)."""
    catalog = dbutils.widgets.get("catalog")
    gold_schema = dbutils.widgets.get("gold_schema")
    feature_schema = dbutils.widgets.get("feature_schema")
    model_name = dbutils.widgets.get("model_name")
    
    print(f"Catalog: {catalog}")
    print(f"Gold Schema: {gold_schema}")
    print(f"Feature Schema: {feature_schema}")
    print(f"Model Name: {model_name}")
    
    return catalog, gold_schema, feature_schema, model_name


# =============================================================================
# DATA PREPARATION
# =============================================================================
def prepare_training_data(
    spark: SparkSession,
    catalog: str,
    gold_schema: str,
    feature_schema: str
):
    """
    Prepare training data with feature engineering.
    
    SCHEMA-GROUNDED: All columns verified against Gold layer YAML.
    
    ⚠️ SCD2 Tables (have is_current): dim_{entity1}, dim_{entity2}
       ALWAYS filter: .filter(col("is_current") == True)
       
    ⚠️ Regular Tables (no is_current): dim_date, dim_location
       Do NOT filter.
    """
    print("\n" + "="*80)
    print("Preparing training data")
    print("="*80)
    
    # Load Gold layer tables
    fact_table = spark.table(f"{catalog}.{gold_schema}.fact_{name}")
    
    # ✅ SCD2 dimension - filter for current records
    dim_{entity} = (
        spark.table(f"{catalog}.{gold_schema}.dim_{entity}")
        .filter(col("is_current") == True)
    )
    
    # Create training labels
    training_labels = (
        fact_table
        .select(
            "{entity}_id",
            "{date_column}",
            "{target_column}",  # Label
            # Additional columns for feature engineering
        )
        # Add temporal features
        .withColumn("month", month("{date_column}"))
        .withColumn("quarter", quarter("{date_column}"))
        .withColumn("day_of_week", dayofweek("{date_column}"))
        .withColumn("is_weekend", dayofweek("{date_column}").isin([1, 7]).cast("double"))
    )
    
    # Join with feature tables
    feature_table = spark.table(f"{catalog}.{feature_schema}.{entity}_features")
    
    training_df = (
        training_labels
        .join(feature_table.drop("feature_timestamp"), "{entity}_id", "left")
        .fillna(0)  # Fill nulls for numeric columns
    )
    
    # Convert to Pandas for sklearn/xgboost
    pdf = training_df.toPandas()
    
    print(f"✓ Training data prepared: {pdf.shape}")
    
    return pdf, training_labels


def preprocess_features(pdf: pd.DataFrame, target_col: str):
    """
    Preprocess features for model training.
    
    ⚠️ CRITICAL: Document ALL transformations - batch inference MUST replicate exactly.
    
    Transformations Applied:
    1. Convert Spark DECIMAL to float (XGBoost can't handle Decimal)
    2. Encode categorical columns
    3. Handle datetime columns
    4. Fill NaN values
    """
    print("\n" + "="*80)
    print("Preprocessing features")
    print("="*80)
    
    # 1. Convert Spark DECIMAL to float (REQUIRED - XGBoost can't handle Decimal)
    decimal_cols = ['revenue', 'price', 'amount', 'value']
    for col_name in decimal_cols:
        if col_name in pdf.columns:
            pdf[col_name] = pd.to_numeric(pdf[col_name], errors='coerce')
    
    # 2. Encode categorical columns (must match inference)
    categorical_cols = ['{entity}_type', 'category', 'region', 'country']
    for col_name in categorical_cols:
        if col_name in pdf.columns and pdf[col_name].dtype == 'object':
            pdf[col_name] = pd.Categorical(pdf[col_name]).codes
    
    # 3. Handle datetime columns
    date_cols = ['{date_column}']
    for col_name in date_cols:
        if col_name in pdf.columns:
            pdf[col_name] = pd.to_datetime(pdf[col_name])
    
    # 4. Fill NaN values
    pdf = pdf.fillna(0)
    
    # Separate features and label
    exclude_cols = [
        '{entity}_id', '{date_column}', target_col,
        'feature_timestamp'
    ]
    feature_cols = [c for c in pdf.columns if c not in exclude_cols]
    
    X = pdf[feature_cols]
    y = pdf[target_col]
    
    print(f"Feature matrix: {X.shape}")
    print(f"Features: {list(X.columns)[:10]}... ({len(X.columns)} total)")
    
    return X, y, feature_cols


# =============================================================================
# MODEL TRAINING
# =============================================================================
def train_model(X_train, y_train, X_val, y_val):
    """
    Train {algorithm} model.
    
    Hyperparameters optimized for {use_case}.
    """
    print("\n" + "="*80)
    print("Training model")
    print("="*80)
    
    model = XGBRegressor(  # or XGBClassifier for classification
        max_depth=6,
        learning_rate=0.1,
        n_estimators=100,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='reg:squarederror',  # or 'binary:logistic'
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    print(f"✓ Model trained with {model.n_estimators} trees")
    
    return model


def evaluate_model(model, X_train, y_train, X_val, y_val):
    """
    Evaluate model and return metrics.
    """
    print("\n" + "="*80)
    print("Evaluating model")
    print("="*80)
    
    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)
    
    # Regression metrics
    metrics = {
        "train_rmse": np.sqrt(mean_squared_error(y_train, train_pred)),
        "val_rmse": np.sqrt(mean_squared_error(y_val, val_pred)),
        "train_mae": mean_absolute_error(y_train, train_pred),
        "val_mae": mean_absolute_error(y_val, val_pred),
        "train_r2": r2_score(y_train, train_pred),
        "val_r2": r2_score(y_val, val_pred),
        # MAPE
        "train_mape": np.mean(np.abs((y_train - train_pred) / (y_train + 1))) * 100,
        "val_mape": np.mean(np.abs((y_val - val_pred) / (y_val + 1))) * 100
    }
    
    print("\nModel Performance:")
    print(f"  Validation MAPE: {metrics['val_mape']:.2f}%")
    print(f"  Validation RMSE: {metrics['val_rmse']:.4f}")
    print(f"  Validation R²: {metrics['val_r2']:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    return metrics, feature_importance


# =============================================================================
# MODEL LOGGING (with all required components for UC)
# =============================================================================
def log_model_with_mlflow(
    model,
    X_train: pd.DataFrame,
    feature_cols: list,
    metrics: dict,
    feature_importance: pd.DataFrame,
    model_name: str,
    catalog: str,
    feature_schema: str,
    gold_schema: str,
    experiment_name: str,
    spark
):
    """
    Log model to MLflow with best practices.
    
    ⚠️ CRITICAL: All logging MUST be inside mlflow.start_run() context!
    """
    print("\n" + "="*80)
    print("Logging model to MLflow")
    print("="*80)
    
    # 3-level name for Unity Catalog
    registered_model_name = f"{catalog}.{feature_schema}.{model_name}"
    print(f"Registered Model: {registered_model_name}")
    
    # Descriptive run name
    run_name = get_run_name(model_name, "xgboost", "v1")
    
    with mlflow.start_run(run_name=run_name) as run:
        
        # 1. Set tags (before other logging)
        tags = get_standard_tags(
            model_name=model_name,
            domain="{domain}",
            model_type="regression",
            algorithm="xgboost",
            use_case="{use_case}",
            training_table=f"{catalog}.{gold_schema}.fact_{name}",
            feature_store_enabled=False
        )
        mlflow.set_tags(tags)
        
        # 2. Log dataset (INSIDE run context!)
        log_training_dataset(spark, catalog, gold_schema, "fact_{name}")
        
        # 3. Log hyperparameters
        mlflow.log_params({
            "max_depth": model.max_depth,
            "learning_rate": model.learning_rate,
            "n_estimators": model.n_estimators,
            "subsample": model.subsample,
            "colsample_bytree": model.colsample_bytree,
            "num_features": len(feature_cols),
            "objective": "reg:squarederror"
        })
        
        # 4. Log metrics
        mlflow.log_metrics(metrics)
        
        # 5. Log feature importance artifact
        feature_importance_path = "feature_importance.csv"
        feature_importance.to_csv(feature_importance_path, index=False)
        mlflow.log_artifact(feature_importance_path)
        
        # 6. Create signature with BOTH input AND output (REQUIRED for UC)
        sample_input = X_train.head(5)
        sample_output = model.predict(sample_input)  # Include this!
        signature = infer_signature(sample_input, sample_output)
        
        # 7. Log and register model
        mlflow.xgboost.log_model(
            model,
            artifact_path="model",
            signature=signature,
            input_example=sample_input,
            registered_model_name=registered_model_name
        )
        
        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        
        print(f"\n✓ Model logged")
        print(f"  Run ID: {run_id}")
        print(f"  Model URI: {model_uri}")
        print(f"  Registered Model: {registered_model_name}")
        
        return {
            "run_id": run_id,
            "run_name": run_name,
            "model_uri": model_uri,
            "registered_model_name": registered_model_name,
            "experiment_name": experiment_name
        }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main():
    """Main training pipeline."""
    
    catalog, gold_schema, feature_schema, model_name = get_parameters()
    
    spark = SparkSession.builder.appName(f"{model_name} Training").getOrCreate()
    
    # Disable autolog to control what's logged
    mlflow.autolog(disable=True)
    
    # Setup experiment
    experiment_name = setup_mlflow_experiment(model_name)
    
    try:
        # Prepare data
        pdf, training_labels = prepare_training_data(
            spark, catalog, gold_schema, feature_schema
        )
        
        # Preprocess
        X, y, feature_cols = preprocess_features(pdf, "{target_column}")
        
        # Train/Val split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\nTrain set: {X_train.shape}")
        print(f"Validation set: {X_val.shape}")
        
        # Train model
        model = train_model(X_train, y_train, X_val, y_val)
        
        # Evaluate
        metrics, feature_importance = evaluate_model(
            model, X_train, y_train, X_val, y_val
        )
        
        # Log to MLflow
        run_info = log_model_with_mlflow(
            model=model,
            X_train=X_train,
            feature_cols=feature_cols,
            metrics=metrics,
            feature_importance=feature_importance,
            model_name=model_name,
            catalog=catalog,
            feature_schema=feature_schema,
            gold_schema=gold_schema,
            experiment_name=experiment_name,
            spark=spark
        )
        
        print("\n" + "="*80)
        print("✓ Training completed successfully!")
        print("="*80)
        
        # Check performance target
        if metrics['val_mape'] < {target_mape}:
            print(f"\n✅ Model meets MAPE target (<{target_mape}%)")
        else:
            print(f"\n⚠️ Model does not meet MAPE target")
        
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {str(e)}")
        print(traceback.format_exc())
        # ✅ REQUIRED: Signal failure with message
        dbutils.notebook.exit(f"FAILED: {str(e)}")
    
    # ✅ REQUIRED: Signal success to Databricks
    dbutils.notebook.exit("SUCCESS")


if __name__ == "__main__":
    main()
```

---

## Step 3: Batch Inference Pipeline

### Inference Script Template

```python
# Databricks notebook source
"""
Batch Inference Pipeline for ML Models

Performs batch scoring using registered models.
Supports automatic feature lookup and preprocessing.

⚠️ CRITICAL: Preprocessing MUST exactly match training preprocessing.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, lit, current_timestamp, current_date, when
import mlflow
import pandas as pd
from datetime import datetime
import builtins  # For built-in max function (avoid conflict with PySpark max)


def get_parameters():
    """Get job parameters from dbutils widgets."""
    catalog = dbutils.widgets.get("catalog")
    model_name = dbutils.widgets.get("model_name")
    input_table = dbutils.widgets.get("input_table")
    output_table = dbutils.widgets.get("output_table")
    model_version = dbutils.widgets.get("model_version")  # "latest" or specific version
    feature_schema = dbutils.widgets.get("feature_schema")
    
    print(f"Catalog: {catalog}")
    print(f"Model Name: {model_name}")
    print(f"Feature Schema: {feature_schema}")
    print(f"Input Table: {input_table}")
    print(f"Output Table: {output_table}")
    print(f"Model Version: {model_version}")
    
    return catalog, model_name, input_table, output_table, model_version, feature_schema


def load_model(catalog: str, feature_schema: str, model_name: str, model_version: str):
    """
    Load model from Unity Catalog Model Registry.
    """
    print("\n" + "="*80)
    print("Loading model")
    print("="*80)
    
    # Construct model URI with 3-level naming
    full_model_name = f"{catalog}.{feature_schema}.{model_name}"
    
    client = mlflow.tracking.MlflowClient()
    
    if model_version == "latest":
        model_versions = client.search_model_versions(f"name='{full_model_name}'")
        if model_versions:
            # Use builtins.max to avoid conflict with PySpark's max function
            latest_version = builtins.max(model_versions, key=lambda x: int(x.version))
            version_num = latest_version.version
            print(f"Found latest version: {version_num}")
            model_uri = f"models:/{full_model_name}/{version_num}"
        else:
            raise Exception(f"No model versions found for {full_model_name}")
    else:
        model_uri = f"models:/{full_model_name}/{model_version}"
    
    print(f"Full Model Name: {full_model_name}")
    print(f"Model URI: {model_uri}")
    
    return model_uri


def prepare_input_data(spark: SparkSession, input_table: str, model_name: str):
    """
    Prepare input data for batch scoring.
    """
    print("\n" + "="*80)
    print("Preparing input data for scoring")
    print("="*80)
    
    input_df = spark.table(input_table)
    
    # Model-specific preparation
    if "{model_1}" in model_name:
        scoring_df = (
            input_df
            .select("{entity}_id", "{date_column}")
            .distinct()
            # Add temporal features matching training
            .withColumn("month", F.month("{date_column}"))
            .withColumn("quarter", F.quarter("{date_column}"))
        )
    # ... additional model types
    else:
        raise ValueError(f"Unknown model type: {model_name}")
    
    record_count = scoring_df.count()
    print(f"Scoring data: {record_count} records")
    
    return scoring_df


def score_batch(
    spark: SparkSession,
    model_uri: str,
    scoring_df,
    model_name: str,
    catalog: str,
    feature_schema: str
):
    """
    Score batch data.
    
    ⚠️ CRITICAL: Preprocessing MUST exactly replicate training preprocessing.
    """
    print("\n" + "="*80)
    print("Scoring batch data")
    print("="*80)
    
    # Join with feature tables
    features_df = spark.table(f"{catalog}.{feature_schema}.{entity}_features")
    scoring_df = scoring_df.join(features_df, "{entity}_id", "inner")
    
    print(f"Joined scoring data: {scoring_df.count()} records")
    
    # Convert to Pandas
    pdf = scoring_df.toPandas()
    
    # ⚠️ CRITICAL: Replicate EXACT preprocessing from training
    
    # 1. Convert boolean columns to float (before feature selection)
    for col_name in pdf.columns:
        if pdf[col_name].dtype == 'bool':
            pdf[col_name] = pdf[col_name].astype(float)
    
    # 2. Get feature columns (exclude keys and timestamps)
    exclude_cols = ['{entity}_id', 'feature_date', '{date_column}', 'feature_timestamp']
    feature_cols = [c for c in pdf.columns if c not in exclude_cols]
    
    # 3. Encode categorical columns (same as training)
    categorical_cols = ['{entity}_type', 'category', 'region', 'country']
    for col_name in categorical_cols:
        if col_name in pdf.columns and pdf[col_name].dtype == 'object':
            pdf[col_name] = pd.Categorical(pdf[col_name]).codes
    
    # 4. Convert numeric types (handles Decimal, int, object)
    for col_name in feature_cols:
        if col_name in categorical_cols:
            continue
        try:
            pdf[col_name] = pd.to_numeric(pdf[col_name], errors='coerce')
        except (ValueError, TypeError):
            pass
    
    # Load model and predict
    model = mlflow.pyfunc.load_model(model_uri)
    X = pdf[feature_cols].fillna(0)
    pdf['prediction'] = model.predict(X)
    
    # Convert back to Spark
    predictions_df = spark.createDataFrame(pdf)
    
    # Add metadata
    predictions_df = (
        predictions_df
        .withColumn("model_name", lit(model_name))
        .withColumn("model_uri", lit(model_uri))
        .withColumn("scored_at", current_timestamp())
        .withColumn("scoring_date", current_date())
    )
    
    # Rename prediction column based on model type
    predictions_df = predictions_df.withColumnRenamed("prediction", "predicted_{target}")
    
    print(f"✓ Scored {predictions_df.count()} records")
    
    return predictions_df


def save_predictions(spark, predictions_df, output_table: str):
    """Save predictions to Delta table."""
    print("\n" + "="*80)
    print("Saving predictions")
    print("="*80)
    
    predictions_df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("mergeSchema", "true") \
        .saveAsTable(output_table)
    
    final_count = spark.table(output_table).count()
    print(f"✓ Saved {final_count} predictions to {output_table}")


def main():
    """Main batch inference pipeline."""
    
    catalog, model_name, input_table, output_table, model_version, feature_schema = get_parameters()
    
    spark = SparkSession.builder.appName("Batch Inference").getOrCreate()
    
    try:
        model_uri = load_model(catalog, feature_schema, model_name, model_version)
        scoring_df = prepare_input_data(spark, input_table, model_name)
        predictions_df = score_batch(spark, model_uri, scoring_df, model_name, catalog, feature_schema)
        save_predictions(spark, predictions_df, output_table)
        
        print("\n" + "="*80)
        print("✓ Batch inference completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during batch inference: {str(e)}")
        raise


if __name__ == "__main__":
    main()
```

---

## Step 4: Asset Bundle Jobs

### Training Orchestrator Job

```yaml
# resources/ml/ml_training_orchestrator_job.yml

resources:
  jobs:
    ml_training_orchestrator_job:
      name: "[${bundle.target}] ML Training Orchestrator"
      description: "Orchestrates training of all ML models"
      
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
      
      tasks:
        # Train models in PARALLEL (no dependencies between models)
        
        - task_key: train_{model_1}
          environment_key: default
          notebook_task:
            notebook_path: ../../src/{project}_ml/models/{model_1}/train.py
            base_parameters:
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
              feature_schema: ${var.ml_schema}
              model_name: {model_1}
          timeout_seconds: 3600
        
        - task_key: train_{model_2}
          environment_key: default
          notebook_task:
            notebook_path: ../../src/{project}_ml/models/{model_2}/train.py
            base_parameters:
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
              feature_schema: ${var.ml_schema}
              model_name: {model_2}
          timeout_seconds: 3600
        
        # Add more models...
      
      # Schedule: Weekly retraining on Sunday at 2 AM
      schedule:
        quartz_cron_expression: "0 0 2 ? * SUN"
        timezone_id: "America/Los_Angeles"
        pause_status: PAUSED  # Enable manually in production
      
      timeout_seconds: 14400  # 4 hours total
      
      email_notifications:
        on_failure:
          - data-engineering@company.com
      
      tags:
        environment: ${bundle.target}
        project: {project}
        layer: ml
        compute_type: serverless
        job_type: training
        orchestrator: "true"
```

### Batch Inference Job

```yaml
# resources/ml/ml_batch_inference_job.yml

resources:
  jobs:
    ml_batch_inference_job:
      name: "[${bundle.target}] ML Batch Inference"
      description: "Batch scoring for ML models"
      
      environments:
        - environment_key: default
          spec:
            environment_version: "4"
            dependencies:
              - "mlflow>=3.1"
              - "databricks-feature-engineering>=0.6.0"
              - "xgboost==2.0.3"
              - "scikit-learn==1.3.2"
      
      tasks:
        - task_key: score_{model_1}_predictions
          environment_key: default
          notebook_task:
            notebook_path: ../../src/{project}_ml/inference/batch_inference.py
            base_parameters:
              catalog: ${var.catalog}
              feature_schema: ${var.ml_schema}
              model_name: {model_1}
              input_table: ${var.catalog}.${var.gold_schema}.fact_{source}
              output_table: ${var.catalog}.${var.ml_schema}.{model_1}_predictions
              model_version: latest
          timeout_seconds: 1800
        
        - task_key: score_{model_2}_predictions
          depends_on:
            - task_key: score_{model_1}_predictions
          environment_key: default
          notebook_task:
            notebook_path: ../../src/{project}_ml/inference/batch_inference.py
            base_parameters:
              catalog: ${var.catalog}
              feature_schema: ${var.ml_schema}
              model_name: {model_2}
              input_table: ${var.catalog}.${var.gold_schema}.fact_{source}
              output_table: ${var.catalog}.${var.ml_schema}.{model_2}_predictions
              model_version: latest
          timeout_seconds: 1800
      
      # Schedule: Daily at 4 AM (after data refresh)
      schedule:
        quartz_cron_expression: "0 0 4 * * ?"
        timezone_id: "America/Los_Angeles"
        pause_status: PAUSED
      
      timeout_seconds: 7200
      
      email_notifications:
        on_failure:
          - data-engineering@company.com
      
      tags:
        environment: ${bundle.target}
        project: {project}
        layer: ml
        compute_type: serverless
        job_type: inference
```

### Feature Store Setup Job

```yaml
# resources/ml/ml_feature_store_setup_job.yml

resources:
  jobs:
    ml_feature_store_setup_job:
      name: "[${bundle.target}] ML Feature Store Setup"
      description: "Creates feature tables in Unity Catalog"
      
      environments:
        - environment_key: default
          spec:
            environment_version: "4"
            dependencies:
              - "databricks-feature-engineering>=0.6.0"
      
      tasks:
        - task_key: setup_feature_tables
          environment_key: default
          notebook_task:
            notebook_path: ../../src/{project}_ml/feature_store/setup_feature_tables.py
            base_parameters:
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
              feature_schema: ${var.ml_schema}
          timeout_seconds: 1800
      
      tags:
        environment: ${bundle.target}
        project: {project}
        layer: ml
        compute_type: serverless
        job_type: setup
```

---

## ⚠️ Critical Patterns & Common Mistakes

### 1. Experiment Path

```python
# ✅ CORRECT: /Shared/ path always works
experiment_name = f"/Shared/{project}_ml_{model_name}"

# ❌ WRONG: User path fails silently if subfolder doesn't exist
experiment_name = f"/Users/{user}/subfolder/{model_name}"

# ❌ WRONG: Asset Bundle experiments create duplicates with [dev] prefix
# Never define experiments in resources/ml/ml_experiments.yml
```

### 2. Dataset Logging

```python
# ✅ CORRECT: Inside mlflow.start_run()
with mlflow.start_run(run_name=run_name) as run:
    dataset = mlflow.data.from_spark(df, table_name=table_name)
    mlflow.log_input(dataset, context="training")  # ✅ Associates with run

# ❌ WRONG: Outside run context
dataset = mlflow.data.from_spark(df, table_name=table_name)
mlflow.log_input(dataset)  # ❌ Won't appear in UI!
with mlflow.start_run() as run:
    pass  # Dataset not associated
```

### 3. Helper Functions (Module Imports)

```python
# ✅ CORRECT: Inline helpers in each notebook
def setup_mlflow_experiment(model_name: str) -> str:
    # Implementation here
    pass

# ❌ WRONG: Import from shared module - ModuleNotFoundError in serverless
from utils.mlflow_setup import setup_mlflow_experiment
```

### 4. Notebook Exit Signal

```python
# ✅ CORRECT: Always signal exit
def main():
    try:
        # ... training code ...
    except Exception as e:
        dbutils.notebook.exit(f"FAILED: {str(e)}")
    
    dbutils.notebook.exit("SUCCESS")  # ✅ Required

# ❌ WRONG: No exit signal
def main():
    # ... training code ...
    print("Done!")  # ❌ Job status unclear
    
# ❌ WRONG: spark.stop() prevents exit signal
def main():
    try:
        pass
    finally:
        spark.stop()  # ❌ Prevents dbutils.notebook.exit()
```

### 5. Unity Catalog Model Signature

```python
# ✅ CORRECT: BOTH input AND output
sample_input = X_train.head(5)
sample_output = model.predict(sample_input)  # ✅ Include output!
signature = infer_signature(sample_input, sample_output)

# ❌ WRONG: Only input
signature = infer_signature(sample_input)  # ❌ Missing output
# Error: "Model signature must contain both input and output type specifications"
```

### 6. SCD2 Table Filtering

```python
# ✅ CORRECT: Filter SCD2 tables for current records
dim_entity = (
    spark.table(f"{catalog}.{schema}.dim_{entity}")
    .filter(col("is_current") == True)  # ✅ Required for SCD2
)

# ❌ WRONG: No filter on SCD2 table
dim_entity = spark.table(f"{catalog}.{schema}.dim_{entity}")  # Gets all versions!

# ❌ WRONG: Filter non-SCD2 table
dim_date = spark.table(f"{catalog}.{schema}.dim_date")
dim_date.filter(col("is_current"))  # ❌ Column doesn't exist!
```

### 7. Preprocessing Consistency (Training ↔ Inference)

```python
# Training preprocessing
pdf[col] = pd.to_numeric(pdf[col], errors='coerce')
pdf[cat_col] = pd.Categorical(pdf[cat_col]).codes
pdf = pdf.fillna(0)

# ⚠️ Inference MUST replicate EXACTLY:
# - Same column order
# - Same type conversions
# - Same categorical encoding
# - Same fillna strategy
```

---

## Validation Checklist

### Feature Store
- [ ] Schema exists in Unity Catalog
- [ ] Feature tables have descriptive names and descriptions
- [ ] Primary keys are correct (single or composite)
- [ ] All columns verified against Gold layer YAML

### Training Pipeline
- [ ] Experiment path uses `/Shared/` prefix
- [ ] All helper functions are inlined (not imported)
- [ ] Dataset logging is inside `mlflow.start_run()` context
- [ ] Model signature includes BOTH input and output
- [ ] `dbutils.notebook.exit()` called for success and failure
- [ ] SCD2 tables filtered with `is_current == True`
- [ ] Preprocessing documented for inference replication

### Batch Inference
- [ ] Preprocessing exactly matches training
- [ ] Boolean columns converted to float before scoring
- [ ] `builtins.max` used instead of PySpark `max`
- [ ] Output table has metadata columns (model_name, scored_at)

### Asset Bundle Jobs
- [ ] `environments` block defined at job level
- [ ] `environment_key: default` in every task
- [ ] `base_parameters` (not `parameters`) for notebook_task
- [ ] `${var.xxx}` format for variables
- [ ] Schedule set to `PAUSED` in dev

---

## Model Type Patterns

### Regression (XGBoost)

```python
from xgboost import XGBRegressor

model = XGBRegressor(
    max_depth=6,
    learning_rate=0.1,
    n_estimators=100,
    objective='reg:squarederror'
)

# Metrics: RMSE, MAE, R², MAPE
```

### Classification (XGBoost)

```python
from xgboost import XGBClassifier

model = XGBClassifier(
    max_depth=6,
    learning_rate=0.1,
    n_estimators=100,
    objective='binary:logistic'
)

# Metrics: AUC-ROC, Precision, Recall, F1
```

### Time Series (Prophet)

```python
from prophet import Prophet

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    seasonality_mode='multiplicative'
)

# Metrics: MAPE, RMSE, MAE, Coverage
```

---

## References

### MLflow 3.1+
- [MLflow 3.0 Overview](https://learn.microsoft.com/en-us/azure/databricks/mlflow/mlflow-3-install)
- [Logged Models](https://learn.microsoft.com/en-us/azure/databricks/mlflow/logged-model)
- [Model Registry](https://learn.microsoft.com/en-us/azure/databricks/mlflow/model-registry-3)

### Feature Store
- [Feature Engineering Client](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/feature-store/uc/feature-tables-uc)
- [Train Models with Feature Store](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/feature-store/train-models-with-feature-store)

### Model Serving
- [Model Serving Overview](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/)
- [Serverless Model Serving](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/serverless-optimized-deployments)

### Cursor Rules
- [MLflow and ML Models Patterns](../.cursor/rules/ml/27-mlflow-mlmodels-patterns.mdc)
- [Databricks Asset Bundles](../.cursor/rules/common/databricks-asset-bundles.mdc)

---

## Time Estimates

| Task | Duration |
|------|----------|
| Feature Store Setup | 1-2 hours |
| First Model Training Pipeline | 2-3 hours |
| Additional Models (each) | 1-2 hours |
| Batch Inference Pipeline | 1-2 hours |
| Asset Bundle Configuration | 1 hour |
| **Total (3-5 models)** | **6-12 hours** |

---

## Next Steps

After ML Models:
1. **Real-time Serving**: Create model serving endpoints
2. **Model Monitoring**: Set up inference tables and drift detection
3. **A/B Testing**: Configure traffic splitting between model versions
4. **Dashboards**: Integrate predictions into AI/BI dashboards
5. **Alerting**: Set up alerts for model performance degradation


