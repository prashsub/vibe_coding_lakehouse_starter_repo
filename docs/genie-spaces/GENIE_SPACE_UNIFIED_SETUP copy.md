# Wanderbricks Unified Genie Space Setup Guide

**Created:** December 2025  
**Status:** 📋 Ready for Deployment  
**Artifact Count:** 1 Unified Genie Space  
**Reference:** [Genie Space Patterns](../../.cursor/rules/semantic-layer/16-genie-space-patterns.mdc)

---

## Overview

This document configures a **single unified Genie Space** that provides natural language access to ALL business domains. This approach offers:

✅ **Cross-domain queries** - Ask questions spanning revenue, marketing, property, host, and customer data  
✅ **Single point of access** - Users don't switch between spaces  
✅ **Unified context** - Genie understands relationships across domains  
✅ **Simpler administration** - One space to manage

| Component | Count |
|-----------|-------|
| Metric Views | 5 |
| Table-Valued Functions | 33 (26 analytics + 7 ML) |
| ML Inference Tables | 4 |
| Dimension Tables | 5 |
| Fact Tables | 3 |
| Sample Questions | 35+ |
| Benchmark Questions | 24 |

---

## ⚠️ Important: Sample Data Date Ranges

**The Wanderbricks sample data has booking dates from historical periods.** When testing TVFs, use 5-year date ranges to capture all available data:

```sql
-- For sample data testing, use 5-year date ranges:
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_payment_metrics(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),  -- ✅ 5 years back
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);

-- NOT "last 90 days" which may return no data:
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_payment_metrics(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -90), 'yyyy-MM-dd'),  -- ❌ May be outside sample data
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```

**To find valid date ranges in your data:**
```sql
SELECT MIN(check_in_date), MAX(check_in_date) FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.fact_booking_detail;
```

---

## ⚠️ Important: Unity Catalog Namespace

**All table and function references must use the full 3-part Unity Catalog namespace:**
```
prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.object_name
```

For example:
- **Tables:** `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.fact_booking_daily`
- **Metric Views:** `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.revenue_analytics_metrics`
- **TVFs:** `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_revenue_by_period(...)`

---

# 🌐 Wanderbricks Analytics Genie Space

---

## A. Space Name

```
Space Name: Wanderbricks Analytics
```

---

## B. Space Description

```
Description: Unified natural language analytics and ML predictions for Wanderbricks vacation rental platform.
Enables business users to query revenue, marketing, property, host, customer insights, AND ML predictions
without SQL. Supports cross-domain analysis like "Which high-demand properties have the best conversion rates?"
and prescriptive questions like "What price should I set for Miami properties?"
Powered by 5 metric views, 33 TVFs (including 7 ML prediction functions), and 4 ML inference tables.
```

---

## C. Sample Questions

### 💰 Revenue & Financial
1. "What was total revenue last month?"
2. "Show me the top 10 properties by revenue"
3. "What is the weekly revenue trend for Q4?"
4. "Compare monthly revenue Q3 vs Q4"
5. "What is our cancellation rate?"

### 📊 Marketing & Engagement
6. "What is our conversion rate?"
7. "Show the view-to-booking funnel"
8. "Which properties have highest engagement?"
9. "What is click-through rate by property type?"
10. "Show daily engagement trends"

### 🏠 Property & Inventory
11. "How many properties do we have?"
12. "Show properties by destination"
13. "What is the average price by destination?"
14. "Which properties are underperforming?"
15. "Compare house vs apartment performance"

### 👤 Host & Partner
16. "Who are our top performing hosts?"
17. "How many verified hosts do we have?"
18. "Impact of verification on performance"
19. "Show multi-property hosts"
20. "Host distribution by country"

### 🎯 Customer & Segmentation
21. "What are our customer segments?"
22. "Who are our most valuable customers?"
23. "How often do customers book?"
24. "Business vs leisure breakdown"
25. "What is average customer lifetime value?"

### 🔗 Cross-Domain Questions
26. "Which destinations have both high engagement AND high revenue?"
27. "Do verified hosts generate more revenue per property?"
28. "What property types attract VIP customers?"
29. "Which markets have the best conversion rates AND highest LTV?"
30. "Compare host quality scores with customer satisfaction by destination"

### 🤖 ML Predictions & Recommendations
31. "Which properties have the highest predicted demand?"
32. "What price should I set for properties in Miami?"
33. "Show me VIP customers by predicted lifetime value"
34. "Which properties have high conversion probability?"
35. "What are the ML model predictions available?"

