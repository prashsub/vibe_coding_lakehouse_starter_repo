---
name: sql-alerting-patterns
description: Comprehensive guide for Databricks SQL Alerts - config-driven alerting framework with SDK deployment. Use when setting up SQL alerts, creating alert configuration tables, deploying alerts via Databricks SDK, or troubleshooting alert failures. Includes config-driven patterns, two-job separation (setup vs deploy), fully qualified table names (no parameters), severity-based routing, alert ID conventions, SQL query patterns (threshold, percentage change, anomaly detection), SDK integration, DAB job configuration, custom notification templates, Quartz cron schedules, and troubleshooting patterns.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: monitoring
---

# SQL Alerting: Config-Driven Framework for Databricks

## Overview

This skill provides a comprehensive config-driven framework for setting up Databricks SQL Alerts using a Delta configuration table and SDK deployment. It covers alert rule design, SQL query patterns, SDK integration, and deployment workflows.

## When to Use This Skill

- Setting up SQL alerts for Gold layer tables
- Creating alert configuration tables
- Deploying alerts via Databricks SDK
- Troubleshooting alert failures
- Implementing config-driven alerting (runtime updates without code changes)
- Creating severity-based notification routing

## Core Principles

### Principle 1: Config-Driven Alerting
Alert rules are stored in a Delta configuration table, not hardcoded. This enables:
- Runtime updates without code changes
- Centralized alert management
- Version history via Delta time travel
- Easy enable/disable without deployment

### Principle 2: Two-Job Pattern
**⚠️ CRITICAL:** Alerting uses a two-job separation of concerns:

1. **Setup Job** (`alert_rules_setup_job`): Creates/updates the `alert_rules` config table
2. **Deploy Job** (`alert_deploy_job`): Reads config table and creates/updates SQL Alerts via SDK

**Why This Matters:**
- Rules can be modified in Delta without redeploying alerts
- Dry-run capability for validation
- Clear separation between configuration and deployment

### Principle 3: Fully Qualified Table Names
**⚠️ CRITICAL:** Databricks SQL Alerts (Public Preview) do NOT support parameters in queries.

```sql
-- ❌ WRONG: Parameterized query (NOT SUPPORTED)
SELECT * FROM ${catalog}.${schema}.fact_booking_daily

-- ✅ CORRECT: Fully qualified table names embedded in query
SELECT * FROM wanderbricks_dev.gold.fact_booking_daily
```

**Pattern:** Use f-strings at rule creation time to embed catalog/schema:

```python
rev_001_query = f"""
SELECT ...
FROM {catalog}.{gold_schema}.fact_booking_daily
WHERE ...
"""
```

### Principle 4: Severity-Based Notification Routing
Alerts are categorized by severity with different notification strategies:

| Severity | Icon | Action Required | Notification Speed |
|----------|------|-----------------|-------------------|
| CRITICAL | 🔴 | Immediate | Real-time (email + Slack) |
| WARNING | 🟡 | Investigate soon | Batched (email) |
| INFO | 🟢 | Informational | Daily digest |

## Quick Reference

### Alert ID Convention

**Format:** `<DOMAIN>-<NUMBER>-<SEVERITY>`

**Components:**
- `DOMAIN`: Business domain (3-4 chars): REV, ENG, PROP, HOST, CUST
- `NUMBER`: Sequential within domain (3 digits, zero-padded)
- `SEVERITY`: CRIT, WARN, or INFO

**Examples:**
- `REV-001-CRIT` → Revenue domain, alert #1, critical severity
- `ENG-003-WARN` → Engagement domain, alert #3, warning severity
- `PROP-004-INFO` → Property domain, alert #4, informational

### Alert Rules Configuration Table Schema

**Required Columns for SDK Deployment:**

| Column | SDK Field | Required | Notes |
|--------|-----------|----------|-------|
| `alert_query` | `query_text` | ✅ | Full SQL query |
| `condition_column` | `AlertOperandColumn.name` | ✅ | Column to check |
| `condition_operator` | `AlertConditionOperator` | ✅ | >, <, =, etc. |
| `condition_threshold` | `AlertOperandValue.string_value` | ✅ | Threshold value |
| `schedule_cron` | `cron_schedule` | ✅ | Quartz format |
| `schedule_timezone` | `cron_timezone` | ✅ | IANA timezone |

See [alert-patterns.md](references/alert-patterns.md) for complete schema definition.

### SQL Query Patterns

1. **Threshold Comparison** - Alert when metric crosses threshold
2. **Percentage Change from Baseline** - Alert when metric deviates from historical average
3. **Statistical Anomaly Detection (Z-Score)** - Alert when metric is statistically unusual
4. **Count-Based Alert** - Alert when count is below threshold
5. **Informational Summary** - Always triggers for daily/weekly summaries

See [alert-patterns.md](references/alert-patterns.md) for detailed SQL examples.

## Critical Rules

### Rule 1: Fully Qualified Table Names Only

**❌ WRONG:** Parameterized queries (NOT SUPPORTED)
```sql
SELECT * FROM ${catalog}.${schema}.fact_booking_daily
```

