-- =============================================================================
-- Wanderbricks Gold Layer - Revenue Domain TVFs for Genie
-- 
-- This file contains revenue-focused Table-Valued Functions optimized for
-- Genie Spaces and natural language queries.
--
-- Key Patterns:
-- 1. STRING for date parameters (Genie doesn't support DATE type)
-- 2. Required parameters first, optional (DEFAULT) parameters last
-- 3. ROW_NUMBER + WHERE for Top N (not LIMIT with parameter)
-- 4. NULLIF for all divisions (null safety)
-- 5. is_current = true for SCD2 dimension joins
--
-- Created: December 2025
-- =============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${gold_schema};

-- =============================================================================
-- TVF 1: get_revenue_by_period
-- Returns revenue metrics aggregated by time period
-- =============================================================================

CREATE OR REPLACE FUNCTION get_revenue_by_period(
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)',
  time_grain STRING DEFAULT 'day' COMMENT 'Aggregation grain: day, week, month, quarter, year'
)
RETURNS TABLE (
  period_start DATE COMMENT 'Start date of the period',
  period_name STRING COMMENT 'Human-friendly period label',
  total_revenue DECIMAL(18,2) COMMENT 'Total booking revenue for period',
  booking_count BIGINT COMMENT 'Number of bookings',
  avg_booking_value DECIMAL(18,2) COMMENT 'Average revenue per booking',
  confirmed_bookings BIGINT COMMENT 'Number of confirmed bookings',
  cancellation_count BIGINT COMMENT 'Number of cancelled bookings',
  cancellation_rate DECIMAL(5,2) COMMENT 'Cancellation rate as percentage',
  unique_properties BIGINT COMMENT 'Number of unique properties booked',
  unique_guests BIGINT COMMENT 'Number of unique guests'
)
COMMENT '
• PURPOSE: Revenue metrics aggregated by time period
• BEST FOR: "Weekly revenue trend" | "Monthly revenue" | "Revenue by quarter" | "Revenue for Q4"
• RETURNS: PRE-AGGREGATED rows (period_start, period_name, total_revenue, booking_count, avg_booking_value)
• PARAMS: start_date, end_date, time_grain (day|week|month|quarter|year, default: day)
• SYNTAX: SELECT * FROM get_revenue_by_period(''2024-10-01'', ''2024-12-31'', ''week'')
'
RETURN
  SELECT 
    DATE_TRUNC(time_grain, fbd.check_in_date) AS period_start,
    CASE 
      WHEN time_grain = 'day' THEN DATE_FORMAT(DATE_TRUNC(time_grain, fbd.check_in_date), 'yyyy-MM-dd')
      WHEN time_grain = 'week' THEN CONCAT('Week ', WEEKOFYEAR(DATE_TRUNC(time_grain, fbd.check_in_date)), ' ', YEAR(DATE_TRUNC(time_grain, fbd.check_in_date)))
      WHEN time_grain = 'month' THEN DATE_FORMAT(DATE_TRUNC(time_grain, fbd.check_in_date), 'MMMM yyyy')
      WHEN time_grain = 'quarter' THEN CONCAT('Q', QUARTER(DATE_TRUNC(time_grain, fbd.check_in_date)), ' ', YEAR(DATE_TRUNC(time_grain, fbd.check_in_date)))
      WHEN time_grain = 'year' THEN CAST(YEAR(DATE_TRUNC(time_grain, fbd.check_in_date)) AS STRING)
      ELSE DATE_FORMAT(DATE_TRUNC(time_grain, fbd.check_in_date), 'yyyy-MM-dd')
    END AS period_name,
    SUM(fbd.total_booking_value) as total_revenue,
    SUM(fbd.booking_count) as booking_count,
    SUM(fbd.total_booking_value) / NULLIF(SUM(fbd.booking_count), 0) as avg_booking_value,
    SUM(fbd.confirmed_booking_count) as confirmed_bookings,
    SUM(fbd.cancellation_count) as cancellation_count,
    (SUM(fbd.cancellation_count) / NULLIF(SUM(fbd.booking_count), 0)) * 100 as cancellation_rate,
    COUNT(DISTINCT fbd.property_id) as unique_properties,
    SUM(fbd.total_guests) as unique_guests
  FROM ${catalog}.${gold_schema}.fact_booking_daily fbd
  WHERE fbd.check_in_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
  GROUP BY DATE_TRUNC(time_grain, fbd.check_in_date)
  ORDER BY period_start;

