# Wanderbricks Genie Space Setup Guide

**Created:** December 2025  
**Status:** 📋 Ready for Deployment  
**Artifact Count:** 5 Genie Spaces  
**Reference:** [Genie Space Patterns](../../.cursor/rules/semantic-layer/16-genie-space-patterns.mdc)

---

## Overview

This document contains complete setup configurations for 5 Genie Spaces covering all business domains. Each space follows the **mandatory 7-section structure** required for production deployment.

| # | Genie Space | Domain | Tables | TVFs | Sample Questions |
|---|-------------|--------|--------|------|------------------|
| 1 | Revenue Intelligence | 💰 Revenue | 4 | 6 | 10 |
| 2 | Marketing Intelligence | 📊 Engagement | 3 | 5 | 10 |
| 3 | Property Intelligence | 🏠 Property | 4 | 5 | 10 |
| 4 | Host Intelligence | 👤 Host | 3 | 5 | 10 |
| 5 | Customer Intelligence | 🎯 Customer | 2 | 5 | 10 |

---

## ⚠️ Important: Sample Data Date Ranges

**The Wanderbricks sample data (`samples.wanderbricks.*`) has booking dates from historical periods (typically 2023-2024).** When testing TVFs, use appropriate date ranges:

```sql
-- For sample data testing, use wide historical date ranges:
SELECT * FROM ${catalog}.${gold_schema}.get_payment_metrics('2023-01-01', '2024-12-31');

-- NOT "last 90 days" which may return no data:
SELECT * FROM ${catalog}.${gold_schema}.get_payment_metrics(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),  -- ❌ May be outside sample data
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```

**To find valid date ranges in your data:**
```sql
SELECT MIN(check_in_date), MAX(check_in_date) FROM ${catalog}.${gold_schema}.fact_booking_detail;
```

---

## ⚠️ Important: Unity Catalog Namespace

**All table and function references must use the full 3-part Unity Catalog namespace:**
```
${catalog}.${gold_schema}.object_name
```

For example:
- **Tables:** `${catalog}.${gold_schema}.fact_booking_daily`
- **Metric Views:** `${catalog}.${gold_schema}.revenue_analytics_metrics`
- **TVFs:** `${catalog}.${gold_schema}.get_revenue_by_period(...)`

---

# 💰 1. Revenue Intelligence Genie Space

---

## A. Space Name

```
Space Name: Wanderbricks Revenue Intelligence
```

---

## B. Space Description

```
Description: Natural language interface for revenue, booking, and financial analytics.
Enables business analysts, finance teams, and executives to query revenue trends, 
booking volumes, cancellation patterns, and payment metrics without SQL.
Powered by revenue_analytics_metrics, fact_booking_daily, and 6 specialized TVFs.
```

---

## C. Sample Questions

### Revenue Questions
1. "What was total revenue last month?"
2. "Show me the top 10 properties by revenue"
3. "What is the revenue trend by week?"
4. "Compare monthly revenue Q3 vs Q4"

### Booking Questions
5. "How many bookings did we get this quarter?"
6. "What is our average booking value?"
7. "Which destinations generate the most revenue?"

### Performance Questions
8. "What is our cancellation rate?"
9. "Show payment completion rates by method"
10. "What was the revenue lost to cancellations?"

---

## D. Data Assets

### Metric Views (PRIMARY - Use First)
| Metric View Name | Full Path | Purpose | Key Measures |
|------------------|-----------|---------|--------------|
| `revenue_analytics_metrics` | `${catalog}.${gold_schema}.revenue_analytics_metrics` | Revenue and booking KPIs | total_revenue, booking_count, avg_booking_value, cancellation_rate |

### Fact Tables
| Table Name | Full Path | Purpose | Grain |
|------------|-----------|---------|-------|
| `fact_booking_daily` | `${catalog}.${gold_schema}.fact_booking_daily` | Daily aggregated booking metrics | One row per property-destination-date |
| `fact_booking_detail` | `${catalog}.${gold_schema}.fact_booking_detail` | Transaction-level booking data | One row per booking |

### Dimension Tables
| Table Name | Full Path | Purpose | Key Columns |
|------------|-----------|---------|-------------|
| `dim_property` | `${catalog}.${gold_schema}.dim_property` | Property listings | property_id, title, property_type, base_price |
| `dim_destination` | `${catalog}.${gold_schema}.dim_destination` | Geographic locations | destination_id, destination, country |
| `dim_date` | `${catalog}.${gold_schema}.dim_date` | Calendar lookups | date, year, quarter, month_name, is_weekend |

---

## E. General Instructions

```
You are an expert revenue analyst for Wanderbricks vacation rentals. Follow these rules:

1. **Primary Data:** Use ${catalog}.${gold_schema}.revenue_analytics_metrics metric view first
2. **Use TVFs:** For common queries, prefer Table-Valued Functions over raw SQL
3. **Date Defaults:** If no date specified, check available data range first. Sample data uses 2023-2024 dates.
4. **Aggregations:** Use SUM for totals, AVG for averages, COUNT for volumes
5. **Sorting:** Sort by revenue DESC unless user specifies otherwise
6. **Limits:** Return top 10 rows for ranking queries unless specified
7. **Currency:** Format as USD with $ and 2 decimal places ($1,234.56)
8. **Percentages:** Show rates as % with 1 decimal place (15.3%)
9. **Synonyms:** revenue = sales, income, earnings | bookings = reservations
10. **Context:** Always explain what the numbers mean in business terms
11. **Comparisons:** When comparing periods, show both absolute values and % difference
12. **Time Periods:** Support today, yesterday, last week, month, quarter, YTD
13. **Null Handling:** Exclude nulls from calculations
14. **Performance:** Never scan Bronze/Silver tables directly
15. **Accuracy:** If unsure about metric definition, state the assumption made
```

---

## F. Table-Valued Functions

