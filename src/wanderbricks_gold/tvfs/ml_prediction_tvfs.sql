-- =============================================================================
-- ML Model Prediction TVFs for Genie Space Integration
-- =============================================================================
-- These TVFs provide natural language access to ML model predictions
-- Reference: https://docs.databricks.com/aws/en/genie/trusted-assets#tips-for-writing-functions

-- =============================================================================
-- 1. DEMAND PREDICTIONS TVF
-- =============================================================================
-- Purpose: Get predicted booking demand by destination
-- Sample questions:
--   "What are the demand predictions for Miami?"
--   "Show me high-demand destinations for next month"
--   "Which destinations have the highest predicted bookings?"
-- Note: Groups by destination since batch inference doesn't preserve property_id

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_demand_predictions(
    p_destination_id BIGINT DEFAULT NULL,
    p_min_predicted_bookings DECIMAL(10,2) DEFAULT 0
)
RETURNS TABLE (
    destination_id BIGINT,
    property_type INT,
    avg_predicted_bookings FLOAT,
    max_predicted_bookings FLOAT,
    prediction_count BIGINT,
    scoring_date DATE,
    model_name STRING
)
LANGUAGE SQL
COMMENT '
• PURPOSE: ML-predicted booking demand aggregated by destination
• BEST FOR: "What destinations have high predicted demand?" | "Demand predictions by destination"
• NOT FOR: Individual property demand (query demand_predictions table directly)
• RETURNS: PRE-AGGREGATED rows (destination_id, property_type, avg_predicted_bookings)
• PARAMS: p_destination_id (optional), p_min_predicted_bookings (default: 0)
• SYNTAX: SELECT * FROM get_demand_predictions()
'
RETURN
    SELECT 
        destination_id,
        property_type,
        AVG(predicted_bookings) AS avg_predicted_bookings,
        MAX(predicted_bookings) AS max_predicted_bookings,
        COUNT(*) AS prediction_count,
        MAX(scoring_date) AS scoring_date,
        MAX(model_name) AS model_name
    FROM ${catalog}.${ml_schema}.demand_predictions
    WHERE (p_destination_id IS NULL OR destination_id = p_destination_id)
      AND predicted_bookings >= p_min_predicted_bookings
    GROUP BY destination_id, property_type
    ORDER BY avg_predicted_bookings DESC
    LIMIT 1000;


-- =============================================================================
-- 2. CONVERSION PREDICTIONS TVF
-- =============================================================================
-- Purpose: Get predicted conversion probability by destination/property type
-- Sample questions:
--   "Which destinations have high conversion likelihood?"
--   "Show me property types with conversion probability above 70%"
--   "What's the average conversion prediction by destination?"
-- Note: Groups by destination_id since batch inference doesn't preserve property_id
-- Note: conversion_probability stored as BIGINT (0-100 scale or similar)

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_conversion_predictions(
    p_min_probability BIGINT DEFAULT 0,
    p_destination_id BIGINT DEFAULT NULL
)
RETURNS TABLE (
    destination_id BIGINT,
    property_type INT,
    avg_conversion_probability DOUBLE,
    max_conversion_probability BIGINT,
    predicted_conversion_rate DOUBLE,
    prediction_count BIGINT,
    scoring_date DATE,
    model_name STRING
)
LANGUAGE SQL
COMMENT '
• PURPOSE: ML-predicted booking conversion probability by destination
• BEST FOR: "Which destinations have high conversion?" | "Conversion predictions" | "Likely to book"
• RETURNS: PRE-AGGREGATED rows (destination_id, property_type, avg_conversion_probability)
• PARAMS: p_min_probability (default: 0), p_destination_id (optional)
• SYNTAX: SELECT * FROM get_conversion_predictions()
'
RETURN
    SELECT 
        destination_id,
        property_type,
        AVG(CAST(conversion_probability AS DOUBLE)) AS avg_conversion_probability,
        MAX(conversion_probability) AS max_conversion_probability,
        AVG(CAST(predicted_conversion AS DOUBLE)) AS predicted_conversion_rate,
        COUNT(*) AS prediction_count,
        MAX(scoring_date) AS scoring_date,
        MAX(model_name) AS model_name
    FROM ${catalog}.${ml_schema}.conversion_predictions
    WHERE conversion_probability >= p_min_probability
      AND (p_destination_id IS NULL OR destination_id = p_destination_id)
    GROUP BY destination_id, property_type
    ORDER BY avg_conversion_probability DESC
    LIMIT 1000;