-- =============================================================================
-- TVF 2: get_top_properties_by_revenue
-- Returns top N properties by revenue for date range
-- =============================================================================

CREATE OR REPLACE FUNCTION get_top_properties_by_revenue(
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)',
  top_n INT DEFAULT 10 COMMENT 'Number of top properties to return'
)
RETURNS TABLE (
  rank BIGINT COMMENT 'Property rank by revenue',
  property_id BIGINT COMMENT 'Property identifier',
  property_title STRING COMMENT 'Property listing title',
  destination STRING COMMENT 'Property destination (city, state, country)',
  property_type STRING COMMENT 'Property type (apartment, house, etc.)',
  host_name STRING COMMENT 'Property owner name',
  total_revenue DECIMAL(18,2) COMMENT 'Total revenue for period',
  booking_count BIGINT COMMENT 'Number of bookings',
  avg_revenue_per_booking DECIMAL(18,2) COMMENT 'Average revenue per booking',
  total_nights BIGINT COMMENT 'Total nights booked',
  avg_occupancy_rate DECIMAL(5,2) COMMENT 'Occupancy rate as percentage'
)
COMMENT '
• PURPOSE: Top properties ranked by revenue
• BEST FOR: "Top revenue generating properties" | "Best performing listings" | "Which properties made most money?"
• RETURNS: Individual property rows (rank, property_id, title, destination, total_revenue, booking_count)
• PARAMS: start_date, end_date, top_n (default: 10)
• SYNTAX: SELECT * FROM get_top_revenue_properties(''2020-01-01'', ''2024-12-31'', 20)
'
RETURN
  WITH property_metrics AS (
    SELECT 
      fbd.property_id,
      dp.title as property_title,
      CONCAT(dd.destination, ', ', dd.state_or_province, ', ', dd.country) as destination,
      dp.property_type,
      dh.name as host_name,
      SUM(fbd.total_booking_value) as total_revenue,
      SUM(fbd.booking_count) as booking_count,
      SUM(fbd.total_booking_value) / NULLIF(SUM(fbd.booking_count), 0) as avg_revenue_per_booking,
      SUM(fbd.avg_nights_booked * fbd.booking_count) as total_nights,
      (SUM(fbd.booking_count) / NULLIF(DATEDIFF(CAST(end_date AS DATE), CAST(start_date AS DATE)), 0)) * 100 as avg_occupancy_rate
    FROM ${catalog}.${gold_schema}.fact_booking_daily fbd
    LEFT JOIN ${catalog}.${gold_schema}.dim_property dp 
      ON fbd.property_id = dp.property_id 
      AND dp.is_current = true
    LEFT JOIN ${catalog}.${gold_schema}.dim_destination dd 
      ON fbd.destination_id = dd.destination_id
    LEFT JOIN ${catalog}.${gold_schema}.dim_host dh 
      ON dp.host_id = dh.host_id 
      AND dh.is_current = true
    WHERE fbd.check_in_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY fbd.property_id, dp.title, dd.destination, dd.state_or_province, dd.country, dp.property_type, dh.name
  ),
  ranked_properties AS (
    SELECT 
      ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as rank,
      property_id,
      property_title,
      destination,
      property_type,
      host_name,
      total_revenue,
      booking_count,
      avg_revenue_per_booking,
      total_nights,
      avg_occupancy_rate
    FROM property_metrics
  )
  SELECT * FROM ranked_properties
  WHERE rank <= top_n
  ORDER BY rank;

-- =============================================================================
-- TVF 3: get_revenue_by_destination
-- Returns revenue breakdown by destination/geography
-- =============================================================================