| Function Name | Full Path | Signature | Purpose | When to Use |
|---------------|-----------|-----------|---------|-------------|
| `get_revenue_by_period` | `${catalog}.${gold_schema}.get_revenue_by_period` | `(start_date STRING, end_date STRING, time_grain STRING)` | Revenue by day/week/month/quarter | Period trends, seasonal analysis |
| `get_top_properties_by_revenue` | `${catalog}.${gold_schema}.get_top_properties_by_revenue` | `(start_date STRING, end_date STRING, top_n INT)` | Top N properties ranked by revenue | Property performance |
| `get_revenue_by_destination` | `${catalog}.${gold_schema}.get_revenue_by_destination` | `(start_date STRING, end_date STRING, top_n INT)` | Revenue breakdown by geography | Market analysis |
| `get_payment_metrics` | `${catalog}.${gold_schema}.get_payment_metrics` | `(start_date STRING, end_date STRING)` | Payment method performance | Payment optimization |
| `get_cancellation_analysis` | `${catalog}.${gold_schema}.get_cancellation_analysis` | `(start_date STRING, end_date STRING)` | Cancellation rates and lost revenue | Risk assessment |
| `get_revenue_forecast_inputs` | `${catalog}.${gold_schema}.get_revenue_forecast_inputs` | `(start_date STRING, end_date STRING, property_id BIGINT)` | ML forecasting data | Demand prediction |

### TVF Details

#### get_revenue_by_period
- **Full Path:** `${catalog}.${gold_schema}.get_revenue_by_period`
- **Signature:** `get_revenue_by_period(start_date STRING, end_date STRING, time_grain STRING DEFAULT 'day')`
- **Returns:** period_start, period_name, total_revenue, booking_count, avg_booking_value, cancellation_rate
- **Use When:** User asks about revenue trends, period comparisons, seasonal patterns
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_revenue_by_period('2024-10-01', '2024-12-31', 'month')`

#### get_top_properties_by_revenue
- **Full Path:** `${catalog}.${gold_schema}.get_top_properties_by_revenue`
- **Signature:** `get_top_properties_by_revenue(start_date STRING, end_date STRING, top_n INT DEFAULT 10)`
- **Returns:** rank, property_id, property_title, destination, total_revenue, booking_count
- **Use When:** User asks for best performing properties, top listings, revenue leaders
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_top_properties_by_revenue('2024-01-01', '2024-12-31', 10)`

#### get_revenue_by_destination
- **Full Path:** `${catalog}.${gold_schema}.get_revenue_by_destination`
- **Signature:** `get_revenue_by_destination(start_date STRING, end_date STRING, top_n INT DEFAULT 20)`
- **Returns:** rank, destination, country, total_revenue, booking_count, property_count
- **Use When:** User asks about geographic performance, market revenue, destination comparison
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_revenue_by_destination('2024-01-01', '2024-12-31', 10)`

---

## G. Benchmark Questions & Expected SQL

### Question 1: "What was total revenue last month?"
**Expected SQL:**
```sql
SELECT 
  period_name,
  total_revenue,
  booking_count,
  avg_booking_value
FROM ${catalog}.${gold_schema}.get_revenue_by_period(
  DATE_FORMAT(DATE_TRUNC('month', ADD_MONTHS(CURRENT_DATE, -1)), 'yyyy-MM-dd'),
  DATE_FORMAT(LAST_DAY(ADD_MONTHS(CURRENT_DATE, -1)), 'yyyy-MM-dd'),
  'month'
);
```
**Expected Result:** Single row showing last month's revenue, booking count, and average booking value

---

### Question 2: "Show me the top 10 properties by revenue"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_top_properties_by_revenue(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  10
);
```
**Expected Result:** 10 rows with property details ranked by total revenue

---

### Question 3: "What is the weekly revenue trend for Q4?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_revenue_by_period('2024-10-01', '2024-12-31', 'week')
ORDER BY period_start;
```
**Expected Result:** 13 rows (weeks in Q4) showing revenue per week

---

### Question 4: "Which destinations generate the most revenue?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_revenue_by_destination(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  10
);
```
**Expected Result:** Top 10 destinations ranked by total revenue

---

### Question 5: "What is our cancellation rate by destination?"
**Expected SQL:**
```sql
SELECT 
  destination,
  total_bookings,
  cancelled_bookings,
  cancellation_rate,
  lost_revenue
FROM ${catalog}.${gold_schema}.get_cancellation_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
ORDER BY cancellation_rate DESC;
```
**Expected Result:** Destinations sorted by cancellation rate with lost revenue

---

### Question 6: "Show payment completion rates"
**Expected SQL:**
```sql
SELECT 
  payment_method,
  booking_count,
  total_payment_amount,
  payment_completion_rate
FROM ${catalog}.${gold_schema}.get_payment_metrics('1900-01-01', '2100-12-31')
ORDER BY payment_completion_rate DESC;
```
**Expected Result:** Payment methods with completion rates and volume (all data)

---

### Question 7: "What is the average booking value?"
**Expected SQL:**
```sql
SELECT 
  MEASURE(avg_booking_value) as avg_booking_value,
  MEASURE(booking_count) as bookings,
  MEASURE(total_revenue) as revenue
FROM ${catalog}.${gold_schema}.revenue_analytics_metrics;
```
**Expected Result:** Single row with average booking value and context metrics

---

### Question 8: "Compare this month vs last month revenue"
**Expected SQL:**
```sql
WITH this_month AS (
  SELECT total_revenue, booking_count
  FROM ${catalog}.${gold_schema}.get_revenue_by_period(
    DATE_FORMAT(DATE_TRUNC('month', CURRENT_DATE), 'yyyy-MM-dd'),
    DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
    'month'
  )
),
last_month AS (
  SELECT total_revenue, booking_count
  FROM ${catalog}.${gold_schema}.get_revenue_by_period(
    DATE_FORMAT(DATE_TRUNC('month', ADD_MONTHS(CURRENT_DATE, -1)), 'yyyy-MM-dd'),
    DATE_FORMAT(LAST_DAY(ADD_MONTHS(CURRENT_DATE, -1)), 'yyyy-MM-dd'),
    'month'
  )
)
SELECT 
  tm.total_revenue as this_month_revenue,
  lm.total_revenue as last_month_revenue,
  ((tm.total_revenue - lm.total_revenue) / lm.total_revenue) * 100 as growth_pct
FROM this_month tm, last_month lm;
```
**Expected Result:** Revenue comparison with growth percentage