-- =============================================================================
-- 3. PRICING RECOMMENDATIONS TVF
-- =============================================================================
-- Purpose: Get optimal pricing recommendations by month, quarter, and season
-- Sample questions:
--   "What are the recommended prices for peak season?"
--   "Show pricing recommendations by month"
--   "What's the average recommended price by quarter?"
-- Note: Table only has temporal features (month, quarter, is_peak_season) + price

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_pricing_recommendations(
    p_month INT DEFAULT NULL,
    p_is_peak_season INT DEFAULT NULL
)
RETURNS TABLE (
    month INT,
    quarter INT,
    is_peak_season INT,
    avg_recommended_price DOUBLE,
    min_recommended_price DOUBLE,
    max_recommended_price DOUBLE,
    prediction_count BIGINT,
    scoring_date DATE,
    model_name STRING
)
LANGUAGE SQL
COMMENT '
• PURPOSE: ML-optimized pricing recommendations aggregated by month/season
• BEST FOR: "Seasonal pricing recommendations" | "Optimal prices for peak season"
• NOT FOR: Pricing by destination (use get_pricing_by_destination instead)
• RETURNS: PRE-AGGREGATED rows (month, quarter, is_peak_season, avg_recommended_price)
• PARAMS: p_month (optional), p_is_peak_season (optional)
• SYNTAX: SELECT * FROM get_pricing_recommendations()
'
RETURN
    SELECT 
        month,
        quarter,
        is_peak_season,
        AVG(recommended_price) AS avg_recommended_price,
        MIN(recommended_price) AS min_recommended_price,
        MAX(recommended_price) AS max_recommended_price,
        COUNT(*) AS prediction_count,
        MAX(scoring_date) AS scoring_date,
        MAX(model_name) AS model_name
    FROM ${catalog}.${ml_schema}.pricing_recommendations
    WHERE (p_month IS NULL OR month = p_month)
      AND (p_is_peak_season IS NULL OR is_peak_season = p_is_peak_season)
    GROUP BY month, quarter, is_peak_season
    ORDER BY avg_recommended_price DESC
    LIMIT 1000;


-- =============================================================================
-- 3b. PRICING BY DESTINATION TVF
-- =============================================================================
-- Purpose: Get pricing recommendations for properties in a specific destination
-- Sample questions:
--   "What price should I set for Miami properties?"
--   "Show pricing for Paris properties"
--   "Recommended prices for New York"

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_pricing_by_destination(
    p_destination STRING COMMENT 'Destination name (e.g., Miami, Paris, New York)'
)
RETURNS TABLE (
    destination STRING,
    property_type STRING,
    property_count BIGINT,
    avg_base_price DECIMAL(18,2),
    min_base_price DECIMAL(18,2),
    max_base_price DECIMAL(18,2),
    ml_seasonal_adjustment DOUBLE,
    recommended_price_range STRING
)
LANGUAGE SQL
COMMENT '
• PURPOSE: Pricing recommendations for properties in a specific destination
• BEST FOR: "What price for Miami properties?" | "Pricing for Paris" | "Recommended price by destination"
• RETURNS: PRE-AGGREGATED rows (destination, property_type, property_count, avg_base_price, recommended_price_range)
• PARAMS: p_destination (required - e.g., ''Miami'', ''Paris'')
• SYNTAX: SELECT * FROM get_pricing_by_destination(''Miami'')
• NOTE: Combines property base prices with ML seasonal adjustments
'
RETURN
    WITH property_prices AS (
        SELECT 
            dd.destination,
            dp.property_type,
            COUNT(*) as property_count,
            AVG(dp.base_price) as avg_base_price,
            MIN(dp.base_price) as min_base_price,
            MAX(dp.base_price) as max_base_price
        FROM ${catalog}.${gold_schema}.dim_property dp
        JOIN ${catalog}.${gold_schema}.dim_destination dd ON dp.destination_id = dd.destination_id
        WHERE dp.is_current = true
          AND LOWER(dd.destination) LIKE CONCAT('%', LOWER(p_destination), '%')
        GROUP BY dd.destination, dp.property_type
    ),
    seasonal_adjustment AS (
        SELECT AVG(recommended_price) / 100 as adjustment_factor
        FROM ${catalog}.${ml_schema}.pricing_recommendations
        WHERE month = MONTH(CURRENT_DATE)
    )
    SELECT 
        pp.destination,
        pp.property_type,
        pp.property_count,
        pp.avg_base_price,
        pp.min_base_price,
        pp.max_base_price,
        COALESCE(sa.adjustment_factor, 1.0) as ml_seasonal_adjustment,
        CONCAT('$', CAST(ROUND(pp.min_base_price * COALESCE(sa.adjustment_factor, 1.0)) AS STRING), 
               ' - $', CAST(ROUND(pp.max_base_price * COALESCE(sa.adjustment_factor, 1.0)) AS STRING)) as recommended_price_range
    FROM property_prices pp
    CROSS JOIN seasonal_adjustment sa
    ORDER BY pp.avg_base_price DESC;


