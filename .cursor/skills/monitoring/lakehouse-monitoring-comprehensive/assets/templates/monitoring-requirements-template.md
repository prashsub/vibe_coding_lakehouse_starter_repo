# Lakehouse Monitoring Requirements Template

**Instructions:** Copy this template and fill in all sections BEFORE starting monitoring setup.

---

## Project Context

| Field | Value |
|-------|-------|
| **Project Name** | _________________ |
| **Gold Catalog.Schema** | _________________ |
| **Monitoring Schema** | _________________ (typically `{gold_schema}_monitoring`) |
| **Monitoring Owner** | _________________ (team/email for alerts) |

---

## Tables to Monitor (2-5 critical tables)

| # | Table Name | Type | Monitor Mode | Priority | Alert On |
|---|-----------|------|-------------|----------|----------|
| 1 | | Fact / Dimension | time_series / snapshot | High / Medium / Low | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Priority Guide:**
- **High:** Core business tables, real-time decisions, revenue-impacting
- **Medium:** Important but not critical, daily reports
- **Low:** Reference data, rarely changes

**Monitor Mode:**
- **time_series:** Has timestamp column → use `MonitorTimeSeries(timestamp_col="column_name", granularities=["1 day"])`
- **snapshot:** No timestamp → use `MonitorSnapshot()`

---

## Custom Metrics by Table

### Table: _________________ (Fact)

| Metric Type | Metric Name | Definition | Input Columns |
|------------|-------------|------------|---------------|
| AGGREGATE | | `SUM(...)` | `:table` |
| AGGREGATE | | `SUM(...)` | `:table` |
| DERIVED | | `agg1 / NULLIF(agg2, 0)` | `:table` |
| DRIFT | | `(({{current_df}}.metric - {{base_df}}.metric) / NULLIF({{base_df}}.metric, 0)) * 100` | `:table` |

### Table: _________________ (Dimension)

| Metric Type | Metric Name | Definition | Input Columns |
|------------|-------------|------------|---------------|
| AGGREGATE | | `COUNT(*)` | `:table` |
| AGGREGATE | | `COUNT(DISTINCT ...)` | `:table` |
| DERIVED | | `total / NULLIF(distinct, 0)` | `:table` |

### Table: _________________ (_____)

| Metric Type | Metric Name | Definition | Input Columns |
|------------|-------------|------------|---------------|
| AGGREGATE | | | `:table` |
| AGGREGATE | | | `:table` |
| DERIVED | | | `:table` |

**CRITICAL:** All related metrics (AGGREGATE, DERIVED, DRIFT) MUST use the same `input_columns` value.

---

## Alert Strategy

| Table | Metric | Threshold | Action |
|-------|--------|-----------|--------|
| | | | |
| | | | |
| | | | |
| | | | |

---

## Deployment Plan

| Step | Script | DAB Command |
|------|--------|-------------|
| 1. Deploy | | `databricks bundle deploy -t dev` |
| 2. Create monitors | `setup_monitors.py` | `databricks bundle run setup_monitoring -t dev` |
| 3. Wait for init | `wait_for_initialization.py` | `databricks bundle run wait_for_monitoring -t dev` |
| 4. Validate | Query monitoring tables | Manual SQL queries |
| 5. Document for Genie | Add table/column comments | See deployment-guide.md |