---

### Question 9: "Revenue by property type"
**Expected SQL:**
```sql
SELECT 
  property_type,
  MEASURE(total_revenue) as total_revenue,
  MEASURE(booking_count) as bookings,
  MEASURE(avg_booking_value) as avg_booking
FROM ${catalog}.${gold_schema}.revenue_analytics_metrics
GROUP BY property_type
ORDER BY total_revenue DESC;
```
**Expected Result:** Revenue breakdown by apartment, house, villa, etc.

---

### Question 10: "What percentage of revenue comes from each country?"
**Expected SQL:**
```sql
SELECT 
  country,
  MEASURE(total_revenue) as revenue,
  (MEASURE(total_revenue) * 100.0 / SUM(MEASURE(total_revenue)) OVER ()) as revenue_pct
FROM ${catalog}.${gold_schema}.revenue_analytics_metrics
GROUP BY country
ORDER BY revenue DESC;
```
**Expected Result:** Countries with revenue amount and percentage share

---

# 📊 2. Marketing Intelligence Genie Space

---

## A. Space Name

```
Space Name: Wanderbricks Marketing Intelligence
```

---

## B. Space Description

```
Description: Natural language interface for engagement, conversion, and marketing analytics.
Enables marketing teams and product managers to analyze property views, click-through rates,
conversion funnels, and engagement patterns without SQL.
Powered by engagement_analytics_metrics, fact_property_engagement, and 5 specialized TVFs.
```

---

## C. Sample Questions

### Engagement Questions
1. "What is our overall conversion rate?"
2. "Which properties have the highest engagement?"
3. "Show the view-to-booking funnel"
4. "What is the click-through rate by property type?"

### Traffic Questions
5. "How many property views last week?"
6. "Which destinations have most engagement?"
7. "Compare mobile vs desktop conversion"

### Trend Questions
8. "Show daily engagement trends"
9. "What are weekly engagement patterns?"
10. "Which properties are underperforming on conversion?"

---

## D. Data Assets

### Metric Views (PRIMARY - Use First)
| Metric View Name | Full Path | Purpose | Key Measures |
|------------------|-----------|---------|--------------|
| `engagement_analytics_metrics` | `${catalog}.${gold_schema}.engagement_analytics_metrics` | Engagement and conversion KPIs | total_views, total_clicks, avg_conversion_rate, click_through_rate |

### Fact Tables
| Table Name | Full Path | Purpose | Grain |
|------------|-----------|---------|-------|
| `fact_property_engagement` | `${catalog}.${gold_schema}.fact_property_engagement` | Daily property engagement metrics | One row per property-date |

### Dimension Tables
| Table Name | Full Path | Purpose | Key Columns |
|------------|-----------|---------|-------------|
| `dim_property` | `${catalog}.${gold_schema}.dim_property` | Property listings | property_id, title, property_type |
| `dim_date` | `${catalog}.${gold_schema}.dim_date` | Calendar lookups | date, year, month_name, is_weekend |

---

## E. General Instructions

```
You are an expert marketing analyst for Wanderbricks vacation rentals. Follow these rules:

1. **Primary Data:** Use ${catalog}.${gold_schema}.engagement_analytics_metrics metric view first
2. **Use TVFs:** For funnel analysis, use get_conversion_funnel TVF
3. **Date Defaults:** If no date specified, default to last 30 days
4. **Rates:** Always express conversion rates and CTR as percentages
5. **Benchmarks:** Compare against platform average when available
6. **Sorting:** Sort by conversion rate or engagement score DESC
7. **Limits:** Return top 10 for ranking queries unless specified
8. **Funnel Format:** Show view → click → booking with drop-off rates
9. **Synonyms:** views = impressions | clicks = interactions | conversion = booking rate
10. **Context:** Identify low-performing properties proactively
11. **Optimization:** Suggest improvements when engagement is below benchmark
12. **Time Periods:** Support daily, weekly trends for seasonality
13. **Null Handling:** Exclude properties with zero views
14. **Performance:** Never scan Bronze/Silver tables directly
15. **Accuracy:** If data seems anomalous, note potential data quality issues
```

---

## F. Table-Valued Functions

| Function Name | Full Path | Signature | Purpose | When to Use |
|---------------|-----------|-----------|---------|-------------|
| `get_property_engagement` | `${catalog}.${gold_schema}.get_property_engagement` | `(start_date STRING, end_date STRING, property_id BIGINT)` | Property engagement metrics | Property performance |
| `get_conversion_funnel` | `${catalog}.${gold_schema}.get_conversion_funnel` | `(start_date STRING, end_date STRING, destination STRING)` | View → Click → Book funnel | Funnel analysis |
| `get_traffic_source_analysis` | `${catalog}.${gold_schema}.get_traffic_source_analysis` | `(start_date STRING, end_date STRING)` | Traffic by property type | Channel optimization |
| `get_engagement_trends` | `${catalog}.${gold_schema}.get_engagement_trends` | `(start_date STRING, end_date STRING, time_grain STRING)` | Daily/weekly engagement | Trend analysis |
| `get_top_engaging_properties` | `${catalog}.${gold_schema}.get_top_engaging_properties` | `(start_date STRING, end_date STRING, top_n INT)` | Top properties by engagement | Best performers |

### TVF Details

#### get_conversion_funnel
- **Full Path:** `${catalog}.${gold_schema}.get_conversion_funnel`
- **Signature:** `get_conversion_funnel(start_date STRING, end_date STRING, destination_filter STRING DEFAULT NULL)`
- **Returns:** destination, total_views, total_clicks, total_bookings, view_to_click_rate, click_to_booking_rate
- **Use When:** User asks about funnel, conversion stages, drop-off analysis
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_conversion_funnel('2024-10-01', '2024-12-31', NULL)`

#### get_property_engagement
- **Full Path:** `${catalog}.${gold_schema}.get_property_engagement`
- **Signature:** `get_property_engagement(start_date STRING, end_date STRING, property_id_filter BIGINT DEFAULT NULL)`
- **Returns:** property_id, property_title, total_views, unique_viewers, total_clicks, conversion_rate
- **Use When:** User asks about specific property engagement, property comparison
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_property_engagement('2024-10-01', '2024-12-31', NULL)`

