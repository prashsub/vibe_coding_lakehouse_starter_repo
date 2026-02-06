# Metric View Patterns and Examples

Complete examples of dimension patterns, measure patterns, joins, and snowflake schema patterns.

## Standard Dimension Patterns

### Geographic Dimensions
```yaml
dimensions:
  - name: store_number
    expr: source.store_number
    comment: Store identifier for location-based analysis
    display_name: Store Number
    synonyms: [store id, location number, store code]
  
  - name: city
    expr: dim_store.city
    comment: City where the location is situated
    display_name: City
    synonyms: [store city, location city]
```

### Product Dimensions
```yaml
dimensions:
  - name: upc_code
    expr: source.upc_code
    comment: Universal Product Code for product identification
    display_name: UPC Code
    synonyms: [product code, upc, barcode]
  
  - name: brand
    expr: dim_product.brand
    comment: Product brand name
    display_name: Brand
    synonyms: [product brand, manufacturer brand]
```

### Time Dimensions (from dim_date)
```yaml
dimensions:
  - name: year
    expr: dim_date.year
    comment: Calendar year for annual analysis
    display_name: Year
    synonyms: [calendar year, fiscal year]
  
  - name: month_name
    expr: dim_date.month_name
    comment: Month name for user-friendly reporting
    display_name: Month Name
    synonyms: [month]
  
  - name: is_weekend
    expr: dim_date.is_weekend
    comment: Weekend indicator for weekend vs weekday analysis
    display_name: Is Weekend
    synonyms: [weekend, weekend flag]
```

## Standard Measure Patterns

### Revenue Measures
```yaml
measures:
  - name: total_revenue
    expr: SUM(source.net_revenue)
    comment: Total net revenue after discounts and returns. Primary revenue metric.
    display_name: Total Revenue
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact
    synonyms: [revenue, sales, net revenue]
```

### Count Measures
```yaml
measures:
  - name: booking_count
    expr: COUNT(source.booking_id)  # ✅ Use primary key, not SUM(count_column)
    comment: Total number of transactions
    display_name: Booking Count
    format:
      type: number
      decimal_places:
        type: all
    synonyms: [bookings, transactions]
```

## Join Patterns

### SCD2 Dimension Join
```yaml
joins:
  - name: dim_store
    source: ${catalog}.${gold_schema}.dim_store
    'on': source.store_number = dim_store.store_number AND dim_store.is_current = true
```

### Multiple Dimension Joins
```yaml
joins:
  - name: dim_store
    source: ${catalog}.${gold_schema}.dim_store
    'on': source.store_number = dim_store.store_number AND dim_store.is_current = true
  
  - name: dim_product
    source: ${catalog}.${gold_schema}.dim_product
    'on': source.upc_code = dim_product.upc_code
```

## Snowflake Schema Joins (Nested Joins)

**Issue:** Direct joins fail when fact table doesn't have FK to needed dimension.

### ✅ CORRECT: Snowflake Schema (Nested Joins)

```yaml
source: ${catalog}.${gold_schema}.dim_host

joins:
  - name: dim_property
    source: ${catalog}.${gold_schema}.dim_property
    'on': source.host_id = dim_property.host_id AND dim_property.is_current = true
    joins:  # ✅ Nested join under dim_property
      - name: fact_booking
        source: ${catalog}.${gold_schema}.fact_booking_detail
        'on': dim_property.property_id = fact_booking.property_id
```

### Nested Column Reference Pattern

```yaml
measures:
  - name: total_revenue
    expr: SUM(dim_property.fact_booking.total_amount)  # parent.nested.column
```

## Transitive Join Solutions

### ✅ SOLUTION Option 1: Use Foreign Key Directly

```yaml
source: fact_property_engagement

joins:
  - name: dim_property
    source: catalog.schema.dim_property
    'on': source.property_id = dim_property.property_id

dimensions:
  - name: destination_id
    expr: dim_property.destination_id  # ✅ Use FK directly
```

### ✅ SOLUTION Option 2: Denormalize Fact Table

Add destination_id to fact table, then use direct join.

### ✅ SOLUTION Option 3: Create Enriched View

Create SQL view with all needed columns, then use as source.

## Synonym Best Practices

Provide **3-5 synonyms** per dimension/measure:

```yaml
synonyms:
  - <exact alternative name>
  - <business term variant>
  - <abbreviated form>
  - <common misspelling or alternative>
```

**Examples:**
- Revenue → `sales`, `net revenue`, `total sales`, `dollars`
- Store Number → `store id`, `location number`, `store code`
- Units → `quantity`, `volume`, `items sold`, `units sold`

## Professional Language Standards

**❌ Avoid:**
```yaml
comment: Use this because the TVF doesn't work correctly
```

**✅ Use:**
```yaml
comment: >
  Host demographics and verification analytics ONLY.
  → For revenue/booking queries, USE get_host_performance TVF (different join path).
```