### 🔮 Cross-Domain ML Questions
36. "Do high-demand properties actually generate more revenue?"
37. "Which VIP customers booked properties with high conversion rates?"
38. "Compare predicted vs actual bookings by destination"
39. "What's the recommended price vs current price for top properties?"
40. "Show properties where pricing optimization would have the biggest impact"

---

## D. Data Assets

### Metric Views (PRIMARY - Use First)

| Metric View Name | Full Path | Domain | Key Measures |
|------------------|-----------|--------|--------------|
| `revenue_analytics_metrics` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.revenue_analytics_metrics` | 💰 Revenue | total_revenue, booking_count, avg_booking_value, cancellation_rate, payment_rate |
| `engagement_analytics_metrics` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.engagement_analytics_metrics` | 📊 Marketing | total_views, total_clicks, avg_conversion_rate, click_through_rate |
| `property_analytics_metrics` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.property_analytics_metrics` | 🏠 Property | property_count, avg_base_price, revenue_per_property, total_capacity |
| `host_analytics_metrics` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.host_analytics_metrics` | 👤 Host | host_count, avg_rating, verification_rate, revenue_per_host |
| `customer_analytics_metrics` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.customer_analytics_metrics` | 🎯 Customer | customer_count, spend_per_customer, bookings_per_customer, total_spend |

### Fact Tables

| Table Name | Full Path | Purpose | Grain |
|------------|-----------|---------|-------|
| `fact_booking_daily` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.fact_booking_daily` | Daily aggregated booking metrics | One row per property-destination-date |
| `fact_booking_detail` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.fact_booking_detail` | Transaction-level booking data | One row per booking |
| `fact_property_engagement` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.fact_property_engagement` | Daily property engagement metrics | One row per property-date |

### Dimension Tables

| Table Name | Full Path | Purpose | Key Columns |
|------------|-----------|---------|-------------|
| `dim_property` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_property` | Property listings | property_id, title, property_type, base_price, bedrooms, host_id |
| `dim_destination` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_destination` | Geographic locations | destination_id, destination, country, state_or_province |
| `dim_host` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_host` | Host information | host_id, name, is_verified, rating, country |
| `dim_user` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_user` | Customer master data | user_id, country, user_type, is_business |
| `dim_date` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_date` | Calendar lookups | date, year, quarter, month_name, is_weekend |

### ML Inference Tables (Predictions)

> **Note:** For customer-level analysis with user identifiers, use `get_customer_ltv` TVF which provides complete customer details.

| Table Name | Full Path | Purpose | Key Columns |
|------------|-----------|---------|-------------|
| `demand_predictions` | `${catalog}.${ml_schema}.demand_predictions` | Predicted booking demand | property_id, predicted_bookings, scoring_date, model_name |
| `conversion_predictions` | `${catalog}.${ml_schema}.conversion_predictions` | Conversion probability | property_id, conversion_probability, predicted_conversion, scoring_date |
| `pricing_recommendations` | `${catalog}.${ml_schema}.pricing_recommendations` | ML-optimized prices | property_id, recommended_price, scoring_date |
| `customer_ltv_predictions` | `${catalog}.${ml_schema}.customer_ltv_predictions` | ML-predicted lifetime value | predicted_ltv_12m, ltv_segment, scoring_date |

---

## E. General Instructions

```
You are an expert business analyst for Wanderbricks vacation rentals. Follow these rules:

1. **Metric Views First:** Use metric views before raw tables - they're pre-aggregated
2. **CRITICAL - Metric View Selection:**
   - Revenue/booking questions → revenue_analytics_metrics (source: fact_booking_daily)
   - Engagement/conversion questions → engagement_analytics_metrics
   - Property inventory/portfolio questions → property_analytics_metrics (source: dim_property)
   - Host demographics/verification → host_analytics_metrics (attributes only, NOT for revenue)
   - Customer segment/LTV questions → customer_analytics_metrics
   ⚠️ **HOST PERFORMANCE EXCEPTION:** For "Top hosts", "Best hosts", "Host revenue" → USE get_host_performance TVF (NOT host_analytics_metrics)
3. **CRITICAL - engagement_analytics_metrics Limitation:**
   - engagement_analytics_metrics has destination_id, NOT destination name
   - For destination names in engagement queries, JOIN dim_destination:
     `JOIN dim_destination dd ON engagement.destination_id = dd.destination_id`
   - revenue_analytics_metrics HAS destination name directly (no join needed)