---

## G. Benchmark Questions & Expected SQL

### Question 1: "What is our conversion rate?"
**Expected SQL:**
```sql
SELECT 
  MEASURE(avg_conversion_rate) as conversion_rate,
  MEASURE(total_views) as views,
  MEASURE(total_clicks) as clicks
FROM ${catalog}.${gold_schema}.engagement_analytics_metrics;
```
**Expected Result:** Overall conversion rate with supporting metrics

---

### Question 2: "Show the view-to-booking funnel"
**Expected SQL:**
```sql
SELECT 
  destination,
  total_views,
  total_clicks,
  total_bookings,
  view_to_click_rate,
  click_to_booking_rate,
  overall_conversion_rate
FROM ${catalog}.${gold_schema}.get_conversion_funnel(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -30), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
ORDER BY overall_conversion_rate DESC;
```
**Expected Result:** Funnel metrics by destination with stage drop-off rates

---

### Question 3: "Which properties have highest engagement?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_top_engaging_properties(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -30), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  10
);
```
**Expected Result:** Top 10 properties ranked by engagement score

---

### Question 4: "What is click-through rate by property type?"
**Expected SQL:**
```sql
SELECT 
  property_type,
  MEASURE(total_views) as views,
  MEASURE(total_clicks) as clicks,
  MEASURE(click_through_rate) as ctr
FROM ${catalog}.${gold_schema}.engagement_analytics_metrics
GROUP BY property_type
ORDER BY ctr DESC;
```
**Expected Result:** CTR breakdown by property type

---

### Question 5: "Show daily engagement trends"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_engagement_trends(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -30), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  'day'
)
ORDER BY period_start;
```
**Expected Result:** Daily view, click, and conversion trends

---

### Question 6: "Which destinations have best conversion?"
**Expected SQL:**
```sql
SELECT 
  destination,
  total_views,
  overall_conversion_rate,
  funnel_efficiency
FROM ${catalog}.${gold_schema}.get_conversion_funnel(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -30), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
ORDER BY overall_conversion_rate DESC
LIMIT 10;
```
**Expected Result:** Top 10 destinations by conversion rate

---

### Question 7: "Performance by property type"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_traffic_source_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -30), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```
**Expected Result:** Engagement metrics broken down by property type

---

### Question 8: "Average time on page by property"
**Expected SQL:**
```sql
SELECT 
  property_title,
  total_views,
  avg_time_on_page,
  conversion_rate
FROM ${catalog}.${gold_schema}.get_property_engagement(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -30), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
WHERE total_views > 100
ORDER BY avg_time_on_page DESC
LIMIT 10;
```
**Expected Result:** Properties ranked by time on page

---

### Question 9: "Weekly engagement patterns"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_engagement_trends(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  'week'
)
ORDER BY period_start;
```
**Expected Result:** Weekly engagement trends for seasonality analysis

---

### Question 10: "Properties with low conversion but high views"
**Expected SQL:**
```sql
SELECT 
  property_title,
  total_views,
  conversion_rate,
  engagement_score
FROM ${catalog}.${gold_schema}.get_property_engagement(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -30), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
WHERE total_views > 1000 AND conversion_rate < 2.0
ORDER BY total_views DESC
LIMIT 10;
```
**Expected Result:** High-traffic properties needing optimization

---

# 🏠 3. Property Intelligence Genie Space

---

## A. Space Name

```
Space Name: Wanderbricks Property Intelligence
```

---

## B. Space Description

```
Description: Natural language interface for property portfolio and inventory analytics.
Enables property managers, portfolio analysts, and operations teams to analyze property
performance, pricing strategies, inventory utilization, and amenity impact without SQL.
Powered by property_analytics_metrics, dim_property, and 5 specialized TVFs.
```

---

## C. Sample Questions

### Portfolio Questions
1. "How many properties do we have?"
2. "Show properties by destination"
3. "What is our total inventory capacity?"
4. "Property distribution by type"

### Pricing Questions
5. "What is the average price by destination?"
6. "Show the price range for apartments"
7. "Which price points perform best?"

### Performance Questions
8. "Which properties are underperforming?"
9. "Compare house vs apartment performance"
10. "What amenity configurations perform best?"

---

## D. Data Assets

### Metric Views (PRIMARY - Use First)
| Metric View Name | Full Path | Purpose | Key Measures |
|------------------|-----------|---------|--------------|
| `property_analytics_metrics` | `${catalog}.${gold_schema}.property_analytics_metrics` | Property portfolio KPIs | property_count, avg_base_price, revenue_per_property |

### Dimension Tables
| Table Name | Full Path | Purpose | Key Columns |
|------------|-----------|---------|-------------|
| `dim_property` | `${catalog}.${gold_schema}.dim_property` | Property master data | property_id, title, type, base_price, bedrooms |
| `dim_destination` | `${catalog}.${gold_schema}.dim_destination` | Geographic locations | destination_id, destination, country |
| `dim_host` | `${catalog}.${gold_schema}.dim_host` | Host information | host_id, name, is_verified |

### Fact Tables
| Table Name | Full Path | Purpose | Grain |
|------------|-----------|---------|-------|
| `fact_booking_daily` | `${catalog}.${gold_schema}.fact_booking_daily` | Daily booking metrics | One row per property-destination-date |

---

## E. General Instructions

```
You are an expert property portfolio analyst for Wanderbricks. Follow these rules:

1. **Primary Data:** Use ${catalog}.${gold_schema}.property_analytics_metrics metric view first
2. **Use TVFs:** For property KPIs, use get_property_performance TVF
3. **Date Defaults:** Focus on current active listings unless specified
4. **Pricing:** Include destination and type context for price analysis
5. **Comparisons:** Compare against market/portfolio averages
6. **Sorting:** Sort by revenue or occupancy rate DESC
7. **Limits:** Return top 10 for ranking queries unless specified
8. **Capacity:** Include max_guests and bedroom count for inventory queries
9. **Synonyms:** properties = listings | price = rate | capacity = max guests
10. **Context:** Include property type and destination context
11. **Underperformers:** Flag properties below 50% of average performance
12. **Pricing Insights:** Recommend optimal price ranges when asked
13. **Null Handling:** Use COALESCE(base_price, 0) for price calculations
14. **Performance:** Never scan Bronze/Silver tables directly
15. **Accuracy:** Note if sample size is small for statistical conclusions
```

---

## F. Table-Valued Functions

| Function Name | Full Path | Signature | Purpose | When to Use |
|---------------|-----------|-----------|---------|-------------|
| `get_property_performance` | `${catalog}.${gold_schema}.get_property_performance` | `(start_date STRING, end_date STRING, destination STRING)` | Property KPIs | Property analysis |
| `get_availability_by_destination` | `${catalog}.${gold_schema}.get_availability_by_destination` | `(start_date STRING, end_date STRING, top_n INT)` | Inventory by market | Capacity planning |
| `get_property_type_analysis` | `${catalog}.${gold_schema}.get_property_type_analysis` | `(start_date STRING, end_date STRING)` | Performance by type | Type comparison |
| `get_amenity_impact` | `${catalog}.${gold_schema}.get_amenity_impact` | `(start_date STRING, end_date STRING)` | Amenity correlation | Optimization |
| `get_pricing_analysis` | `${catalog}.${gold_schema}.get_pricing_analysis` | `(start_date STRING, end_date STRING)` | Price point performance | Pricing strategy |

### TVF Details

#### get_property_performance
- **Full Path:** `${catalog}.${gold_schema}.get_property_performance`
- **Signature:** `get_property_performance(start_date STRING, end_date STRING, destination_filter STRING DEFAULT NULL)`
- **Returns:** property_id, property_title, property_type, destination, total_revenue, avg_occupancy_rate
- **Use When:** User asks about property KPIs, performance comparison, underperformers
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_property_performance('2024-10-01', '2024-12-31', NULL)`

#### get_pricing_analysis
- **Full Path:** `${catalog}.${gold_schema}.get_pricing_analysis`
- **Signature:** `get_pricing_analysis(start_date STRING, end_date STRING)`
- **Returns:** price_bucket, property_count, total_revenue, avg_occupancy_rate, price_efficiency_score
- **Use When:** User asks about pricing strategy, optimal price points, price elasticity
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_pricing_analysis('2024-10-01', '2024-12-31')`

---

## G. Benchmark Questions & Expected SQL

### Question 1: "How many properties do we have?"
**Expected SQL:**
```sql
SELECT 
  MEASURE(property_count) as total_properties,
  MEASURE(total_capacity) as total_capacity
FROM ${catalog}.${gold_schema}.property_analytics_metrics;
```
**Expected Result:** Total property count and guest capacity

---

### Question 2: "Show property inventory by destination"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_availability_by_destination(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  20
);
```
**Expected Result:** Top 20 destinations with property counts and metrics

---

### Question 3: "What is the average price by destination?"
**Expected SQL:**
```sql
SELECT 
  destination,
  MEASURE(avg_base_price) as avg_price,
  MEASURE(property_count) as properties
FROM ${catalog}.${gold_schema}.property_analytics_metrics
GROUP BY destination
ORDER BY avg_price DESC;
```
**Expected Result:** Destinations ranked by average nightly rate

---

### Question 4: "Performance by property type"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_property_type_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```
**Expected Result:** Revenue, bookings, occupancy by property type

---

### Question 5: "Which properties are underperforming?"
**Expected SQL:**
```sql
SELECT 
  property_title,
  destination,
  total_revenue,
  avg_occupancy_rate,
  property_score
FROM ${catalog}.${gold_schema}.get_property_performance(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
WHERE avg_occupancy_rate < 30 OR total_revenue < 1000
ORDER BY property_score ASC
LIMIT 20;
```
**Expected Result:** Low-performing properties for optimization focus

---

### Question 6: "What amenity configurations perform best?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_amenity_impact(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
ORDER BY performance_score DESC
LIMIT 10;
```
**Expected Result:** Bedroom/bathroom configs ranked by performance

---

### Question 7: "What is the optimal price range?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_pricing_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
ORDER BY price_efficiency_score DESC;
```
**Expected Result:** Price buckets with efficiency scores

---

### Question 8: "Compare house vs apartment"
**Expected SQL:**
```sql
SELECT 
  property_type,
  property_count,
  total_revenue,
  avg_booking_value,
  avg_occupancy_rate,
  market_share_revenue
FROM ${catalog}.${gold_schema}.get_property_type_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
WHERE property_type IN ('House', 'Apartment');
```
**Expected Result:** Side-by-side comparison of house vs apartment metrics

---

### Question 9: "Properties in Paris"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_property_performance(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  'Paris%'
)
ORDER BY total_revenue DESC;
```
**Expected Result:** All Paris properties with performance metrics

---

### Question 10: "Total revenue per property"
**Expected SQL:**
```sql
SELECT 
  property_type,
  MEASURE(revenue_per_property) as revenue_per_property,
  MEASURE(bookings_per_property) as bookings_per_property
