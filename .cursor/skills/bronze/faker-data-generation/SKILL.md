---
name: faker-data-generation
description: Generate synthetic data with Faker for Bronze layer testing with configurable data corruption. Use when creating test data for data quality validation, testing DLT expectations, or simulating production-like datasets. Supports realistic data generation with intentional corruption patterns mapped to specific DQ expectations.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: bronze
---
# Faker Data Generation Patterns

## Overview

When generating synthetic data for Databricks Bronze layer tables, use Faker with **configurable data corruption** to test Silver layer data quality expectations.

## When to Use This Skill

Use when:
- Creating test data for data quality validation
- Testing DLT expectations with intentional violations
- Simulating production-like datasets for development/staging
- Validating referential integrity between dimensions and facts

## Core Principles

1. **Realistic Data**: Use Faker to generate production-like data
2. **Referential Integrity**: Maintain proper FK relationships between dimensions and facts
3. **Configurable Corruption**: Add intentional data quality issues for testing
4. **DQ Mapping**: Each corruption type maps to specific DLT expectations
5. **Documentation**: Document corruption patterns and their DQ impacts

## Critical Rules

### Standard Function Signature

```python
def generate_<entity>_data(
    dimension_keys: dict,
    num_records: int = 1000,
    corruption_rate: float = 0.05
) -> list:
    """
    Generate fake <entity> data with realistic patterns.
    
    Args:
        dimension_keys: Dictionary containing dimension keys for referential integrity
        num_records: Number of records to generate
        corruption_rate: Percentage of records to intentionally corrupt (0.0 to 1.0)
        
    Returns:
        List of <entity> dictionaries
    """
    fake = Faker()
    records = []
    
    print(f"\nGenerating {num_records} <entities> (corruption rate: {corruption_rate*100}%)")
    
    for i in range(num_records):
        # Generate valid data first
        record_data = generate_valid_record(fake, dimension_keys)
        
        # Apply corruption if selected
        should_corrupt = random.random() < corruption_rate
        
        if should_corrupt:
            record_data = apply_corruption(record_data, corruption_rate)
        
        records.append(record_data)
    
    return records
```

### Corruption Pattern Structure

```python
# Determine if this record should be corrupted for DQ testing
should_corrupt = random.random() < corruption_rate

if should_corrupt:
    # Apply various DQ violations to test expectations
    corruption_type = random.choice([
        'corruption_type_1',
        'corruption_type_2',
        'corruption_type_3',
    ])
    
    if corruption_type == 'corruption_type_1':
        # Will fail: <expectation_name>
        field = invalid_value  # Description of violation
```

### Comments Must Include

1. **Corruption type name**: Descriptive identifier
2. **DQ expectation failed**: Which expectation(s) this triggers
3. **Violation description**: What makes the data invalid

## Parameter Handling

### Function Parameters

```python
def get_parameters():
    """Get parameters from notebook widgets or command line."""
    try:
        # Try Databricks widgets first (notebook mode)
        catalog = dbutils.widgets.get("catalog")
        schema = dbutils.widgets.get("schema")
        num_records = int(dbutils.widgets.get("num_records"))
        corruption_rate = float(dbutils.widgets.get("corruption_rate"))
    except:
        # Fall back to command line arguments or defaults
        catalog = "default_catalog"
        schema = "default_schema"
        num_records = 1000
        corruption_rate = 0.05  # 5% corruption by default
        
        for arg in sys.argv[1:]:
            if arg.startswith("--catalog="):
                catalog = arg.split("=")[1]
            elif arg.startswith("--schema="):
                schema = arg.split("=")[1]
            elif arg.startswith("--num_records="):
                num_records = int(arg.split("=")[1])
            elif arg.startswith("--corruption_rate="):
                corruption_rate = float(arg.split("=")[1])
    
    return catalog, schema, num_records, corruption_rate
```

### Job Configuration (YAML)

```yaml
tasks:
  - task_key: generate_data
    environment_key: default
    notebook_task:
      notebook_path: ../src/layer/generate_data.py
      base_parameters:
        catalog: ${var.catalog}
        schema: ${var.schema}
        num_records: "1000"
        corruption_rate: "0.05"  # 5% corruption for DQ testing
```

## Quick Patterns

### Corruption Type Categories

1. **Missing Required Fields** - Null or empty required fields
2. **Invalid Format/Length** - Wrong format or below minimum length
3. **Out of Range Values** - Excessive or negative values
4. **Business Logic Violations** - Field relationships that violate rules
5. **Temporal Issues** - Dates too old or in the future
6. **Referential Integrity Issues** - Missing or invalid foreign keys

### Dimension vs Fact Patterns

**Dimensions** are referenced by facts, so must be generated first. Use locale-specific Faker for realistic data.

**Facts** reference dimensions, so dimensions must exist first. Load dimension keys for referential integrity.

## Common Mistakes to Avoid

### ❌ DON'T: Apply corruption before generating valid data

```python
# BAD - hard to maintain
if should_corrupt:
    field = generate_invalid_field()
else:
    field = generate_valid_field()
```

### ✅ DO: Generate valid data first, then corrupt

```python
# GOOD - clean separation
field = generate_valid_field()

if should_corrupt:
    field = corrupt_field(field)  # Modify valid data
```

### ❌ DON'T: Hardcode corruption without comments

```python
# BAD - no DQ mapping
if corruption_type == 'bad_data':
    field = None
```

### ✅ DO: Document which expectation fails

```python
# GOOD - clear DQ mapping
if corruption_type == 'null_required_field':
    # Will fail: valid_field_name
    field = None
```

### ❌ DON'T: Use magic numbers

```python
# BAD - unclear threshold
if random.random() < 0.05:
    # What is 0.05?
```

### ✅ DO: Use named parameter

```python
# GOOD - explicit parameter
should_corrupt = random.random() < corruption_rate
```

## Testing Scenarios

### Development: High Corruption
```yaml
corruption_rate: "0.10"  # 10% for thorough testing
```

### Staging: Realistic Corruption
```yaml
corruption_rate: "0.05"  # 5% production-like
```

### Production: No Synthetic Corruption
```yaml
corruption_rate: "0.0"  # Real data only
```

## Validation Checklist

When generating data with corruption:

- [ ] `corruption_rate` parameter added with default 0.05 (5%)
- [ ] Each corruption type has comment: `# Will fail: <expectation_name>`
- [ ] Corruption types map 1:1 to DLT expectations
- [ ] Parameter handling supports widgets, CLI, and defaults
- [ ] Job YAML includes `corruption_rate` parameter
- [ ] Documentation file created explaining all corruption types
- [ ] Realistic domain constants defined at module level
- [ ] Referential integrity maintained (facts reference valid dimensions)
- [ ] Print statements include corruption rate visibility

## Reference Files

- **[Faker Providers](references/faker-providers.md)** - Detailed provider examples, corruption patterns, dimension vs fact patterns, and complete implementation examples. Includes locale-specific providers, business-specific providers, and domain-specific constants.

- **[Generate Data Script](scripts/generate_data.py)** - Data generation utility with standard function signatures and parameter handling. Includes `generate_dimension_data()`, `generate_fact_data()`, `apply_corruption()`, and `get_parameters()` functions.

## References

- [Faker Documentation](https://faker.readthedocs.io/)
- [DLT Expectations](https://docs.databricks.com/aws/en/dlt/expectations)