4. **TVFs for Computed Analysis:**
   - Customer segments overview → get_customer_segments (aggregate stats only)
   - **"Most valuable customers"** → BOTH are valid:
     - By historical spend → get_customer_ltv (actual total_spend)
     - By predicted future value → customer_ltv_predictions ML table (predicted_ltv_12m)
   - **"What property types attract VIP customers?"** → get_vip_customer_property_preferences()
   - Business vs leisure → get_business_vs_leisure_analysis
   - Host performance / Top hosts → get_host_performance
   - ⚠️ NEVER use get_customer_segments for joining - it has NO user_id column
5. **Revenue & Pricing Analysis:**
   - Revenue per property (counts) → property_analytics_metrics
   - **"Impact of verification on performance"** → get_host_performance TVF (accurate revenue totals)
   - Revenue by host → get_host_performance TVF
   - Price for [destination] properties → get_pricing_by_destination (e.g., Miami, Paris)
   - ⚠️ property_analytics_metrics under-reports revenue (~$10M vs ~$40M actual) - use TVF for totals
6. **TVF Syntax:** SELECT * FROM tvf_name(params)
   - TVFs return pre-aggregated data - additional GROUP BY typically not needed
7. **Use TVFs:** For common patterns, prefer Table-Valued Functions over raw SQL
8. **ML Predictions:** Use ML TVFs (get_demand_predictions, get_pricing_recommendations, etc.) for forecasts
9. **Date Handling:** If no date specified, use 5-year range: DATE_ADD(CURRENT_DATE, -1826) to CURRENT_DATE
9. **Cross-Domain:** When questions span domains, join metric views or use multiple TVFs
10. **Aggregations:** SUM for totals, AVG for averages, COUNT DISTINCT for unique entities
11. **Sorting:** Sort by primary metric DESC unless user specifies otherwise
12. **Limits:** Top 10 for rankings, Top 100 for LTV queries unless specified
10. **Currency:** Format USD with $ and 2 decimals ($1,234.56)
11. **Percentages:** Format as % with 1 decimal (15.3%)
12. **SCD2 Tables:** Filter dim_property and dim_host with is_current = true
13. **Synonyms:** revenue=sales | demand=bookings forecast | VIP=high-value customers
14. **ML Context:** Predictions are ML-based forecasts; explain confidence when relevant
15. **Performance:** Never query Bronze/Silver tables - Gold layer and ML schema only
```

---

## F. Table-Valued Functions

### 💰 Revenue TVFs (6)

| Function | Full Path | Purpose |
|----------|-----------|---------|
| `get_revenue_by_period` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_revenue_by_period(start_date, end_date, time_grain)` | Revenue trends by day/week/month/quarter |
| `get_top_properties_by_revenue` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_top_properties_by_revenue(start_date, end_date, top_n)` | Top N properties by revenue |
| `get_revenue_by_destination` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_revenue_by_destination(start_date, end_date, top_n)` | Revenue by geography |
| `get_payment_metrics` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_payment_metrics(start_date, end_date)` | Payment method performance |
| `get_cancellation_analysis` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_cancellation_analysis(start_date, end_date)` | Cancellation rates and lost revenue |
| `get_revenue_forecast_inputs` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_revenue_forecast_inputs(start_date, end_date, property_id)` | ML forecasting data |

### 📊 Engagement TVFs (5)

| Function | Full Path | Purpose |
|----------|-----------|---------|
| `get_property_engagement` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_property_engagement(start_date, end_date, property_id)` | Property engagement metrics |
| `get_conversion_funnel` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_conversion_funnel(start_date, end_date, destination)` | View→Click→Book funnel |
| `get_traffic_source_analysis` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_traffic_source_analysis(start_date, end_date)` | Traffic by property type |
| `get_engagement_trends` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_engagement_trends(start_date, end_date, time_grain)` | Daily/weekly engagement |
| `get_top_engaging_properties` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_top_engaging_properties(start_date, end_date, top_n)` | Top properties by engagement |

### 🏠 Property TVFs (5)