FROM ${catalog}.${gold_schema}.property_analytics_metrics
GROUP BY property_type
ORDER BY revenue_per_property DESC;
```
**Expected Result:** Revenue efficiency by property type

---

# 👤 4. Host Intelligence Genie Space

---

## A. Space Name

```
Space Name: Wanderbricks Host Intelligence
```

---

## B. Space Description

```
Description: Natural language interface for host performance and partner management analytics.
Enables partner success teams and account managers to analyze host quality, verification impact,
retention trends, and portfolio performance without SQL.
Powered by host_analytics_metrics, dim_host, and 5 specialized TVFs.
```

---

## C. Sample Questions

### Performance Questions
1. "Who are our top performing hosts?"
2. "What is the average host rating?"
3. "Show hosts by revenue"
4. "Host performance metrics"

### Quality Questions
5. "How many verified hosts do we have?"
6. "Impact of verification on performance"
7. "Top quality hosts"

### Retention Questions
8. "Active vs inactive hosts"
9. "Host churn analysis"
10. "Multi-property hosts"

---

## D. Data Assets

### Metric Views (PRIMARY - Use First)
| Metric View Name | Full Path | Purpose | Key Measures |
|------------------|-----------|---------|--------------|
| `host_analytics_metrics` | `${catalog}.${gold_schema}.host_analytics_metrics` | Host performance KPIs | host_count, avg_rating, verification_rate, revenue_per_host |

### Dimension Tables
| Table Name | Full Path | Purpose | Key Columns |
|------------|-----------|---------|-------------|
| `dim_host` | `${catalog}.${gold_schema}.dim_host` | Host master data | host_id, name, is_verified, rating, country |
| `dim_property` | `${catalog}.${gold_schema}.dim_property` | Property-host relationship | property_id, host_id, title |

### Fact Tables
| Table Name | Full Path | Purpose | Grain |
|------------|-----------|---------|-------|
| `fact_booking_detail` | `${catalog}.${gold_schema}.fact_booking_detail` | Booking transactions | One row per booking |

---

## E. General Instructions

```
You are an expert host analytics specialist for Wanderbricks. Follow these rules:

1. **Primary Data:** Use ${catalog}.${gold_schema}.host_analytics_metrics metric view first
2. **Use TVFs:** For host KPIs, use get_host_performance TVF
3. **Date Defaults:** Default to last 90 days for performance metrics
4. **Verification:** Highlight verification status impact on performance
5. **Comparisons:** Compare verified vs non-verified hosts
6. **Sorting:** Sort by revenue or quality score DESC
7. **Limits:** Return top 20 hosts for ranking queries unless specified
8. **Quality Focus:** Include rating, response rate, cancellation rate
9. **Synonyms:** hosts = partners, owners | verified = trusted | churn = inactive
10. **Context:** Explain host quality factors in business terms
11. **At-risk:** Flag hosts with declining metrics or inactivity
12. **Multi-property:** Identify professional hosts with 3+ properties
13. **Null Handling:** Exclude hosts with no activity in period
14. **Performance:** Never scan Bronze/Silver tables directly
15. **Accuracy:** Note small sample sizes affecting statistical validity
```

---

## F. Table-Valued Functions

| Function Name | Full Path | Signature | Purpose | When to Use |
|---------------|-----------|-----------|---------|-------------|
| `get_host_performance` | `${catalog}.${gold_schema}.get_host_performance` | `(start_date STRING, end_date STRING, host_id BIGINT)` | Host KPIs | Performance analysis |
| `get_host_quality_metrics` | `${catalog}.${gold_schema}.get_host_quality_metrics` | `(start_date STRING, end_date STRING, top_n INT)` | Top hosts by quality | Quality assessment |
| `get_host_retention_analysis` | `${catalog}.${gold_schema}.get_host_retention_analysis` | `(start_date STRING, end_date STRING)` | Active vs churned | Retention tracking |
| `get_host_geographic_distribution` | `${catalog}.${gold_schema}.get_host_geographic_distribution` | `(start_date STRING, end_date STRING, top_n INT)` | Hosts by country | Geographic analysis |
| `get_multi_property_hosts` | `${catalog}.${gold_schema}.get_multi_property_hosts` | `(start_date STRING, end_date STRING, min_properties INT)` | Professional hosts | Portfolio analysis |

### TVF Details

#### get_host_performance
- **Full Path:** `${catalog}.${gold_schema}.get_host_performance`
- **Signature:** `get_host_performance(start_date STRING, end_date STRING, host_id_filter BIGINT DEFAULT NULL)`
- **Returns:** host_id, host_name, is_verified, rating, property_count, total_revenue, host_performance_score
- **Use When:** User asks about host KPIs, top performers, host comparison
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_host_performance('2024-10-01', '2024-12-31', NULL)`

#### get_host_quality_metrics
- **Full Path:** `${catalog}.${gold_schema}.get_host_quality_metrics`
- **Signature:** `get_host_quality_metrics(start_date STRING, end_date STRING, top_n INT DEFAULT 20)`
- **Returns:** rank, host_name, is_verified, rating, response_rate, quality_score
- **Use When:** User asks about best hosts, quality assessment, certification
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_host_quality_metrics('2024-10-01', '2024-12-31', 10)`

---

## G. Benchmark Questions & Expected SQL

### Question 1: "Who are our top performing hosts?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_host_performance(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
ORDER BY host_performance_score DESC
LIMIT 10;
```
**Expected Result:** Top 10 hosts ranked by composite performance score

---

### Question 2: "What is the average host rating?"
**Expected SQL:**
```sql
SELECT 
  MEASURE(avg_rating) as avg_rating,
  MEASURE(host_count) as total_hosts
FROM ${catalog}.${gold_schema}.host_analytics_metrics;
```
**Expected Result:** Platform-wide average rating and host count

---

### Question 3: "How many verified hosts do we have?"
**Expected SQL:**
```sql
SELECT 
  MEASURE(verified_count) as verified_count,
  MEASURE(host_count) as total_hosts,
  MEASURE(verification_rate) as verification_rate
FROM ${catalog}.${gold_schema}.host_analytics_metrics;
```
**Expected Result:** Verified host count and percentage

---

### Question 4: "Impact of verification on performance"
**Expected SQL:**
```sql
SELECT 
  is_verified,
  COUNT(DISTINCT host_id) as host_count,
  SUM(total_revenue) as total_revenue,
  AVG(rating) as avg_rating,
  AVG(host_performance_score) as avg_score
FROM ${catalog}.${gold_schema}.get_host_performance(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
GROUP BY is_verified;
```
**Expected Result:** Verified vs non-verified comparison

---