-- =============================================================================
-- 4. CUSTOMER LTV PREDICTIONS TVF
-- =============================================================================
-- Purpose: Get predicted lifetime value distribution by segment
-- Sample questions:
--   "What's the LTV distribution by segment?"
--   "Show high-value customer predictions"
--   "How many customers are in each LTV segment?"
-- Note: Groups by segment since batch inference may not preserve user_id

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_customer_ltv_predictions(
    p_ltv_segment STRING DEFAULT NULL,
    p_min_ltv DECIMAL(18,2) DEFAULT 0
)
RETURNS TABLE (
    ltv_segment STRING,
    avg_predicted_ltv_12m FLOAT,
    min_predicted_ltv_12m FLOAT,
    max_predicted_ltv_12m FLOAT,
    customer_count BIGINT,
    scoring_date DATE,
    model_name STRING
)
LANGUAGE SQL
COMMENT '
• PURPOSE: ML-predicted 12-month lifetime value aggregated by segment
• BEST FOR: "LTV by segment" | "Customer value distribution" | "Predicted customer value"
• NOT FOR: Individual customers (use get_customer_ltv TVF or customer_ltv_predictions table)
• RETURNS: PRE-AGGREGATED rows (ltv_segment, avg_predicted_ltv_12m, customer_count)
• PARAMS: p_ltv_segment (optional), p_min_ltv (default: 0)
• SYNTAX: SELECT * FROM get_customer_ltv_predictions()
• NOTE: Segments: VIP (>$2500), High ($1000-2500), Medium ($500-1000), Low (<$500)
'
RETURN
    SELECT 
        ltv_segment,
        AVG(predicted_ltv_12m) AS avg_predicted_ltv_12m,
        MIN(predicted_ltv_12m) AS min_predicted_ltv_12m,
        MAX(predicted_ltv_12m) AS max_predicted_ltv_12m,
        COUNT(*) AS customer_count,
        MAX(scoring_date) AS scoring_date,
        MAX(model_name) AS model_name
    FROM ${catalog}.${ml_schema}.customer_ltv_predictions
    WHERE (p_ltv_segment IS NULL OR ltv_segment = p_ltv_segment)
      AND predicted_ltv_12m >= p_min_ltv
    GROUP BY ltv_segment
    ORDER BY avg_predicted_ltv_12m DESC
    LIMIT 1000;