| Function | Full Path | Purpose |
|----------|-----------|---------|
| `get_property_performance` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_property_performance(start_date, end_date, destination)` | Property KPIs |
| `get_availability_by_destination` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_availability_by_destination(start_date, end_date, top_n)` | Inventory by market |
| `get_property_type_analysis` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_property_type_analysis(start_date, end_date)` | Performance by type |
| `get_amenity_impact` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_amenity_impact(start_date, end_date)` | Amenity correlation |
| `get_pricing_analysis` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_pricing_analysis(start_date, end_date)` | Price point performance |

### 👤 Host TVFs (5)

| Function | Full Path | Purpose |
|----------|-----------|---------|
| `get_host_performance` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_host_performance(start_date, end_date, host_id)` | Host KPIs |
| `get_host_quality_metrics` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_host_quality_metrics(start_date, end_date, top_n)` | Top hosts by quality |
| `get_host_retention_analysis` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_host_retention_analysis(start_date, end_date)` | Active vs churned |
| `get_host_geographic_distribution` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_host_geographic_distribution(start_date, end_date, top_n)` | Hosts by country |
| `get_multi_property_hosts` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_multi_property_hosts(start_date, end_date, min_properties)` | Professional hosts |

### 🎯 Customer TVFs (5)

| Function | Full Path | Purpose |
|----------|-----------|---------|
| `get_customer_segments` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_customer_segments(start_date, end_date)` | Segment distribution |
| `get_customer_ltv` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_customer_ltv(start_date, end_date, top_n)` | Top customers by LTV |
| `get_booking_frequency_analysis` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_booking_frequency_analysis(start_date, end_date)` | Frequency distribution |
| `get_customer_geographic_analysis` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_customer_geographic_analysis(start_date, end_date, top_n)` | Customers by country |
| `get_business_vs_leisure_analysis` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_business_vs_leisure_analysis(start_date, end_date)` | B2B vs B2C comparison |

### 🤖 ML Prediction TVFs (7)

| Function | Full Path | Purpose |
|----------|-----------|---------|
| `get_demand_predictions` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_demand_predictions(destination_id, min_predicted_bookings)` | Query demand forecasts |
| `get_conversion_predictions` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_conversion_predictions(min_probability, property_id)` | Query conversion probabilities |
| `get_pricing_recommendations` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_pricing_recommendations(month, is_peak_season)` | Seasonal pricing aggregates |
| `get_pricing_by_destination` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_pricing_by_destination('Miami')` | **Pricing for destination properties** |
| `get_customer_ltv_predictions` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_customer_ltv_predictions(ltv_segment, min_ltv, user_id)` | Query customer LTV predictions |
| `get_vip_customers` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_vip_customers()` | Quick access to VIP customers (LTV > $2500) |
| `get_high_demand_properties` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_high_demand_properties(top_n)` | Top properties by predicted demand |
| `get_ml_predictions_summary` | `prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_ml_predictions_summary()` | Summary of all ML models and prediction counts |

---

## G. Benchmark Questions & Expected SQL

### 💰 Revenue Domain

#### Question 1: "What was total revenue last month?"
**Expected SQL:**
```sql
SELECT 
  period_name,
  total_revenue,
  booking_count,
  avg_booking_value
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_revenue_by_period(
  DATE_FORMAT(DATE_TRUNC('month', ADD_MONTHS(CURRENT_DATE, -1)), 'yyyy-MM-dd'),
  DATE_FORMAT(LAST_DAY(ADD_MONTHS(CURRENT_DATE, -1)), 'yyyy-MM-dd'),
  'month'
);
```
**Expected Result:** Single row showing last month's revenue, booking count, and average booking value

---

#### Question 2: "What is the weekly revenue trend for Q4?"
**Expected SQL:**
```sql
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_revenue_by_period('2024-10-01', '2024-12-31', 'week')
ORDER BY period_start;
```
**Expected Result:** 13 rows (weeks in Q4) showing revenue per week

---

#### Question 3: "Show payment completion rates"
**Expected SQL:**
```sql
SELECT 
  payment_method,
  booking_count,
  total_payment_amount,
  payment_completion_rate
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_payment_metrics('1900-01-01', '2100-12-31')
ORDER BY payment_completion_rate DESC;
```
**Expected Result:** Payment methods with completion rates and volume (all data)

---

#### Question 4: "Revenue by property type"
**CRITICAL:** Must use `revenue_analytics_metrics` (not `property_analytics_metrics`) for accurate revenue totals.

**Expected SQL:**
```sql
SELECT 
  property_type,
  MEASURE(total_revenue) as total_revenue,
  MEASURE(booking_count) as bookings,
  MEASURE(avg_booking_value) as avg_booking
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.revenue_analytics_metrics
GROUP BY property_type
ORDER BY total_revenue DESC;
```
**Expected Result:** Revenue breakdown by apartment, house, villa, etc.