### Question 5: "Host distribution by country"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_host_geographic_distribution(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  15
);
```
**Expected Result:** Top 15 countries by host count

---

### Question 6: "Active vs inactive hosts"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_host_retention_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```
**Expected Result:** Host status breakdown (active with bookings, active without, churned)

---

### Question 7: "Top quality hosts"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_host_quality_metrics(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  10
);
```
**Expected Result:** Top 10 hosts ranked by quality score

---

### Question 8: "Multi-property hosts"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_multi_property_hosts(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  3
)
ORDER BY portfolio_performance_score DESC;
```
**Expected Result:** Hosts with 3+ properties ranked by performance

---

### Question 9: "Host revenue distribution"
**Expected SQL:**
```sql
SELECT 
  host_name,
  property_count,
  total_revenue,
  avg_booking_value,
  host_performance_score
FROM ${catalog}.${gold_schema}.get_host_performance(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
ORDER BY total_revenue DESC
LIMIT 20;
```
**Expected Result:** Top 20 hosts by revenue

---

### Question 10: "At-risk hosts"
**Expected SQL:**
```sql
SELECT 
  host_status,
  host_count,
  total_revenue,
  avg_rating
FROM ${catalog}.${gold_schema}.get_host_retention_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
WHERE host_status != 'Active with Bookings';
```
**Expected Result:** Hosts at risk of churning (inactive or no bookings)

---

# 🎯 5. Customer Intelligence Genie Space

---

## A. Space Name

```
Space Name: Wanderbricks Customer Intelligence
```

---

## B. Space Description

```
Description: Natural language interface for customer behavior and segmentation analytics.
Enables marketing teams, customer success, and growth teams to analyze customer segments,
lifetime value, booking frequency, and business vs leisure patterns without SQL.
Powered by customer_analytics_metrics, dim_user, and 5 specialized TVFs.
```

---

## C. Sample Questions

### Segmentation Questions
1. "What are our customer segments?"
2. "Show segment performance"
3. "How many VIP customers do we have?"
4. "Customer distribution by segment"

### Value Questions
5. "Who are our most valuable customers?"
6. "What is average customer lifetime value?"
7. "Top customers by spend"

### Behavior Questions
8. "How often do customers book?"
9. "Business vs leisure breakdown"
10. "Customers by country"

---

## D. Data Assets

### Metric Views (PRIMARY - Use First)
| Metric View Name | Full Path | Purpose | Key Measures |
|------------------|-----------|---------|--------------|
| `customer_analytics_metrics` | `${catalog}.${gold_schema}.customer_analytics_metrics` | Customer behavior KPIs | customer_count, spend_per_customer, bookings_per_customer |

### Dimension Tables
| Table Name | Full Path | Purpose | Key Columns |
|------------|-----------|---------|-------------|
| `dim_user` | `${catalog}.${gold_schema}.dim_user` | Customer master data | user_id, country, user_type, is_business |

### Fact Tables
| Table Name | Full Path | Purpose | Grain |
|------------|-----------|---------|-------|
| `fact_booking_detail` | `${catalog}.${gold_schema}.fact_booking_detail` | Booking transactions | One row per booking |

---

## E. General Instructions

```
You are an expert customer analytics specialist for Wanderbricks. Follow these rules:

1. **Primary Data:** Use ${catalog}.${gold_schema}.customer_analytics_metrics metric view first
2. **Use TVFs:** For segmentation, use get_customer_segments TVF
3. **Date Defaults:** Default to last 12 months for LTV calculations
4. **Segments:** Use standard segments (VIP, Frequent, Repeat, One-time, Inactive)
5. **LTV:** Calculate using total spend / customer count
6. **Sorting:** Sort by lifetime_value or revenue DESC
7. **Limits:** Return top 100 customers for LTV queries unless specified
8. **B2B Focus:** Highlight business customers separately
9. **Synonyms:** customers = guests, users | LTV = lifetime value | segments = cohorts
10. **Context:** Explain segment definitions and business implications
11. **High-value:** Identify customers with LTV > 2x average
12. **Frequency:** Categorize by booking frequency (1, 2-3, 4-6, 7+)
13. **Null Handling:** Exclude users with no bookings from LTV calculations
14. **Performance:** Never scan Bronze/Silver tables directly
15. **Accuracy:** Note recency of data for segment classifications
```

---

## F. Table-Valued Functions

| Function Name | Full Path | Signature | Purpose | When to Use |
|---------------|-----------|-----------|---------|-------------|
| `get_customer_segments` | `${catalog}.${gold_schema}.get_customer_segments` | `(start_date STRING, end_date STRING)` | Segment distribution | Segmentation analysis |
| `get_customer_ltv` | `${catalog}.${gold_schema}.get_customer_ltv` | `(start_date STRING, end_date STRING, top_n INT)` | Top customers by LTV | Value analysis |
| `get_booking_frequency_analysis` | `${catalog}.${gold_schema}.get_booking_frequency_analysis` | `(start_date STRING, end_date STRING)` | Frequency distribution | Behavior patterns |
| `get_customer_geographic_analysis` | `${catalog}.${gold_schema}.get_customer_geographic_analysis` | `(start_date STRING, end_date STRING, top_n INT)` | Customers by country | Geographic analysis |
| `get_business_vs_leisure_analysis` | `${catalog}.${gold_schema}.get_business_vs_leisure_analysis` | `(start_date STRING, end_date STRING)` | B2B vs B2C comparison | Segment comparison |

### TVF Details

#### get_customer_segments
- **Full Path:** `${catalog}.${gold_schema}.get_customer_segments`
- **Signature:** `get_customer_segments(start_date STRING, end_date STRING)`
- **Returns:** segment_name, customer_count, total_bookings, total_revenue, segment_revenue_share
- **Use When:** User asks about customer segments, cohorts, customer distribution
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_customer_segments('2024-01-01', '2024-12-31')`

#### get_customer_ltv
- **Full Path:** `${catalog}.${gold_schema}.get_customer_ltv`
- **Signature:** `get_customer_ltv(start_date STRING, end_date STRING, top_n INT DEFAULT 100)`
- **Returns:** rank, user_id, country, lifetime_value, total_bookings, avg_booking_value
- **Use When:** User asks about top customers, LTV analysis, valuable customers
- **Example:** `SELECT * FROM ${catalog}.${gold_schema}.get_customer_ltv('2024-01-01', '2024-12-31', 50)`

---

## G. Benchmark Questions & Expected SQL

### Question 1: "What are our customer segments?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_customer_segments(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -365), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```
**Expected Result:** Segment breakdown (VIP, Frequent, Repeat, One-time, Inactive)