CREATE OR REPLACE FUNCTION get_revenue_by_destination(
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)',
  top_n INT DEFAULT 20 COMMENT 'Number of top destinations to return'
)
RETURNS TABLE (
  rank BIGINT COMMENT 'Destination rank by revenue',
  destination_id BIGINT COMMENT 'Destination identifier',
  destination STRING COMMENT 'Destination city/area name',
  state_or_province STRING COMMENT 'Destination state/region',
  country STRING COMMENT 'Destination country',
  property_count BIGINT COMMENT 'Number of properties in destination',
  total_revenue DECIMAL(18,2) COMMENT 'Total revenue for destination',
  booking_count BIGINT COMMENT 'Number of bookings',
  avg_revenue_per_property DECIMAL(18,2) COMMENT 'Average revenue per property',
  unique_guests BIGINT COMMENT 'Number of unique guests'
)
COMMENT '
• PURPOSE: Revenue breakdown by geographic destination
• BEST FOR: "Revenue by destination" | "Top performing cities" | "Which markets generate most revenue?"
• RETURNS: PRE-AGGREGATED rows (destination, country, total_revenue, booking_count, avg_booking_value)
• PARAMS: start_date, end_date, top_n (default: 20)
• SYNTAX: SELECT * FROM get_revenue_by_destination(''2020-01-01'', ''2024-12-31'')
'
RETURN
  WITH destination_metrics AS (
    SELECT 
      fbd.destination_id,
      dd.destination,
      dd.state_or_province,
      dd.country,
      COUNT(DISTINCT fbd.property_id) as property_count,
      SUM(fbd.total_booking_value) as total_revenue,
      SUM(fbd.booking_count) as booking_count,
      SUM(fbd.total_booking_value) / NULLIF(COUNT(DISTINCT fbd.property_id), 0) as avg_revenue_per_property,
      SUM(fbd.total_guests) as unique_guests
    FROM ${catalog}.${gold_schema}.fact_booking_daily fbd
    LEFT JOIN ${catalog}.${gold_schema}.dim_destination dd 
      ON fbd.destination_id = dd.destination_id
    WHERE fbd.check_in_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY fbd.destination_id, dd.destination, dd.state_or_province, dd.country
  ),
  ranked_destinations AS (
    SELECT 
      ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as rank,
      destination_id,
      destination,
      state_or_province,
      country,
      property_count,
      total_revenue,
      booking_count,
      avg_revenue_per_property,
      unique_guests
    FROM destination_metrics
  )
  SELECT * FROM ranked_destinations
  WHERE rank <= top_n
  ORDER BY rank;

-- =============================================================================
-- TVF 4: get_payment_metrics
-- Returns payment completion rates and method analysis
-- =============================================================================

CREATE OR REPLACE FUNCTION get_payment_metrics(
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)'
)
RETURNS TABLE (
  payment_method STRING COMMENT 'Payment method used',
  booking_count BIGINT COMMENT 'Number of bookings with this payment method',
  total_payment_amount DECIMAL(18,2) COMMENT 'Total payments processed',
  avg_payment_amount DECIMAL(18,2) COMMENT 'Average payment amount',
  payment_completion_rate DECIMAL(5,2) COMMENT 'Percentage of bookings with completed payments',
  total_booking_value DECIMAL(18,2) COMMENT 'Total booking value (including unpaid)'
)
COMMENT '
• PURPOSE: Payment completion rates and method analysis
• BEST FOR: "Payment completion rates" | "Payment method performance" | "Most popular payment methods"
• RETURNS: PRE-AGGREGATED rows (payment_method, booking_count, total_payment_amount, payment_completion_rate)
• PARAMS: start_date, end_date
• SYNTAX: SELECT * FROM get_payment_metrics(''2020-01-01'', ''2024-12-31'')
'
RETURN
  WITH payment_data AS (
    SELECT 
      COALESCE(payment_method, 'Unpaid/Pending') as payment_method,
      COUNT(*) as booking_count,
      SUM(COALESCE(payment_amount, 0)) as total_payment_amount,
      SUM(COALESCE(payment_amount, 0)) / NULLIF(COUNT(*), 0) as avg_payment_amount,
      (SUM(CASE WHEN payment_amount IS NOT NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)) * 100 as payment_completion_rate,
      SUM(total_amount) as total_booking_value
    FROM ${catalog}.${gold_schema}.fact_booking_detail
    WHERE check_in_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY COALESCE(payment_method, 'Unpaid/Pending')
  )
  SELECT 
    payment_method,
    booking_count,
    total_payment_amount,
    avg_payment_amount,
    payment_completion_rate,
    total_booking_value
  FROM payment_data
  ORDER BY total_payment_amount DESC;

-- =============================================================================
-- TVF 5: get_cancellation_analysis
-- Returns cancellation patterns and revenue impact
-- =============================================================================