**Why:** `revenue_analytics_metrics` sources from `fact_booking_daily` (complete booking data). `property_analytics_metrics` sources from `dim_property` (SCD2 dimension) and may show lower totals due to join behavior.

---

### 📊 Marketing Domain

#### Question 5: "What is our conversion rate?"
**Expected SQL:**
```sql
SELECT 
  MEASURE(avg_conversion_rate) as conversion_rate,
  MEASURE(total_views) as views,
  MEASURE(total_clicks) as clicks
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.engagement_analytics_metrics;
```
**Expected Result:** Overall conversion rate with supporting metrics

---

#### Question 6: "Show the view-to-booking funnel"
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
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_conversion_funnel(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
ORDER BY overall_conversion_rate DESC;
```
**Expected Result:** Funnel metrics by destination with stage drop-off rates

---

#### Question 7: "Which properties have highest engagement?"
**Expected SQL:**
```sql
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_top_engaging_properties(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  10
);
```
**Expected Result:** Top 10 properties ranked by engagement score

---

### 🏠 Property Domain

#### Question 8: "How many properties do we have?"
**Expected SQL:**
```sql
SELECT 
  MEASURE(property_count) as total_properties,
  MEASURE(total_capacity) as total_capacity
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.property_analytics_metrics;
```
**Expected Result:** Total property count and guest capacity

---

#### Question 9: "Which properties are underperforming?"
**Expected SQL:**
```sql
SELECT 
  property_title,
  destination,
  total_revenue,
  avg_occupancy_rate,
  property_score
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_property_performance(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
WHERE avg_occupancy_rate < 30 OR total_revenue < 1000
ORDER BY property_score ASC
LIMIT 20;
```
**Expected Result:** Low-performing properties for optimization focus

---

#### Question 10: "Compare house vs apartment performance"
**Expected SQL:**
```sql
SELECT 
  property_type,
  property_count,
  total_revenue,
  avg_booking_value,
  avg_occupancy_rate,
  market_share_revenue
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_property_type_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
)
WHERE property_type IN ('House', 'Apartment');
```
**Expected Result:** Side-by-side comparison of house vs apartment metrics

---

### 👤 Host Domain

#### Question 11: "Who are our top performing hosts?"

> **CRITICAL:** Use `get_host_performance` TVF, NOT `host_analytics_metrics` metric view!
> - Metric view shows top host with $1,094 revenue (WRONG - only finds 1 booking per host)
> - TVF shows top host with $253,534 revenue (CORRECT - finds 465 bookings)
> - **230x difference!** The metric view's direct host_id join misses 99%+ of bookings
> - TVF joins correctly: dim_host → dim_property → fact_booking_detail

**Expected SQL:**
```sql
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_host_performance(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
ORDER BY host_performance_score DESC
LIMIT 10;
```
**Expected Result:** Top 10 hosts ranked by composite performance score with accurate revenue/booking counts

---

#### Question 12: "How many verified hosts do we have?"
**Expected SQL:**
```sql
SELECT 
  MEASURE(verified_count) as verified_count,
  MEASURE(host_count) as total_hosts,
  MEASURE(verification_rate) as verification_rate
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.host_analytics_metrics;
```
**Expected Result:** Verified host count and percentage

---

#### Question 13: "Impact of verification on performance"

> **CRITICAL:** Use `get_host_performance` TVF aggregated by `is_verified`, NOT `host_analytics_metrics`.
> - TVF joins correctly: dim_host → dim_property → fact_booking_detail (via property_id)
> - Metric view joins directly on host_id which may miss bookings
> - TVF includes SCD2 filter (is_current=true) and proper date range
> - Revenue difference: TVF ~$36M vs Metric View ~$1.8M (19x difference!)

**Expected SQL:**
```sql
SELECT 
  is_verified,
  COUNT(DISTINCT host_id) as host_count,
  SUM(total_revenue) as total_revenue,
  AVG(rating) as avg_rating,
  AVG(host_performance_score) as avg_score
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_host_performance(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  NULL
)
GROUP BY is_verified;
```
**Expected Result:** Verified vs non-verified comparison with accurate revenue totals

---

### 🎯 Customer Domain

#### Question 14: "What are our customer segments?"

> **CRITICAL:** "Customer segments" = **behavioral segments** based on booking frequency, NOT dimensional groupings.
> - Use `get_customer_segments` TVF → returns VIP, Frequent Traveler, Repeat Customer, One-time Booker, Inactive
> - Do NOT use `customer_analytics_metrics` grouped by user_type/country → that's demographic breakdown, not behavioral segmentation
> - Behavioral segments are calculated programmatically by booking count (7+ = VIP, 4-6 = Frequent, 2-3 = Repeat, 1 = One-time, 0 = Inactive)

**Expected SQL:**
```sql
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_customer_segments(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```
**Expected Result:** Behavioral segment breakdown with revenue share, booking patterns, and cancellation rates per segment

---

#### Question 15: "Who are our most valuable customers?"

> **CRITICAL:** Use `get_customer_ltv` TVF, NOT `customer_analytics_metrics` metric view.
> - TVF uses INNER JOIN + explicit SUM(total_amount) = accurate lifetime value calculation
> - Metric view with MEASURE() + ROW_NUMBER() OVER may produce incorrect aggregations
> - TVF also provides valuable context: country, tenure, recency, first/last booking dates

**Expected SQL:**
```sql
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_customer_ltv(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd'),
  20
);
```
**Expected Result:** Top 20 customers ranked by lifetime value with full customer profile

---

#### Question 16: "Business vs leisure breakdown"

> **CRITICAL:** This question asks about **trip purpose** (business travel vs leisure vacation), NOT customer type.
> - Use `get_business_vs_leisure_analysis` TVF → groups by `is_business_booking` (booking attribute)
> - Do NOT use `customer_analytics_metrics` with `user_type` → that's customer account type, not trip purpose
> - A "business" user can book leisure trips; an "individual" can book business trips

**Expected SQL:**
```sql
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_business_vs_leisure_analysis(
  DATE_FORMAT(DATE_ADD(CURRENT_DATE, -1826), 'yyyy-MM-dd'),
  DATE_FORMAT(CURRENT_DATE, 'yyyy-MM-dd')
);
```
**Expected Result:** Business vs Leisure comparison by **booking type** (trip purpose), including revenue, avg booking value, lead time, cancellation rate

---

### 🔗 Cross-Domain Questions

#### Question 17: "Which destinations have both high engagement AND high revenue?"

> **Note:** Uses percentile-based "high" definition (top 10%) which is more robust than hardcoded thresholds.
> `engagement_analytics_metrics` has `destination_id`, while `revenue_analytics_metrics` has `destination`.

**Expected SQL:**
```sql
WITH engagement AS (
  SELECT
    destination_id,
    MEASURE(total_views) AS total_views
  FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.engagement_analytics_metrics
  GROUP BY destination_id
),
revenue AS (
  SELECT
    destination,
    MEASURE(total_revenue) AS total_revenue
  FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.revenue_analytics_metrics
  GROUP BY destination
),
-- Calculate percentiles SEPARATELY (not cartesian product!)
eng_p90 AS (
  SELECT percentile_approx(total_views, 0.9) AS p90_views FROM engagement
),
rev_p90 AS (
  SELECT percentile_approx(total_revenue, 0.9) AS p90_revenue FROM revenue
),
engagement_with_name AS (
  SELECT e.destination_id, d.destination, e.total_views
  FROM engagement e
  JOIN prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_destination d
    ON e.destination_id = d.destination_id
  WHERE d.destination IS NOT NULL
)
SELECT
  ewn.destination,
  ewn.total_views,
  r.total_revenue
FROM engagement_with_name ewn
JOIN revenue r ON ewn.destination = r.destination
CROSS JOIN eng_p90
CROSS JOIN rev_p90
WHERE ewn.total_views >= eng_p90.p90_views
  AND r.total_revenue >= rev_p90.p90_revenue
ORDER BY ewn.total_views DESC, r.total_revenue DESC
LIMIT 20;
```
**Expected Result:** Top destinations with both high engagement (top 10% views) AND high revenue (top 10%)

> **Note:** Genie's query is correct! The key is calculating percentiles separately, not via cartesian product which inflates values.

---

#### Question 18: "Do verified hosts generate more revenue per property?"

> **⚠️ CRITICAL:** This question asks about "revenue per **PROPERTY**" - use `property_analytics_metrics`!
> 
> **DO NOT use `host_analytics_metrics`!** Its nested join structure drops ~80% of properties
> (3,446 vs 16,458), causing dramatically wrong results.
>
> `property_analytics_metrics` has:
> - `revenue_per_property` measure (pre-calculated correctly)
> - `is_verified_host` dimension (inherited from dim_property → dim_host)
> - ALL properties included (18,163 total)

**Expected SQL:**
```sql
SELECT 
  is_verified_host,
  MEASURE(revenue_per_property) as revenue_per_property,
  MEASURE(property_count) as property_count,
  MEASURE(avg_base_price) as avg_base_price
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.property_analytics_metrics
WHERE is_verified_host IS NOT NULL
GROUP BY is_verified_host
ORDER BY revenue_per_property DESC;
```
**Expected Result:** Revenue per property comparison by host verification status (verified hosts' properties generate ~$550.86 vs ~$546.45 for unverified, with 16,458 and 1,705 properties respectively)

---

#### Question 19: "What property types attract VIP customers?"

> **⚠️ CRITICAL:** Use `get_vip_customer_property_preferences()` TVF for this question!
> 
> **DO NOT try to join `get_customer_segments()`** - it returns AGGREGATE stats without user_ids.
> The dedicated TVF calculates VIP customers (top 5% spenders) and their property preferences in one query.

**Expected SQL:**
```sql
SELECT *
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_vip_customer_property_preferences();
```
**Expected Result:** Property types ranked by number of VIP customers who book them, including VIP booking count and revenue

---

#### Question 20: "Show a complete business overview"
**Expected SQL:**
```sql
WITH revenue_summary AS (
  SELECT 
    MEASURE(total_revenue) as total_revenue,
    MEASURE(booking_count) as total_bookings,
    MEASURE(avg_booking_value) as avg_booking
  FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.revenue_analytics_metrics
),
property_summary AS (
  SELECT 
    MEASURE(property_count) as total_properties
  FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.property_analytics_metrics
),
host_summary AS (
  SELECT 
    MEASURE(host_count) as total_hosts,
    MEASURE(verification_rate) as verification_rate
  FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.host_analytics_metrics
),
customer_summary AS (
  SELECT 
    MEASURE(customer_count) as total_customers,
    MEASURE(spend_per_customer) as avg_ltv
  FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.customer_analytics_metrics
)
SELECT 
  r.total_revenue, r.total_bookings, r.avg_booking,
  p.total_properties,
  h.total_hosts, h.verification_rate,
  c.total_customers, c.avg_ltv
FROM revenue_summary r, property_summary p, host_summary h, customer_summary c;
```
**Expected Result:** Complete platform metrics in one view

---

### 🤖 ML Predictions Domain

#### Question 21: "Which properties have the highest predicted demand?"
**Expected SQL:**
```sql
SELECT
  property_id,
  predicted_bookings,
  scoring_date
FROM
  prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_ml.demand_predictions
ORDER BY
  predicted_bookings DESC
LIMIT 20;
```
**Expected Result:** Top 20 individual properties by predicted booking demand

> **Note:** If all `predicted_bookings = 1`, this indicates the ML model needs retraining or the batch inference pipeline issue. Use `get_high_demand_properties()` for destination-level aggregates instead.

---

#### Question 22: "What price should I set for Miami properties?"
**Expected SQL:**
```sql
SELECT *
FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_pricing_by_destination('Miami');
```
**Expected Result:** Miami properties with avg/min/max prices by property type and ML seasonal adjustment

> **Note:** The `pricing_recommendations` ML table doesn't have `property_id`. Use `get_pricing_by_destination` TVF which combines property base prices with ML seasonal adjustments.

---

#### Question 23: "Show me VIP customers"
**Expected SQL:**
```sql
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_vip_customers();
```
**Expected Result:** Customers with predicted LTV > $2500

---

#### Question 24: "What ML predictions are available?"
**Expected SQL:**
```sql
SELECT * FROM prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_ml_predictions_summary();
```
**Expected Result:** Summary of all 4 ML models with prediction counts and latest scoring dates

---

# ✅ Deployment Checklist

## Pre-Deployment Validation

| Section | Requirement | Status |
|---------|-------------|--------|
| A. Space Name | "Wanderbricks Analytics" | ✅ |
| B. Space Description | 3 sentences, cross-domain + ML mention | ✅ |
| C. Sample Questions | 40 questions across 8 categories (incl. ML) | ✅ |
| D. Data Assets | 5 metric views + 3 facts + 5 dims + 4 ML tables | ✅ |
| E. General Instructions | 15 lines (incl. ML guidance) | ✅ |
| F. TVFs | 33 functions (26 analytics + 7 ML) | ✅ |
| G. Benchmark Questions | 24 with working SQL (incl. 4 ML) | ✅ |

## Deployment Steps

### 1. Create Genie Space (UI)

```
1. Navigate to: Databricks Workspace → Genie → Create New Space
2. Enter Space Name: "Wanderbricks Analytics"
3. Enter Description (from Section B)
4. Select Serverless SQL Warehouse
5. Add Sample Questions (from Section C - select 10-15 representative ones)
```

### 2. Add Trusted Assets

**Add in this order for best performance:**

```
1. Click "Add Trusted Assets"

2. Add ALL 5 Metric Views (primary data sources):
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.revenue_analytics_metrics
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.engagement_analytics_metrics
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.property_analytics_metrics
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.host_analytics_metrics
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.customer_analytics_metrics

3. Add ALL 26 Analytics TVFs (grouped by domain)

4. Add ALL 7 ML Prediction TVFs:
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_demand_predictions
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_conversion_predictions
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_pricing_recommendations
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_customer_ltv_predictions
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_vip_customers
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_high_demand_properties
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.get_ml_predictions_summary

5. Add Dimension Tables:
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_property
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_destination
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_host
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_user
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.dim_date

6. Add Fact Tables (for advanced queries):
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.fact_booking_daily
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.fact_booking_detail
   - prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.fact_property_engagement

7. Add ML Inference Tables (for cross-referencing):
   - ${catalog}.${ml_schema}.demand_predictions
   - ${catalog}.${ml_schema}.conversion_predictions
   - ${catalog}.${ml_schema}.pricing_recommendations
   - ${catalog}.${ml_schema}.customer_ltv_predictions
```

### 3. Configure Agent Instructions

```
1. Open Space Settings
2. Paste General Instructions (from Section E)
3. Verify ≤20 lines
```

### 4. Test Benchmark Questions

```
1. Test all 20 benchmark questions (Section G)
2. Pay special attention to cross-domain questions (17-20)
3. Compare generated SQL to expected SQL
4. Verify results match expected output
5. Refine instructions if needed
```

### 5. Grant Permissions

```sql
-- Grant access to user groups
GRANT USE SCHEMA ON prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold TO data_analysts;
GRANT SELECT ON TABLE prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.* TO data_analysts;
GRANT EXECUTE ON FUNCTION prashanth_subrahmanyam_catalog.dev_prashanth_subrahmanyam_wanderbricks_gold.* TO data_analysts;
```

---

## Comparison: Unified vs Domain-Specific Spaces

| Aspect | 5 Domain Spaces | 1 Unified Space (with ML) |
|--------|-----------------|---------------------------|
| **Cross-domain queries** | ❌ Need to switch | ✅ Natural |
| **ML predictions** | ❌ Separate ML space needed | ✅ Integrated |
| **User experience** | Complex (which space?) | Simple (one space) |
| **Administration** | 5x instructions | 1 set of instructions |
| **Context size** | Smaller per space | Larger but comprehensive |
| **Asset count per space** | 3-6 each | 41 assets (incl. ML) |
| **Best for** | Role-specific teams | Analysts, executives, data scientists |

**Recommendation:** Use the unified space with ML for most users. It enables:
- ✅ Analytics questions (revenue, engagement, property, host, customer)
- ✅ Predictive questions (demand forecasts, conversion likelihood)
- ✅ Prescriptive questions (pricing recommendations, LTV predictions)
- ✅ Validation questions (predicted vs actual comparisons)

---

## Why ML Predictions in Genie Space Makes Sense

| Capability | Without ML | With ML |
|------------|------------|---------|
| "What was revenue?" | ✅ Descriptive | ✅ Descriptive |
| "What will demand be?" | ❌ N/A | ✅ Predictive |
| "What price should we set?" | ❌ N/A | ✅ Prescriptive |
| "Are predictions accurate?" | ❌ N/A | ✅ Validation |

**Key ML Questions Now Supported:**
1. **Demand Planning:** "Which properties have highest predicted demand?"
2. **Revenue Optimization:** "What price should I set for X properties?"
3. **Customer Focus:** "Who are our predicted VIP customers?"
4. **Model Validation:** "How do predictions compare to actuals?"

---

## References

- [Genie Spaces Documentation](https://docs.databricks.com/genie/)
- [Trusted Assets](https://docs.databricks.com/genie/trusted-assets.html)
- [Genie Space Patterns Rule](../../.cursor/rules/semantic-layer/16-genie-space-patterns.mdc)
- [TVF Patterns Rule](../../.cursor/rules/semantic-layer/15-databricks-table-valued-functions.mdc)
- [Domain-Specific Setup Guide](./GENIE_SPACE_SETUP_COMPLETE.md)