---

### Question 2: "Who are our most valuable customers?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_customer_ltv(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -365), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  20
);
```
**Expected Result:** Top 20 customers ranked by lifetime value

---

### Question 3: "How often do customers book?"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_booking_frequency_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -365), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```
**Expected Result:** Frequency distribution (1, 2-3, 4-6, 7+ bookings)

---

### Question 4: "Business vs leisure breakdown"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_business_vs_leisure_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```
**Expected Result:** Business vs Leisure comparison metrics

---

### Question 5: "Customers by country"
**Expected SQL:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.get_customer_geographic_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -365), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  15
);
```
**Expected Result:** Top 15 countries by customer count

---

### Question 6: "Average customer lifetime value"
**Expected SQL:**
```sql
SELECT 
  MEASURE(spend_per_customer) as avg_ltv,
  MEASURE(customer_count) as total_customers,
  MEASURE(total_spend) as total_revenue
FROM ${catalog}.${gold_schema}.customer_analytics_metrics;
```
**Expected Result:** Platform-wide average LTV with context

---

### Question 7: "VIP customer count and revenue"
**Expected SQL:**
```sql
SELECT 
  segment_name,
  customer_count,
  total_revenue,
  segment_revenue_share
FROM ${catalog}.${gold_schema}.get_customer_segments(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -365), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
WHERE segment_name = 'VIP Customer';
```
**Expected Result:** VIP segment metrics

---

### Question 8: "Repeat customer percentage"
**Expected SQL:**
```sql
SELECT 
  booking_frequency_bucket,
  customer_count,
  customer_percentage,
  revenue_percentage
FROM ${catalog}.${gold_schema}.get_booking_frequency_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -365), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
WHERE booking_frequency_bucket IN ('2-3 Bookings', '4-6 Bookings', '7+ Bookings');
```
**Expected Result:** Repeat customer breakdown

---

### Question 9: "Business customer metrics"
**Expected SQL:**
```sql
SELECT 
  booking_type,
  customer_count,
  total_revenue,
  avg_booking_value,
  avg_nights_booked
FROM ${catalog}.${gold_schema}.get_business_vs_leisure_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -365), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
WHERE booking_type = 'Business';
```
**Expected Result:** Business customer specific metrics

---

### Question 10: "Customer segment revenue share"
**Expected SQL:**
```sql
SELECT 
  segment_name,
  customer_count,
  total_revenue,
  segment_revenue_share,
  avg_booking_value
FROM ${catalog}.${gold_schema}.get_customer_segments(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -365), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
ORDER BY segment_revenue_share DESC;
```
**Expected Result:** Segments ranked by revenue contribution

---

# ✅ Deployment Checklist

## Pre-Deployment Validation

| Space | A. Name | B. Desc | C. Questions | D. Assets | E. Instructions | F. TVFs | G. SQL |
|-------|---------|---------|--------------|-----------|-----------------|---------|--------|
| Revenue Intelligence | ✅ | ✅ | ✅ (10) | ✅ (4) | ✅ (15 lines) | ✅ (6) | ✅ (10) |
| Marketing Intelligence | ✅ | ✅ | ✅ (10) | ✅ (3) | ✅ (15 lines) | ✅ (5) | ✅ (10) |
| Property Intelligence | ✅ | ✅ | ✅ (10) | ✅ (4) | ✅ (15 lines) | ✅ (5) | ✅ (10) |
| Host Intelligence | ✅ | ✅ | ✅ (10) | ✅ (3) | ✅ (15 lines) | ✅ (5) | ✅ (10) |
| Customer Intelligence | ✅ | ✅ | ✅ (10) | ✅ (2) | ✅ (15 lines) | ✅ (5) | ✅ (10) |

## Deployment Steps

### 1. Create Genie Spaces (UI)

```
For each space:
1. Navigate to: Databricks Workspace → Genie → Create New Space
2. Enter Space Name (from Section A)
3. Enter Description (from Section B)
4. Select Serverless SQL Warehouse
5. Add Sample Questions (from Section C)
```

### 2. Add Trusted Assets

```
For each space:
1. Click "Add Trusted Assets"
2. Add Metric Views first (from Section D)
3. Add TVFs (from Section F)
4. Add dimension tables (from Section D)
5. Verify all assets are accessible
```

### 3. Configure Agent Instructions

```
For each space:
1. Open Space Settings
2. Paste General Instructions (from Section E)
3. Ensure ≤20 lines
```

### 4. Test Benchmark Questions

```
For each space:
1. Test all 10 benchmark questions (Section G)
2. Compare generated SQL to expected SQL
3. Verify results match expected output
4. Document any discrepancies
5. Refine instructions if needed
```

### 5. Grant Permissions

```sql
-- Grant access to user groups
GRANT USE SCHEMA ON ${catalog}.${gold_schema} TO data_analysts;
GRANT SELECT ON TABLE ${catalog}.${gold_schema}.* TO data_analysts;
GRANT EXECUTE ON FUNCTION ${catalog}.${gold_schema}.* TO data_analysts;
```

---

## References

- [Genie Spaces Documentation](https://docs.databricks.com/genie/)
- [Trusted Assets](https://docs.databricks.com/genie/trusted-assets.html)
- [Genie Space Patterns Rule](../../.cursor/rules/semantic-layer/16-genie-space-patterns.mdc)
- [Metric Views Guide](../deployment/metric-views-deployment-guide.md)
- [TVF Implementation](../../src/wanderbricks_gold/tvfs/)


