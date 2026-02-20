# Databricks notebook source
# ===========================================================================
# PATH SETUP FOR ASSET BUNDLE IMPORTS
# ===========================================================================
# Enables imports from src modules when deployed via Databricks Asset Bundles.
# Reference: https://docs.databricks.com/aws/en/notebooks/share-code
import sys
import os

try:
    _notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    _bundle_root = "/Workspace" + str(_notebook_path).rsplit('/src/', 1)[0]
    if _bundle_root not in sys.path:
        sys.path.insert(0, _bundle_root)
        print(f"Added bundle root to sys.path: {_bundle_root}")
except Exception as e:
    print(f"Path setup skipped (local execution): {e}")
# ===========================================================================
"""
Deploy Genie Spaces from JSON configuration files via REST API.

This notebook is designed for Databricks Asset Bundle deployment using notebook_task.
Parameters are received via dbutils.widgets.get() (not argparse).

For CLI/CI usage, use scripts/import_genie_space.py instead.
"""
# COMMAND ----------

import json
import uuid
import requests
from pathlib import Path

# COMMAND ----------

# Parameters via dbutils.widgets (set by notebook_task base_parameters)
catalog = dbutils.widgets.get("catalog")
gold_schema = dbutils.widgets.get("gold_schema")
config_dir = dbutils.widgets.get("config_dir")
warehouse_id = dbutils.widgets.get("warehouse_id")

print(f"Catalog: {catalog}")
print(f"Gold Schema: {gold_schema}")
print(f"Config Dir: {config_dir}")
print(f"Warehouse ID: {warehouse_id}")

# COMMAND ----------

# Derive workspace host and token from runtime context
ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
host = ctx.apiUrl().get()
token = ctx.apiToken().get()

print(f"Workspace: {host}")

# COMMAND ----------

def substitute_variables(data: dict, variables: dict) -> dict:
    """Replace template variables (${catalog}, ${gold_schema}, etc.) with actual values."""
    json_str = json.dumps(data)
    for key, value in variables.items():
        json_str = json_str.replace(f"${{{key}}}", value)
    return json.loads(json_str)


def generate_id() -> str:
    """Generate a Genie Space compatible ID (32 hex chars, no dashes)."""
    return uuid.uuid4().hex


def list_existing_spaces(host: str, token: str) -> dict:
    """List existing Genie Spaces to check for duplicates."""
    url = f"{host}/api/2.0/genie/spaces"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def create_or_update_space(
    host: str,
    token: str,
    title: str,
    description: str,
    warehouse_id: str,
    config: dict,
    existing_spaces: dict
) -> dict:
    """Create a new Genie Space or update if one with the same title exists."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    existing_id = None
    for space in existing_spaces.get("spaces", []):
        if space.get("title") == title:
            existing_id = space.get("space_id")
            break

    payload = {
        "title": title,
        "description": description,
        "warehouse_id": warehouse_id,
        "serialized_space": json.dumps(config)
    }

    if existing_id:
        url = f"{host}/api/2.0/genie/spaces/{existing_id}"
        response = requests.patch(url, headers=headers, json=payload)
        action = "Updated"
    else:
        url = f"{host}/api/2.0/genie/spaces"
        response = requests.post(url, headers=headers, json=payload)
        action = "Created"

    response.raise_for_status()
    result = response.json()
    print(f"{action} Genie Space: {result.get('space_id', 'unknown')} ({title})")
    return result

# COMMAND ----------

# Resolve config directory path within the bundle workspace
_notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
_bundle_root = "/Workspace" + str(_notebook_path).rsplit('/src/', 1)[0]
config_path = Path(f"{_bundle_root}/{config_dir}")

print(f"Looking for JSON configs in: {config_path}")

json_files = sorted(config_path.glob("*.json"))
if not json_files:
    print(f"No JSON config files found in {config_path}")
    dbutils.notebook.exit("No configs found")

print(f"Found {len(json_files)} Genie Space config(s): {[f.name for f in json_files]}")

# COMMAND ----------

variables = {
    "catalog": catalog,
    "gold_schema": gold_schema,
}

existing_spaces = list_existing_spaces(host, token)
results = []

for config_file in json_files:
    print(f"\n--- Processing: {config_file.name} ---")

    with open(config_file, 'r') as f:
        raw_config = json.load(f)

    config = substitute_variables(raw_config, variables)

    title = config.pop("title", config_file.stem.replace("_", " ").title())
    description = config.pop("description", f"Genie Space deployed from {config_file.name}")

    result = create_or_update_space(
        host=host,
        token=token,
        title=title,
        description=description,
        warehouse_id=warehouse_id,
        config=config,
        existing_spaces=existing_spaces
    )
    results.append(result)

# COMMAND ----------

print(f"\n=== Deployment Summary ===")
print(f"Total Genie Spaces processed: {len(results)}")
for r in results:
    print(f"  - {r.get('title', 'unknown')}: {r.get('space_id', 'unknown')}")

dbutils.notebook.exit(json.dumps({"spaces_deployed": len(results)}))