-- =============================================================================
-- 5. VIP CUSTOMERS SUMMARY TVF
-- =============================================================================
-- Purpose: Quick summary of VIP customer segment
-- Sample questions:
--   "How many VIP customers do we have?"
--   "What's the average VIP customer value?"

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_vip_customers()
RETURNS TABLE (
    ltv_segment STRING,
    vip_customer_count BIGINT,
    avg_predicted_ltv_12m FLOAT,
    min_predicted_ltv_12m FLOAT,
    max_predicted_ltv_12m FLOAT,
    scoring_date DATE
)
LANGUAGE SQL
COMMENT '
• PURPOSE: VIP segment aggregate statistics (count, average LTV)
• BEST FOR: "How many VIP customers?" | "VIP segment summary"
• NOT FOR: Individual VIP customers (use get_customer_ltv or customer_ltv_predictions table)
• RETURNS: 1 PRE-AGGREGATED row (ltv_segment, customer_count, avg_predicted_ltv)
• SYNTAX: SELECT * FROM get_vip_customers()
'
RETURN
    SELECT 
        ltv_segment,
        COUNT(*) AS vip_customer_count,
        AVG(predicted_ltv_12m) AS avg_predicted_ltv_12m,
        MIN(predicted_ltv_12m) AS min_predicted_ltv_12m,
        MAX(predicted_ltv_12m) AS max_predicted_ltv_12m,
        MAX(scoring_date) AS scoring_date
    FROM ${catalog}.${ml_schema}.customer_ltv_predictions
    WHERE ltv_segment = 'VIP'
    GROUP BY ltv_segment;


-- =============================================================================
-- 6. HIGH DEMAND DESTINATIONS SHORTCUT TVF
-- =============================================================================
-- Purpose: Quick access to high-demand destinations by property type
-- Sample questions:
--   "Which destinations have high demand?"
--   "Show popular destinations"

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_high_demand_properties(
    p_top_n INT DEFAULT 100
)
RETURNS TABLE (
    rank BIGINT,
    destination_id BIGINT,
    property_type INT,
    avg_predicted_bookings FLOAT,
    max_predicted_bookings FLOAT,
    property_count BIGINT,
    scoring_date DATE
)
LANGUAGE SQL
COMMENT '
• PURPOSE: Top destinations by ML-predicted booking demand
• BEST FOR: "Which destinations have high demand?" | "Top high-demand destinations"
• NOT FOR: Individual properties (query demand_predictions table directly)
• RETURNS: PRE-AGGREGATED rows (rank, destination_id, property_type, avg_predicted_bookings)
• PARAMS: p_top_n (default: 100)
• SYNTAX: SELECT * FROM get_high_demand_properties(20)
'
RETURN
    WITH ranked AS (
        SELECT 
            destination_id,
            property_type,
            AVG(predicted_bookings) AS avg_predicted_bookings,
            MAX(predicted_bookings) AS max_predicted_bookings,
            COUNT(*) AS property_count,
            MAX(scoring_date) AS scoring_date,
            ROW_NUMBER() OVER (ORDER BY AVG(predicted_bookings) DESC) AS rank
        FROM ${catalog}.${ml_schema}.demand_predictions
        GROUP BY destination_id, property_type
    )
    SELECT rank, destination_id, property_type, avg_predicted_bookings, 
           max_predicted_bookings, property_count, scoring_date
    FROM ranked
    WHERE rank <= p_top_n
    ORDER BY rank;