**✅ CORRECT:** Fully qualified names embedded at rule creation
```python
alert_query = f"""
SELECT * FROM {catalog}.{gold_schema}.fact_booking_daily
WHERE check_in_date = DATE_ADD(CURRENT_DATE(), -1)
"""
```

### Rule 2: Query Must Return Rows Only When Condition Met

**❌ WRONG:** Returns rows always
```sql
SELECT rate FROM ... WHERE rate IS NOT NULL
```

**✅ CORRECT:** Only returns rows when threshold crossed
```sql
SELECT rate FROM ... HAVING rate > 15
```

### Rule 3: Always Include alert_message Column

**✅ CORRECT:** Human-readable notification content
```sql
SELECT 
    cancellation_rate,
    'CRITICAL: Cancellation rate at ' || cancellation_rate || '%' as alert_message
FROM ...
HAVING cancellation_rate > 15
```

### Rule 4: Use NULLIF for Division

**✅ CORRECT:** Prevent division by zero errors
```sql
ROUND(SUM(cancellation_count) / NULLIF(SUM(booking_count), 0) * 100, 1) as cancellation_rate
```

## Core Patterns

### Pattern 1: Alert Rules Configuration Table

```sql
CREATE TABLE IF NOT EXISTS {catalog}.{gold_schema}.alert_rules (
    alert_id STRING NOT NULL,
    alert_name STRING NOT NULL,
    domain STRING NOT NULL,
    severity STRING NOT NULL,
    alert_description STRING NOT NULL,
    alert_query STRING NOT NULL,
    condition_column STRING NOT NULL,
    condition_operator STRING NOT NULL,
    condition_threshold STRING NOT NULL,
    aggregation_type STRING,
    schedule_cron STRING NOT NULL,
    schedule_timezone STRING NOT NULL,
    notification_emails STRING,
    notification_slack_channel STRING,
    custom_subject_template STRING,
    custom_body_template STRING,
    notify_on_ok BOOLEAN NOT NULL,
    rearm_seconds INT,
    is_enabled BOOLEAN NOT NULL,
    tags STRING,
    owner STRING NOT NULL,
    record_created_timestamp TIMESTAMP NOT NULL,
    record_updated_timestamp TIMESTAMP NOT NULL,
    CONSTRAINT pk_alert_rules PRIMARY KEY (alert_id) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO
```

### Pattern 2: SDK Alert Creation

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import (
    AlertCondition,
    AlertConditionOperand,
    AlertConditionThreshold,
    AlertOperandColumn,
    AlertOperandValue,
    AlertConditionOperator,
)

def create_alert(ws: WorkspaceClient, rule: dict, warehouse_id: str):
    """Create a SQL Alert from a rule configuration."""
    
    # Build condition
    condition = AlertCondition(
        op=get_operator_enum(rule["condition_operator"]),
        operand=AlertConditionOperand(
            column=AlertOperandColumn(name=rule["condition_column"])
        ),
        threshold=AlertConditionThreshold(
            value=AlertOperandValue(
                string_value=str(rule["condition_threshold"])
            )
        )
    )
    
    # Create alert
    new_alert = ws.alerts.create(
        display_name=f"[{rule['severity']}] {rule['alert_name']}",
        query_text=rule["alert_query"],
        warehouse_id=warehouse_id,
        condition=condition,
        cron_schedule=rule["schedule_cron"],
        cron_timezone=rule["schedule_timezone"],
        notify_on_ok=rule.get("notify_on_ok", False),
        custom_subject=rule.get("custom_subject_template"),
        custom_body=rule.get("custom_body_template"),
    )
    
    return new_alert
```

### Pattern 3: Idempotent Deployment

```python
def deploy_alert(ws: WorkspaceClient, rule: dict, warehouse_id: str, 
                 existing_alerts: dict, dry_run: bool = False):
    """Deploy alert with idempotency check."""
    
    alert_name = f"[{rule['severity']}] {rule['alert_name']}"
    existing = existing_alerts.get(alert_name)
    
    if dry_run:
        if existing:
            print(f"[DRY RUN] Would update: {existing.id}")
        else:
            print(f"[DRY RUN] Would create new alert")
        return {"status": "dry_run"}
    
    if existing:
        print(f"Alert exists: {existing.id} - skipping")
        return {"status": "skipped", "id": existing.id}
    
    # Create new alert
    new_alert = create_alert(ws, rule, warehouse_id)
    return {"status": "created", "id": new_alert.id}
```

### Pattern 4: DAB Job Configuration

**Setup Job:**
```yaml
resources:
  jobs:
    alert_rules_setup_job:
      name: "[${bundle.target}] Alert Rules - Setup"
      description: "Creates alert_rules configuration table"
      environments:
        - environment_key: default
          spec:
            environment_version: "4"
      tasks:
        - task_key: setup_alert_rules
          environment_key: default
          notebook_task:
            notebook_path: ../../src/alerting/setup_alert_rules.py
            base_parameters:
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
```

**Deploy Job:**
```yaml
resources:
  jobs:
    alert_deploy_job:
      name: "[${bundle.target}] Alert - Deploy"
      description: "Deploys SQL alerts from alert_rules configuration table"
      environments:
        - environment_key: default
          spec:
            environment_version: "4"
            dependencies:
              - "databricks-sdk>=0.28.0"  # Required for alerts API
      tasks:
        - task_key: deploy_alerts
          environment_key: default
          notebook_task:
            notebook_path: ../../src/alerting/deploy_alerts.py
            base_parameters:
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
              warehouse_id: ${var.warehouse_id}
              dry_run: "false"