CREATE OR REPLACE FUNCTION get_cancellation_analysis(
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)'
)
RETURNS TABLE (
  destination STRING COMMENT 'Destination (city, state, country)',
  total_bookings BIGINT COMMENT 'Total bookings (confirmed + cancelled)',
  confirmed_bookings BIGINT COMMENT 'Number of confirmed bookings',
  cancelled_bookings BIGINT COMMENT 'Number of cancelled bookings',
  cancellation_rate DECIMAL(5,2) COMMENT 'Cancellation rate as percentage',
  potential_revenue DECIMAL(18,2) COMMENT 'Total booking value including cancelled',
  actual_revenue DECIMAL(18,2) COMMENT 'Revenue from confirmed bookings only',
  lost_revenue DECIMAL(18,2) COMMENT 'Revenue lost to cancellations'
)
COMMENT '
• PURPOSE: Cancellation patterns and revenue impact by destination
• BEST FOR: "Cancellation rates by destination" | "Revenue lost to cancellations" | "Highest cancellation markets"
• RETURNS: PRE-AGGREGATED rows (destination, cancellation_rate, cancelled_revenue, total_revenue)
• PARAMS: start_date, end_date
• SYNTAX: SELECT * FROM get_cancellation_analysis(''2020-01-01'', ''2024-12-31'')
'
RETURN
  WITH cancellation_data AS (
    SELECT 
      CONCAT(dd.destination, ', ', dd.state_or_province, ', ', dd.country) as destination,
      COUNT(*) as total_bookings,
      SUM(CASE WHEN fbd.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_bookings,
      SUM(CASE WHEN fbd.is_cancelled THEN 1 ELSE 0 END) as cancelled_bookings,
      (SUM(CASE WHEN fbd.is_cancelled THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)) * 100 as cancellation_rate,
      SUM(fbd.total_amount) as potential_revenue,
      SUM(CASE WHEN fbd.status = 'confirmed' THEN fbd.total_amount ELSE 0 END) as actual_revenue,
      SUM(CASE WHEN fbd.is_cancelled THEN fbd.total_amount ELSE 0 END) as lost_revenue
    FROM ${catalog}.${gold_schema}.fact_booking_detail fbd
    LEFT JOIN ${catalog}.${gold_schema}.dim_destination dd 
      ON fbd.destination_id = dd.destination_id
    WHERE fbd.check_in_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY dd.destination, dd.state_or_province, dd.country
  )
  SELECT 
    destination,
    total_bookings,
    confirmed_bookings,
    cancelled_bookings,
    cancellation_rate,
    potential_revenue,
    actual_revenue,
    lost_revenue
  FROM cancellation_data
  WHERE total_bookings > 0
  ORDER BY lost_revenue DESC;

-- =============================================================================
-- TVF 6: get_revenue_forecast_inputs
-- Returns historical data formatted for revenue forecasting ML models
-- =============================================================================

CREATE OR REPLACE FUNCTION get_revenue_forecast_inputs(
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)',
  property_id_filter BIGINT DEFAULT NULL COMMENT 'Optional: Filter to specific property (NULL for all)'
)
RETURNS TABLE (
  ds DATE COMMENT 'Date (Prophet-compatible column name)',
  property_id BIGINT COMMENT 'Property identifier for grouping',
  y DECIMAL(18,2) COMMENT 'Daily revenue (Prophet-compatible target variable)',
  booking_count BIGINT COMMENT 'Number of bookings (feature)',
  avg_booking_value DECIMAL(18,2) COMMENT 'Average booking value (feature)',
  day_of_week INT COMMENT 'Day of week (1=Sunday, feature)',
  is_weekend BOOLEAN COMMENT 'Weekend indicator (feature)',
  month INT COMMENT 'Month number (feature)',
  quarter INT COMMENT 'Quarter number (feature)'
)
COMMENT '
• PURPOSE: Historical revenue data formatted for ML forecasting (Prophet-compatible)
• BEST FOR: "Revenue forecasting data" | "Historical revenue for ML" | "Time series data"
• RETURNS: Daily rows (ds, y) - Prophet-compatible format
• PARAMS: start_date, end_date, property_id_filter (optional, NULL for all)
• SYNTAX: SELECT * FROM get_revenue_forecast_data(''2020-01-01'', ''2024-12-31'')
'
RETURN
  SELECT 
    fbd.check_in_date as ds,
    fbd.property_id,
    fbd.total_booking_value as y,
    fbd.booking_count,
    fbd.avg_booking_value,
    DAYOFWEEK(fbd.check_in_date) as day_of_week,
    dd.is_weekend,
    MONTH(fbd.check_in_date) as month,
    QUARTER(fbd.check_in_date) as quarter
  FROM ${catalog}.${gold_schema}.fact_booking_daily fbd
  LEFT JOIN ${catalog}.${gold_schema}.dim_date dd 
    ON fbd.check_in_date = dd.date
  WHERE fbd.check_in_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    AND (property_id_filter IS NULL OR fbd.property_id = property_id_filter)
  ORDER BY ds, property_id;

