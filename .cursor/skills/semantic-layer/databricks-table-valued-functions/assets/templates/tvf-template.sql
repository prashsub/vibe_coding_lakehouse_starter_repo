-- Template for creating Table-Valued Functions (TVFs) for Genie Spaces
-- Replace <placeholders> with actual values

CREATE OR REPLACE FUNCTION <function_name>(
  -- Required parameters first (no DEFAULT)
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)',
  -- Optional parameters last (with DEFAULT)
  top_n INT DEFAULT 10 COMMENT 'Number of top results to return'
)
RETURNS TABLE(
  -- Every column documented
  rank INT COMMENT 'Rank by primary metric',
  <column1> <type> COMMENT '<description>',
  <column2> <type> COMMENT '<description>',
  <column3> <type> COMMENT '<description>'
)
COMMENT '
• PURPOSE: <One-line description of what the TVF does>
• BEST FOR: "<Question 1>" | "<Question 2>" | "<Question 3>"
• NOT FOR: <What to avoid> (use <correct_asset> instead) (optional)
• RETURNS: <PRE-AGGREGATED or Individual> rows (<column1>, <column2>, <column3>)
• PARAMS: start_date, end_date, top_n (default: 10)
• SYNTAX: SELECT * FROM <function_name>(''2024-01-01'', ''2024-12-31'', 10)
• NOTE: <Important caveats - DO NOT wrap in TABLE(), etc.> (optional)
'
RETURN
  WITH <cte_name> AS (
    SELECT 
      <columns>,
      SUM(<measure>) as <aggregated_measure>,
      ROW_NUMBER() OVER (ORDER BY <sort_column> DESC) as rank
    FROM <source_table>
    WHERE <date_column> BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY <group_by_columns>
  )
  SELECT 
    rank,
    <columns>,
    <aggregated_measure> / NULLIF(<denominator>, 0) as <calculated_measure>
  FROM <cte_name>
  WHERE rank <= top_n  -- ✅ Use WHERE instead of LIMIT
  ORDER BY rank;