-- =============================================================================
-- 7. CUSTOMER SEGMENT DISTRIBUTION TVF
-- =============================================================================
-- Purpose: Get distribution of detailed customer segments for targeting
-- Sample questions:
--   "What is the customer segment distribution?"
--   "How many high-value customers do we have?"
--   "Show me at-risk customers"
--   "What's the breakdown of customer segments?"

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_customer_segment_distribution()
RETURNS TABLE (
    segment_name STRING,
    segment_description STRING,
    customer_count BIGINT,
    pct_of_total DOUBLE,
    avg_ltv DOUBLE,
    avg_total_bookings DOUBLE,
    avg_total_spend DOUBLE,
    scoring_date DATE
)
LANGUAGE SQL
COMMENT 'Returns distribution of detailed customer segments: High-Value, At-Risk, Repeat Travelers, Price-Sensitive, New Prospects. Use: "What is the customer segment distribution?" or "How many high-value customers?"'
RETURN
    WITH total_customers AS (
        SELECT COUNT(*) as total FROM ${catalog}.${ml_schema}.customer_ltv_predictions
    ),
    segments AS (
        SELECT 
            CASE 
                WHEN predicted_ltv_12m > 2500 AND total_bookings >= 5 THEN 'High-Value Customers'
                WHEN days_since_last_booking > 90 OR cancellation_rate > 0.3 THEN 'At-Risk Customers'
                WHEN total_bookings >= 3 AND is_repeat > 0 THEN 'Repeat Travelers'
                WHEN avg_booking_value < 200 THEN 'Price-Sensitive'
                WHEN total_bookings < 2 AND tenure_days < 30 THEN 'New Prospects'
                ELSE 'Standard Customers'
            END AS segment_name,
            predicted_ltv_12m,
            total_bookings,
            total_spend,
            scoring_date
        FROM ${catalog}.${ml_schema}.customer_ltv_predictions
    )
    SELECT 
        s.segment_name,
        CASE s.segment_name
            WHEN 'High-Value Customers' THEN 'VIP treatment, loyalty programs - LTV > $2500 and 5+ bookings'
            WHEN 'At-Risk Customers' THEN 'Win-back campaigns - 90+ days inactive or high cancellation'
            WHEN 'Repeat Travelers' THEN 'Loyalty rewards - 3+ bookings with repeat behavior'
            WHEN 'Price-Sensitive' THEN 'Discount campaigns - avg booking < $200'
            WHEN 'New Prospects' THEN 'Onboarding incentives - <2 bookings, <30 days tenure'
            ELSE 'Standard customer base'
        END AS segment_description,
        COUNT(*) AS customer_count,
        ROUND(COUNT(*) * 100.0 / t.total, 2) AS pct_of_total,
        ROUND(AVG(s.predicted_ltv_12m), 2) AS avg_ltv,
        ROUND(AVG(s.total_bookings), 2) AS avg_total_bookings,
        ROUND(AVG(s.total_spend), 2) AS avg_total_spend,
        MAX(s.scoring_date) AS scoring_date
    FROM segments s
    CROSS JOIN total_customers t
    GROUP BY s.segment_name, t.total
    ORDER BY customer_count DESC;


-- =============================================================================
-- 8. ML MODEL PERFORMANCE SUMMARY TVF
-- =============================================================================
-- Purpose: Get summary of all ML predictions
-- Sample questions:
--   "Show me ML model summary"
--   "What predictions are available?"
--   "How many predictions do we have?"

CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_ml_predictions_summary()
RETURNS TABLE (
    model_name STRING,
    prediction_count BIGINT,
    latest_scoring_date DATE,
    description STRING
)
LANGUAGE SQL
COMMENT '
• PURPOSE: Summary of all available ML model predictions
• BEST FOR: "What ML models are available?" | "Show ML predictions summary" | "ML model overview"
• RETURNS: PRE-AGGREGATED rows (model_name, prediction_count, latest_scoring_date, description)
• SYNTAX: SELECT * FROM get_ml_predictions_summary()
'
RETURN
    SELECT 
        'demand_predictor' as model_name,
        COUNT(*) as prediction_count,
        MAX(scoring_date) as latest_scoring_date,
        'Predicts booking demand by property' as description
    FROM ${catalog}.${ml_schema}.demand_predictions
    
    UNION ALL
    
    SELECT 
        'conversion_predictor' as model_name,
        COUNT(*) as prediction_count,
        MAX(scoring_date) as latest_scoring_date,
        'Predicts booking conversion probability' as description
    FROM ${catalog}.${ml_schema}.conversion_predictions
    
    UNION ALL
    
    SELECT 
        'pricing_optimizer' as model_name,
        COUNT(*) as prediction_count,
        MAX(scoring_date) as latest_scoring_date,
        'Recommends optimal property prices' as description
    FROM ${catalog}.${ml_schema}.pricing_recommendations
    
    UNION ALL
    
    SELECT 
        'customer_ltv_predictor' as model_name,
        COUNT(*) as prediction_count,
        MAX(scoring_date) as latest_scoring_date,
        'Predicts customer 12-month lifetime value' as description
    FROM ${catalog}.${ml_schema}.customer_ltv_predictions;

