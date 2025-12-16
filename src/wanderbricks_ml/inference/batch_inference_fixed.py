# Databricks notebook source
"""
Robust Batch Inference for All ML Models

Critical Design Principles:
1. Match EXACT model signature (column order + types)
2. Minimal preprocessing (avoid type conversions that break schema)
3. Model-specific feature preparation
4. Proper error handling with detailed logging

Reference: Production batch scoring patterns
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, lit, current_timestamp, current_date, when
import mlflow
from mlflow.models import ModelSignature
import pandas as pd
import numpy as np
from datetime import datetime


def get_parameters():
    """Get job parameters from dbutils widgets."""
    catalog = dbutils.widgets.get("catalog")
    model_name = dbutils.widgets.get("model_name")
    input_table = dbutils.widgets.get("input_table")
    output_table = dbutils.widgets.get("output_table")
    model_version = dbutils.widgets.get("model_version")
    feature_schema = dbutils.widgets.get("feature_schema")
    
    print(f"Catalog: {catalog}")
    print(f"Model Name: {model_name}")
    print(f"Input Table: {input_table}")
    print(f"Output Table: {output_table}")
    print(f"Model Version: {model_version}")
    print(f"Feature Schema: {feature_schema}")
    
    return catalog, model_name, input_table, output_table, model_version, feature_schema


def load_model_and_signature(catalog: str, feature_schema: str, model_name: str, model_version: str):
    """
    Load model and extract signature to know exact expected schema.
    """
    print("\n" + "="*80)
    print("Loading model and extracting signature")
    print("="*80)
    
    full_model_name = f"{catalog}.{feature_schema}.{model_name}"
    
    if model_version == "latest":
        # Get latest version
        client = mlflow.tracking.MlflowClient()
        versions = client.search_model_versions(f"name='{full_model_name}'")
        if versions:
            latest_version = max(versions, key=lambda v: int(v.version))
            version_num = latest_version.version
            print(f"Found latest version: {version_num}")
            model_uri = f"models:/{full_model_name}/{version_num}"
        else:
            raise Exception(f"No model versions found for {full_model_name}")
    else:
        model_uri = f"models:/{full_model_name}/{model_version}"
    
    print(f"Model URI: {model_uri}")
    
    # Load model to get signature
    model = mlflow.pyfunc.load_model(model_uri)
    signature = model.metadata.signature
    
    print(f"\nModel Signature:")
    print(f"  Input columns: {[inp.name for inp in signature.inputs]}")
    print(f"  Input types: {[(inp.name, str(inp.type)) for inp in signature.inputs]}")
    
    return model, model_uri, signature


def prepare_features_for_signature(
    spark: SparkSession,
    input_table: str,
    model_name: str,
    signature: ModelSignature,
    catalog: str,
    feature_schema: str
):
    """
    Prepare features matching EXACT model signature.
    
    Strategy:
    1. Read input table for keys
    2. Read feature tables
    3. Create derived columns as needed
    4. Select ONLY columns in signature (exact order) for model input
    5. Convert types to match signature
    6. PRESERVE key columns (property_id, user_id, destination_id) for output
    
    Returns:
        tuple: (features_pdf for model, keys_pdf for output join)
    """
    print("\n" + "="*80)
    print("Preparing features to match model signature")
    print("="*80)
    
    input_df = spark.table(input_table)
    
    # Extract expected column names and types from signature
    expected_cols = {inp.name: str(inp.type) for inp in signature.inputs}
    print(f"\nExpected {len(expected_cols)} columns from model signature")
    
    # Model-specific feature preparation
    # IMPORTANT: Track key columns to preserve for output
    key_columns = []
    
    if "demand_predictor" in model_name:
        # Start with property_id + check_in_date
        base_df = input_df.select("property_id", "check_in_date").distinct()
        key_columns = ["property_id"]
        
        # Add temporal features (expected by model)
        base_df = (
            base_df
            .withColumn("month", F.month("check_in_date").cast("integer"))
            .withColumn("quarter", F.quarter("check_in_date").cast("integer"))
            .withColumn("is_holiday", F.lit(0).cast("integer"))
        )
        
        # Join property features to get destination_id
        prop_features = spark.table(f"{catalog}.{feature_schema}.property_features")
        features_df = base_df.join(prop_features, "property_id", "left")
        key_columns.append("destination_id")
        
    elif "conversion_predictor" in model_name:
        # Start with property_id
        base_df = input_df.select("property_id").distinct()
        key_columns = ["property_id"]
        
        # Join engagement features
        eng_features = spark.table(f"{catalog}.{feature_schema}.engagement_features")
        features_df = base_df.join(eng_features, "property_id", "left")
        
        # Join property features (drop duplicates) to get destination_id
        prop_features = (
            spark.table(f"{catalog}.{feature_schema}.property_features")
            .drop("feature_date", "feature_timestamp")
        )
        features_df = features_df.join(prop_features, "property_id", "left")
        key_columns.append("destination_id")
        
    elif "pricing_optimizer" in model_name:
        # Pricing model trained without Feature Store
        base_df = input_df.select("property_id").distinct()
        key_columns = ["property_id"]
        
        # Add temporal features from booking data
        booking_context = (
            input_df
            .select("property_id", "check_in_date")
            .groupBy("property_id")
            .agg(F.max("check_in_date").alias("check_in_date"))
        )
        
        features_df = (
            base_df
            .join(booking_context, "property_id", "left")
            .withColumn("month", F.month("check_in_date").cast("integer"))
            .withColumn("quarter", F.quarter("check_in_date").cast("integer"))
            .withColumn("is_peak_season", 
                       when(F.month("check_in_date").isin([6,7,8,12]), 1).otherwise(0).cast("integer"))
            .drop("check_in_date")
        )
        
        # Try to add destination_id from property features if available
        try:
            prop_dest = (
                spark.table(f"{catalog}.{feature_schema}.property_features")
                .select("property_id", "destination_id")
                .distinct()
            )
            features_df = features_df.join(prop_dest, "property_id", "left")
            key_columns.append("destination_id")
        except:
            pass  # destination_id not available
        
    elif "customer_ltv" in model_name:
        # LTV model trained without Feature Store
        base_df = input_df.select("user_id").distinct()
        key_columns = ["user_id"]
        
        # Join user features
        user_features = spark.table(f"{catalog}.{feature_schema}.user_features")
        features_df = base_df.join(user_features, "user_id", "left")
        
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    print(f"Features DataFrame: {features_df.count()} records, {len(features_df.columns)} columns")
    print(f"Key columns to preserve: {key_columns}")
    print(f"Features DataFrame columns: {features_df.columns}")
    
    # Convert to Pandas for precise type control
    pdf = features_df.toPandas()
    
    # =========================================================================
    # CRITICAL: Verify key columns exist in DataFrame BEFORE extracting
    # =========================================================================
    print(f"\nVerifying key columns exist in pandas DataFrame...")
    print(f"  PDF columns: {list(pdf.columns)}")
    
    missing_keys = [k for k in key_columns if k not in pdf.columns]
    if missing_keys:
        print(f"  ⚠️  WARNING: Key columns missing from DataFrame: {missing_keys}")
        print(f"  Available columns: {list(pdf.columns)}")
        # Remove missing keys from key_columns list
        key_columns = [k for k in key_columns if k in pdf.columns]
        print(f"  Adjusted key_columns: {key_columns}")
    
    # =========================================================================
    # PRESERVE KEY COLUMNS for output (before filtering to signature columns)
    # =========================================================================
    keys_pdf = pdf[key_columns].copy()
    print(f"Preserved {len(keys_pdf)} key records with columns: {list(keys_pdf.columns)}")
    
    # Verify key data is non-null
    for key_col in key_columns:
        non_null = keys_pdf[key_col].notna().sum()
        print(f"  Key '{key_col}': {non_null}/{len(keys_pdf)} non-null values")
    
    # =========================================================================
    # CRITICAL: Match signature types EXACTLY
    # MLflow enforces strict type matching - int64 != int32
    # =========================================================================
    print(f"\nConverting {len(expected_cols)} columns to match model signature...")
    
    for col_name, col_type in expected_cols.items():
        if col_name not in pdf.columns:
            print(f"  ⚠️  Missing column: {col_name} (adding with default value)")
            # Add missing column with proper type
            if 'double' in col_type:
                pdf[col_name] = np.float64(0.0)
            elif 'float' in col_type:
                pdf[col_name] = np.float32(0.0)
            elif 'long' in col_type:
                pdf[col_name] = np.int64(0)
            elif 'integer' in col_type:
                pdf[col_name] = np.int32(0)
            elif 'boolean' in col_type:
                pdf[col_name] = False
            else:
                pdf[col_name] = None
        else:
            # Convert existing column to match signature type EXACTLY
            try:
                if 'double' in col_type:
                    # Convert to float64 (double)
                    pdf[col_name] = pd.to_numeric(pdf[col_name], errors='coerce').fillna(0.0).astype(np.float64)
                elif 'float' in col_type:
                    # Convert to float32 (float)
                    pdf[col_name] = pd.to_numeric(pdf[col_name], errors='coerce').fillna(0.0).astype(np.float32)
                elif 'long' in col_type:
                    # Convert to int64 (long)
                    pdf[col_name] = pd.to_numeric(pdf[col_name], errors='coerce').fillna(0).astype(np.int64)
                elif 'integer' in col_type:
                    # Convert to int32 (integer) - MLflow is strict about this!
                    # First convert to numeric, then clip to int32 range, then cast
                    numeric_vals = pd.to_numeric(pdf[col_name], errors='coerce').fillna(0)
                    # Clip to int32 range to avoid overflow
                    clipped = numeric_vals.clip(lower=-2147483648, upper=2147483647)
                    pdf[col_name] = clipped.astype(np.int32)
                elif 'boolean' in col_type:
                    # Convert to boolean
                    if pdf[col_name].dtype in ['int64', 'float64', 'int32', 'float32']:
                        pdf[col_name] = pdf[col_name].astype(bool)
                    elif pdf[col_name].dtype == 'object':
                        pdf[col_name] = pdf[col_name].astype(str).str.lower().isin(['true', '1', 'yes'])
                    else:
                        pdf[col_name] = pdf[col_name].astype(bool)
            except Exception as e:
                print(f"  ⚠️  Error converting {col_name} to {col_type}: {e}")
                # Fallback: try basic conversion
                if 'integer' in col_type:
                    pdf[col_name] = pdf[col_name].fillna(0).astype(np.int32)
                elif 'long' in col_type:
                    pdf[col_name] = pdf[col_name].fillna(0).astype(np.int64)
                elif 'double' in col_type or 'float' in col_type:
                    pdf[col_name] = pdf[col_name].fillna(0.0).astype(np.float64)
    
    # Select ONLY columns in signature (in signature order) for model input
    signature_col_names = [inp.name for inp in signature.inputs]
    pdf_final = pdf[signature_col_names]
    
    # =========================================================================
    # VERIFY: Print dtypes to confirm correct conversion
    # =========================================================================
    print(f"\n✓ Features prepared matching signature")
    print(f"  Final shape: {pdf_final.shape}")
    print(f"  Column types match: {len(pdf_final.columns)}/{len(expected_cols)}")
    
    # Show dtype verification for first few columns
    print(f"\n  Dtype verification (first 10 columns):")
    for i, (col_name, col_type) in enumerate(list(expected_cols.items())[:10]):
        actual_dtype = pdf_final[col_name].dtype
        expected = col_type.split('(')[0].strip()  # Remove (required)
        print(f"    {col_name}: expected={expected}, actual={actual_dtype}")
    
    # Check for any remaining int64 columns that should be int32
    int64_cols = [c for c in pdf_final.columns if pdf_final[c].dtype == 'int64']
    if int64_cols:
        print(f"\n  ⚠️  Columns still as int64 (may need int32): {int64_cols[:5]}...")
    
    return pdf_final, keys_pdf


def score_batch_with_model(model, features_pdf: pd.DataFrame, keys_pdf: pd.DataFrame, model_name: str):
    """
    Score batch using loaded MLflow model.
    
    Features DataFrame already matches model signature.
    Keys DataFrame contains identifiers to preserve in output.
    
    CRITICAL: Keys (property_id, user_id) MUST be preserved in output for TVFs.
    """
    print("\n" + "="*80)
    print("Scoring batch")
    print("="*80)
    
    print(f"Scoring {len(features_pdf)} records...")
    print(f"Keys DataFrame columns: {list(keys_pdf.columns)}")
    print(f"Keys DataFrame shape: {keys_pdf.shape}")
    
    # Verify keys are present BEFORE scoring
    for key_col in keys_pdf.columns:
        print(f"  Key column '{key_col}': {keys_pdf[key_col].notna().sum()} non-null values")
    
    # Make predictions
    predictions = model.predict(features_pdf)
    
    # ==========================================================================
    # CRITICAL FIX: Use pd.concat with reset_index to ensure proper alignment
    # The previous approach using .values assignment lost key columns
    # ==========================================================================
    
    # Reset indices to ensure alignment
    keys_reset = keys_pdf.reset_index(drop=True)
    features_reset = features_pdf.reset_index(drop=True)
    
    # Start with keys (property_id, user_id, destination_id)
    output_pdf = keys_reset.copy()
    
    # Add feature columns that are NOT already in keys (avoid duplicates)
    for col in features_reset.columns:
        if col not in output_pdf.columns:
            output_pdf[col] = features_reset[col]
        else:
            # Column exists in both - keep the one from keys (usually destination_id)
            print(f"  Note: Column '{col}' exists in both keys and features, keeping from keys")
    
    # Add predictions
    output_pdf['prediction'] = predictions
    
    # ==========================================================================
    # VERIFY keys are preserved in output
    # ==========================================================================
    print(f"\n✓ Output DataFrame columns: {list(output_pdf.columns)}")
    
    # Check key columns are present
    expected_keys = list(keys_pdf.columns)
    missing_keys = [k for k in expected_keys if k not in output_pdf.columns]
    if missing_keys:
        print(f"⚠️  WARNING: Missing key columns in output: {missing_keys}")
        # Re-add missing keys
        for key_col in missing_keys:
            output_pdf[key_col] = keys_reset[key_col]
            print(f"  ✓ Re-added key column: {key_col}")
    
    # Verify key columns have data
    for key_col in expected_keys:
        if key_col in output_pdf.columns:
            non_null = output_pdf[key_col].notna().sum()
            print(f"  ✓ Key '{key_col}' in output: {non_null} non-null values")
        else:
            print(f"  ❌ Key '{key_col}' MISSING from output!")
    
    print(f"\n✓ Scored {len(output_pdf)} records")
    print(f"✓ Output columns ({len(output_pdf.columns)} total): {list(output_pdf.columns[:8])}...")
    
    return output_pdf


def add_metadata_and_save(
    spark: SparkSession,
    predictions_pdf: pd.DataFrame,
    model_name: str,
    model_uri: str,
    output_table: str
):
    """
    Add metadata and save predictions to Delta table.
    
    CRITICAL: Verify key columns (property_id, user_id) are present before saving.
    """
    print("\n" + "="*80)
    print("Adding metadata and saving predictions")
    print("="*80)
    
    # =========================================================================
    # CRITICAL: Verify key columns before converting to Spark
    # =========================================================================
    print(f"Input pandas DataFrame columns: {list(predictions_pdf.columns)}")
    print(f"Input pandas DataFrame shape: {predictions_pdf.shape}")
    
    # Check for key columns
    key_columns_to_check = ['property_id', 'user_id', 'destination_id']
    for key_col in key_columns_to_check:
        if key_col in predictions_pdf.columns:
            non_null = predictions_pdf[key_col].notna().sum()
            print(f"  ✓ Key '{key_col}' present: {non_null}/{len(predictions_pdf)} non-null values")
        else:
            print(f"  - Key '{key_col}' not in DataFrame (may not be required for this model)")
    
    # Convert back to Spark
    predictions_df = spark.createDataFrame(predictions_pdf)
    
    print(f"\nSpark DataFrame schema before metadata:")
    predictions_df.printSchema()
    
    # Add metadata
    predictions_df = (
        predictions_df
        .withColumn("model_name", lit(model_name))
        .withColumn("model_uri", lit(model_uri))
        .withColumn("scored_at", current_timestamp())
        .withColumn("scoring_date", current_date())
    )
    
    # Rename prediction column based on model type
    if "demand_predictor" in model_name:
        predictions_df = predictions_df.withColumnRenamed("prediction", "predicted_bookings")
        
    elif "conversion_predictor" in model_name:
        predictions_df = (
            predictions_df
            .withColumnRenamed("prediction", "conversion_probability")
            .withColumn("predicted_conversion", 
                       when(col("conversion_probability") > 0.5, 1).otherwise(0))
        )
        
    elif "pricing_optimizer" in model_name:
        predictions_df = predictions_df.withColumnRenamed("prediction", "recommended_price")
        
    elif "customer_ltv" in model_name:
        predictions_df = (
            predictions_df
            .withColumnRenamed("prediction", "predicted_ltv_12m")
            .withColumn("ltv_segment",
                       when(col("predicted_ltv_12m") >= 2500, "VIP")
                       .when(col("predicted_ltv_12m") >= 1000, "High")
                       .when(col("predicted_ltv_12m") >= 500, "Medium")
                       .otherwise("Low"))
        )
    
    # =========================================================================
    # Final verification before save
    # =========================================================================
    print(f"\nFinal DataFrame schema before save:")
    predictions_df.printSchema()
    
    final_columns = predictions_df.columns
    print(f"Final columns ({len(final_columns)}): {final_columns}")
    
    # Verify key columns are present
    key_check = {
        'demand_predictor': ['property_id', 'destination_id'],
        'conversion_predictor': ['property_id', 'destination_id'],
        'pricing_optimizer': ['property_id'],
        'customer_ltv': ['user_id']
    }
    
    expected_keys = []
    for model_key, keys in key_check.items():
        if model_key in model_name:
            expected_keys = keys
            break
    
    if expected_keys:
        missing = [k for k in expected_keys if k not in final_columns]
        if missing:
            print(f"\n⚠️  WARNING: Expected key columns missing from output: {missing}")
            print(f"    This will cause TVFs to fail!")
        else:
            print(f"\n✓ All expected key columns present: {expected_keys}")
    
    # Save predictions
    print(f"\nWriting to: {output_table}")
    
    predictions_df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("mergeSchema", "true") \
        .option("overwriteSchema", "true") \
        .saveAsTable(output_table)
    
    final_count = spark.table(output_table).count()
    print(f"✓ Saved {final_count} predictions to {output_table}")
    
    # Verify saved table has key columns
    saved_df = spark.table(output_table)
    saved_columns = saved_df.columns
    print(f"\nSaved table columns: {saved_columns}")
    
    return final_count


def main():
    """Main batch inference pipeline with robust schema matching."""
    
    catalog, model_name, input_table, output_table, model_version, feature_schema = get_parameters()
    
    spark = SparkSession.builder.appName("Batch Inference (Fixed)").getOrCreate()
    
    try:
        # Load model and get signature
        model, model_uri, signature = load_model_and_signature(
            catalog, feature_schema, model_name, model_version
        )
        
        # Prepare features matching signature EXACTLY
        # Returns (features_pdf, keys_pdf) tuple - keys preserved for output
        features_pdf, keys_pdf = prepare_features_for_signature(
            spark, input_table, model_name, signature, catalog, feature_schema
        )
        
        # Score batch (includes keys in output)
        predictions_pdf = score_batch_with_model(model, features_pdf, keys_pdf, model_name)
        
        # Save with metadata
        record_count = add_metadata_and_save(
            spark, predictions_pdf, model_name, model_uri, output_table
        )
        
        print("\n" + "="*80)
        print("✓ Batch inference completed successfully!")
        print("="*80)
        print(f"\nModel: {catalog}.{feature_schema}.{model_name}")
        print(f"Version: {model_version}")
        print(f"Input: {input_table}")
        print(f"Output: {output_table}")
        print(f"Records Scored: {record_count}")
        
        # Verify key columns in final output
        saved_df = spark.table(output_table)
        saved_columns = saved_df.columns
        
        print(f"\n--- KEY COLUMN VERIFICATION ---")
        if 'property_id' in saved_columns:
            print(f"✓ property_id: PRESENT")
        elif 'demand_predictor' in model_name or 'conversion' in model_name or 'pricing' in model_name:
            print(f"⚠️  property_id: MISSING (expected for {model_name})")
        
        if 'user_id' in saved_columns:
            print(f"✓ user_id: PRESENT")
        elif 'customer_ltv' in model_name:
            print(f"⚠️  user_id: MISSING (expected for {model_name})")
        
        if 'destination_id' in saved_columns:
            print(f"✓ destination_id: PRESENT")
        
        print(f"\nAll output columns: {saved_columns}")
        
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"\n❌ Error during batch inference: {str(e)}")
        print(f"\nFull traceback:\n{tb}")
        raise
        
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