```

## Reference Files

### [alert-patterns.md](references/alert-patterns.md)
Comprehensive SQL alert patterns including:
- SQL query patterns (threshold, percentage change, anomaly detection, count-based, informational)
- Complete alert examples (CRITICAL, WARNING, INFO)
- Custom notification templates
- Schedule patterns (Quartz cron)
- Query design rules
- Troubleshooting patterns

## Assets

### [alert-config.yaml](assets/templates/alert-config.yaml)
Template configuration file for alert rules with example structure.

## Troubleshooting

### Problem: Alert Not Triggering

**Symptoms:** Alert is enabled but never sends notifications

**Diagnosis Steps:**
1. Run the alert query manually - does it return rows?
2. Check condition: does returned value satisfy operator + threshold?
3. Verify warehouse is running when schedule fires
4. Check notification destination configuration

**Fix:** Add HAVING clause to filter results:
```sql
-- ✅ CORRECT: Only returns rows when threshold crossed
SELECT rate FROM ... HAVING rate > 15
```

### Problem: Alert Always Triggering

**Symptoms:** Getting notifications even when condition shouldn't be met

**Fix:** Query returns rows even when condition isn't met - missing HAVING clause

### Problem: "Query Failed" Error Status

**Common Causes:**
1. Table doesn't exist (wrong catalog/schema)
2. Column doesn't exist
3. SQL syntax error
4. Warehouse unavailable

**Debug:** Test query in notebook first:
```python
spark.sql(f"""
    {alert_query}
""").display()
```

### Problem: SDK Permission Error

**Fix:** Ensure service principal or user has:
- `CAN_MANAGE` permission on SQL Warehouse
- `CAN_CREATE` permission for SQL Alerts
- `CAN_USE` on catalog and schema

## Best Practices

### ✅ DO

1. **Use config table for all rules** - Never hardcode alert configurations
2. **Include `alert_message` column** - Human-readable notification content
3. **Test queries manually first** - Verify in notebook before adding to config
4. **Use NULLIF for division** - Prevent division by zero errors
5. **Set appropriate rearm periods** - Prevent alert fatigue (1800-3600 seconds)
6. **Enable notify_on_ok for critical** - Know when issues are resolved
7. **Use dry_run for validation** - Test deployment without creating alerts

### ❌ DON'T

1. **Don't use parameters in queries** - SQL Alerts don't support `${param}` syntax
2. **Don't skip the HAVING clause** - Queries should only return rows when alerting
3. **Don't set rearm too low** - Causes notification spam
4. **Don't hardcode credentials** - Use WorkspaceClient() for auto-auth
5. **Don't skip schema validation** - Verify alert_rules table exists before deploying

## Workflow Summary

### Initial Setup

```bash
# 1. Deploy alert rules table
databricks bundle run alert_rules_setup_job -t dev

# 2. Verify rules
# SELECT * FROM {catalog}.{gold_schema}.alert_rules

# 3. Deploy alerts (dry run first)
# Edit dry_run: "true" in job config
databricks bundle run alert_deploy_job -t dev

# 4. Deploy alerts (for real)
# Edit dry_run: "false" in job config
databricks bundle run alert_deploy_job -t dev
```

### Adding New Alerts

1. Add rule to `get_alert_rules()` function in `setup_alert_rules.py`
2. Run setup job: `databricks bundle run alert_rules_setup_job -t dev`
3. Run deploy job: `databricks bundle run alert_deploy_job -t dev`

### Modifying Existing Alerts

1. Update rule in config table or `setup_alert_rules.py`
2. Run setup job to update config table
3. Delete existing alert in Databricks UI
4. Run deploy job to recreate with new configuration

## References

- [Databricks SQL Alerts Documentation](https://docs.databricks.com/sql/user/alerts/)
- [Alert Notifications](https://docs.databricks.com/sql/user/alerts/index.html#notifications)
- [Databricks SDK - Alerts API](https://databricks-sdk-py.readthedocs.io/en/latest/)
- [Quartz Cron Expression Format](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html)

## Summary

**Key Takeaways:**
- Use config-driven approach with Delta table for runtime updates
- Two-job pattern: setup (config) and deploy (SDK)
- Fully qualified table names only (no parameters)
- Queries must return rows ONLY when condition is met (HAVING clause)
- Always include `alert_message` column for notifications
- Use NULLIF for division to prevent errors

**Next Steps:**
1. Review [alert-patterns.md](references/alert-patterns.md) for SQL query examples
2. Set up alert_rules configuration table
3. Create setup and deploy jobs
4. Test with dry_run before production deployment
