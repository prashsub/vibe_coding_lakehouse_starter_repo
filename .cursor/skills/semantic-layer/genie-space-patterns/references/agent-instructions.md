# Agent Instructions Guide

Comprehensive guide for writing effective Genie Space agent instructions.

## Core Principle: Business Context Drives AI Quality

**The quality of Genie responses directly correlates with the depth of business context provided in agent instructions.**

**Key Patterns:**
1. **Seven-Section Structure**: A→B→C→D→E→F→G (all required)
2. **Concise Instructions**: 20 lines max for LLM behavior rules
3. **Data Asset Hierarchy**: Metric Views (primary) → TVFs (specific) → Tables (reference)
4. **SQL Validation**: Every benchmark question has working SQL

---

## Two Levels of Instructions

**Level 1: General Instructions (MANDATORY - Section E)**
- **MAXIMUM 20 LINES** - Concise behavior rules
- Goes in the mandatory deliverable document
- Covers defaults, formatting, synonyms

**Level 2: Extended Instructions (OPTIONAL - for complex domains)**
- 200-500 lines of detailed business context
- Can be added to Genie Space for better responses
- Use template below if needed

---

## Extended Instructions Template (Optional)

```markdown
=================================================================================
[PROJECT NAME] - GENIE AGENT INSTRUCTIONS
=================================================================================

BUSINESS DOMAIN KNOWLEDGE:

1. [DOMAIN ENTITY 1]
   • [Key classification or concept]
   • [Identifiers used]
   • [Hierarchies or groupings]

2. [DOMAIN ENTITY 2]
   • [Types or categories]
   • [Business rules]

3. [TRANSACTION TYPES]
   • [Type 1]: [Description and business logic]
   • [Type 2]: [Description and business logic]

4. [PROGRAM/FEATURE 1]
   • [Component 1]: [Business definition]
   • [Component 2]: [Business definition]
   • [Metric]: [How calculated]

5. [DOMAIN CONCEPT]
   • [Classification 1]: [Definition and criteria]
   • [Classification 2]: [Definition and criteria]

6. [ANOTHER PROGRAM/FEATURE]
   • [Field 1]: [Description]
   • [Field 2]: [Description]
   • [Calculation]: [Formula]

7. KEY PERFORMANCE INDICATORS (KPIs)

   [Category 1] Metrics:
   • [Metric 1] = [Formula with clear variable definitions]
   • [Metric 2] = [Formula]
   
   [Category 2] Metrics:
   • [Metric 1] = [Formula]
   • [Metric 2] = [Formula]

8. TIME DIMENSIONS
   • [Hierarchy]: Year > Quarter > Month > Week > Day
   • [Fiscal periods description]
   • [Special time classifications]
   • Time Comparisons:
     - Week-over-Week (WoW)
     - Month-over-Month (MoM)
     - Quarter-over-Quarter (QoQ)
     - Year-over-Year (YoY)

9. GEOGRAPHIC ANALYSIS LEVELS
   • [Level 1]: [Description]
   • [Level 2]: [Description]
   • [Level 3]: [Description]

=================================================================================
DATA ASSETS AVAILABLE
=================================================================================

PRIMARY METRIC VIEWS (Use These First):

1. [metric_view_name]
   Purpose: [One-sentence description]
   Source: [Underlying fact table]
   Grain: [Aggregation level]
   Dimensions: [List key dimensions]
   Measures: [Count]+ measures including [examples]
   Window Measures: [List rolling windows, YoY]
   Best For: "[Example query pattern 1]", "[Example query pattern 2]"

TABLE-VALUED FUNCTIONS (Use for Specific Queries):

1. [function_name]([parameters])
   Returns: [Result description]
   Use When: [Specific scenario]
   Example: "[Natural language query example]"

=================================================================================
QUERY INTERPRETATION GUIDELINES
=================================================================================

1. TIME PERIOD HANDLING
   When user says:          Interpret as:
   • "this month"         → [SQL/filter logic]
   • "last month"         → [SQL/filter logic]
   • "this quarter"       → [SQL/filter logic]
   • "last 7 days"        → [SQL/filter logic or window measure]
   • "YTD"                → [SQL/filter logic]

2. AGGREGATION LEVEL DETECTION
   When user says:          Group by:
   • "by [dimension1]"   → [table.column]
   • "by [dimension2]"   → [table.column]
   • "by [dimension3]"   → [table.column]

3. RANKING AND LIMITS
   When user says:          Use:
   • "top 10"            → ORDER BY metric DESC LIMIT 10
   • "bottom 5"          → ORDER BY metric ASC LIMIT 5
   • "best performing"   → ORDER BY [primary_metric] DESC

4. COMPARISON KEYWORDS
   When user says:          Strategy:
   • "compare X vs Y"    → Use CASE WHEN or PIVOT
   • "growth"            → Calculate (current - prior) / prior * 100
   • "trend"             → ORDER BY date ASC
   • "vs last year"      → Join to prior year data

5. FILTER KEYWORDS
   When user says:          Filter:
   • "[brand/category1]" → [table.column] = '[value]'
   • "[classification1]" → [table.column] = [boolean/value]
   • "[status1]"         → [table.column] = '[value]'

6. METRIC SELECTION
   When user asks about:    Use measure:
   • "[term1]" / "[term2]" → [measure_name]
   • "[term3]" / "[term4]" → [measure_name]

7. AMBIGUITY RESOLUTION
   If user query is unclear:
   • Default to [most common metric] (not [alternative])
   • Default to [time period] if no time specified
   • Default to [scope] if no filter specified
   • Include [key identifiers] for clarity

8. HANDLING MISSING DATA
   • If metric view doesn't have requested data, check if TVF provides it
   • If neither works, query underlying gold tables
   • Always validate time period filters
   • If no data matches filters, return empty result with explanation

9. COMPLEX QUERIES
   For multi-part questions:
   • Break into subqueries
   • Use CTEs for readability
   • Combine metric views when crossing domains
   • Use window functions for ranking within groups

10. RESPONSE FORMAT
    Always include:
    • Clear column headers with business-friendly names
    • Proper formatting (currency, percentages, integers)
    • Sorted results (DESC for "top", ASC for "bottom")
    • Limited results (TOP N) for large datasets

=================================================================================
IMPORTANT CONSTRAINTS
=================================================================================

DATA QUALITY NOTES:
• [Layer] data has passed [validation process]
• [Special handling for edge cases]
• [Identification of special record types]

PERFORMANCE BEST PRACTICES:
• Use metric views instead of fact tables (pre-aggregated)
• Specify time period filters
• Use TOP N to limit result sets
• Leverage window_measures for rolling windows

BUSINESS RULES:
• [Rule 1 with formula]
• [Rule 2 with data type notes]
• [Rule 3 with SCD handling]

=================================================================================
EXAMPLE QUERY PATTERNS
=================================================================================

PATTERN 1: Top N with Time Filter
Question: "[Example natural language question]"
Strategy:
  FROM [metric_view]
  WHERE [time_filter]
  GROUP BY [dimension]
  ORDER BY MEASURE([metric]) DESC
  LIMIT N

[Include 4-5 more patterns covering different query types]

=================================================================================
TROUBLESHOOTING TIPS
=================================================================================

If query fails:
1. [Common issue 1 and fix]
2. [Common issue 2 and fix]
3. [Common issue 3 and fix]

If results seem wrong:
1. [Validation check 1]
2. [Validation check 2]
3. [Validation check 3]

=================================================================================
SYNONYMS AND ALIASES
=================================================================================

[Business Term 1]: [synonym1], [synonym2], [synonym3]
[Business Term 2]: [synonym1], [synonym2], [synonym3]

=================================================================================
END OF INSTRUCTIONS
=================================================================================
```

---

## Why This Structure?

| Section | Purpose | Impact on Genie Quality |
|---------|---------|------------------------|
| **Business Domain Knowledge** | Teaches Genie your business concepts | ⭐⭐⭐⭐⭐ Critical |
| **Data Assets Available** | Shows what data sources to use | ⭐⭐⭐⭐⭐ Critical |
| **Query Interpretation** | Maps natural language to SQL patterns | ⭐⭐⭐⭐⭐ Critical |
| **Constraints** | Prevents common errors | ⭐⭐⭐⭐ Very Important |
| **Example Patterns** | Provides concrete query templates | ⭐⭐⭐⭐ Very Important |
| **Troubleshooting** | Helps Genie recover from failures | ⭐⭐⭐ Important |
| **Synonyms** | Improves query understanding | ⭐⭐⭐ Important |

---

## Critical Patterns for General Instructions

### 1. General Instructions Consistency

**Issue:** Contradictory rules in General Instructions caused Genie to select wrong data assets.

**Prevention Patterns:**

#### Use Explicit Exceptions
```markdown
# GOOD: Clear exception handling
- Host demographics/verification → host_analytics_metrics (attributes only)
⚠️ HOST PERFORMANCE EXCEPTION: For "Top hosts", "Host revenue" → USE get_host_performance TVF
```

#### Group by Question Type, Not Asset
```markdown
# BAD: Asset-first (causes conflicts)
- host_analytics_metrics → for host data
- get_host_performance → for host data

# GOOD: Question-first (clear routing)
Revenue/booking questions:
  - By property → revenue_analytics_metrics
  - By host → get_host_performance TVF (not metric view!)
  - By customer → customer_analytics_metrics

Attribute/demographic questions:
  - Host attributes → host_analytics_metrics
  - Property inventory → property_analytics_metrics
```

#### Use ⚠️ Markers for Critical Routing
```markdown
⚠️ CRITICAL - Metric View Selection:
- Revenue by property type → revenue_analytics_metrics (fact source)
- NOT property_analytics_metrics (dimension source, under-reports)
```

---

### 2. Ambiguous Term Definitions

**Issue:** Subjective terms like "underperforming" had multiple valid interpretations.

**Common Ambiguous Terms:**

| Term | Interpretation 1 | Interpretation 2 |
|---|---|---|
| "underperforming" | Low revenue (some activity) | Zero activity (no bookings) |
| "top performing" | Highest revenue | Highest rating |
| "business vs leisure" | Account type (individual/business) | Trip purpose (is_business_booking) |
| "valuable customers" | Historical spend | Predicted LTV |
| "best hosts" | Most revenue | Highest rating |

**Resolution Pattern:**

```markdown
## Term Definitions

"underperforming" = properties with revenue below median (use get_underperforming_properties TVF)
"top performing" = highest revenue unless "rated" specified
"business vs leisure" = trip purpose (is_business_booking), NOT account type
"valuable customers" = 
  - Historical: use get_customer_ltv TVF
  - Predicted: use customer_ltv_predictions table
"best hosts" = highest revenue per property (use get_host_performance TVF)
```

---

### 3. Metric View vs TVF Routing

**Issue:** Genie selected metric views when TVFs were more appropriate (and vice versa).

**Routing Decision Table:**

| Question Pattern | Best Asset | Reason |
|---|---|---|
| "Show X" (general) | Metric View | No parameters needed |
| "X by [dimension]" | Metric View | Standard aggregation |
| "Top N [entities]" | TVF with `top_n` param | Parameterized ranking |
| "X for [specific date range]" | TVF with date params | Bounded query |
| "X trend for [period]" | TVF (e.g., `get_revenue_by_period`) | Time-series logic |
| "Who are the [entities]?" | TVF returning individuals | Individual rows needed |
| "How many [entities]?" | Metric View or aggregate TVF | Summary stats |
| "Compare X vs Y" | Metric View with GROUP BY | Segmentation |

**Add Routing Rules to General Instructions:**

```markdown
## Query Routing

Revenue questions:
  - General revenue → revenue_analytics_metrics
  - Revenue by time period → get_revenue_by_period TVF
  - Revenue by host → get_host_performance TVF (NOT host_analytics_metrics!)

Customer questions:
  - Customer segments (summary) → get_customer_segments TVF
  - Individual VIP customers → get_customer_ltv TVF
  - Predicted customer value → customer_ltv_predictions table

Host questions:
  - Host demographics → host_analytics_metrics
  - Host revenue/bookings → get_host_performance TVF ⚠️

Property questions:
  - Property counts/inventory → property_analytics_metrics
  - Property performance → get_property_performance TVF
```

---

### 4. TVF Syntax Guidance

**Issue:** Genie wrapped TVFs incorrectly or added unnecessary GROUP BY.

**Common Errors to Prevent:**

```sql
-- ❌ TABLE() wrapper
SELECT * FROM TABLE(get_customer_segments('2020-01-01', '2024-12-31'))
-- Error: NOT_A_SCALAR_FUNCTION

-- ❌ Missing parameters  
SELECT * FROM get_customer_segments()
-- Error: WRONG_NUM_ARGS

-- ❌ GROUP BY on pre-aggregated TVF
SELECT segment_name, COUNT(*) FROM get_customer_segments(...) GROUP BY segment_name
-- Result: Same as without GROUP BY, but confusing
```

**Add Syntax Rules to General Instructions:**

```markdown
## TVF Syntax Rules

1. NEVER wrap TVFs in TABLE() - just call directly:
   ✅ SELECT * FROM get_customer_segments('2020-01-01', '2024-12-31')
   ❌ SELECT * FROM TABLE(get_customer_segments(...))

2. Include required parameters (check TVF signature):
   ✅ get_customer_ltv('2020-01-01', '2024-12-31', 100)
   ❌ get_customer_ltv()

3. Don't GROUP BY on aggregate TVFs - they're pre-aggregated:
   - get_customer_segments: Returns 5 segment rows (already grouped)
   - get_vip_customers: Returns segment stats (already grouped)
   - get_revenue_by_period: Returns time periods (already grouped)
```

---

### 5. Professional Language Standards

**Issue:** Instructions with negative language about assets confused Genie.

**❌ Avoid:**
```markdown
- Don't use host_analytics_metrics - it's broken for revenue
- The metric view returns wrong results so use the TVF
- host_analytics_metrics doesn't work properly
```

**✅ Use:**
```markdown
- Host revenue/bookings → get_host_performance TVF (accurate join path)
- Host attributes/demographics → host_analytics_metrics

⚠️ CRITICAL: get_host_performance TVF is PREFERRED for host revenue metrics
```

---

## Common Mistakes to Avoid

### ❌ DON'T: General Instructions > 20 Lines
```markdown
# BAD: 50+ lines of instructions
Instructions:
[Line 1]
[Line 2]
...
[Line 50]  # ❌ TOO LONG - Genie won't read all of this effectively
```

### ✅ DO: Concise 20-Line General Instructions
```markdown
# GOOD: Exactly 20 lines or less
## General Instructions

You are an expert analyst. Follow these rules:

1. **Primary Data:** Use Metric Views first
2. **TVFs:** Prefer TVFs for common queries
3. **Dates:** Default to last 30 days
4. **Sorting:** DESC by primary metric
5. **Limits:** Top 10-20 for rankings
[... up to 20 lines total]
```

---

## Benchmark Questions Pattern

### Organization by Business Function

Create 20-30 benchmark questions organized by business domain:

```markdown
### **Category 1: [Business Function Name]**

#### Q1.1: [Question Topic]
**Business Question:**
```
[Natural language question as user would ask]
```

**Expected Genie Query Strategy:**
- Metric View: `[metric_view_name]`
- Filter: `[SQL conditions or description]`
- Group By: `[dimensions]`
- Measure: `[metric expression]`
- Sort: `[ORDER BY clause]`
- Limit: `[LIMIT clause if applicable]`

**Expected Answer Format:**
| [Column 1] | [Column 2] | [Column 3] | [Column 4] |
|------------|------------|------------|------------|
| [Example 1] | [Data] | [Data] | [Data] |
| [Example 2] | [Data] | [Data] | [Data] |

**Validation Criteria:**
✓ [Check 1]
✓ [Check 2]
✓ [Check 3]
```

### Question Categories by Complexity

**Simple (Single dimension, single metric):**
- "What are the top 10 [entities] by [metric]?"
- "Show me [metric] by [dimension]"

**Moderate (Multiple dimensions, time filters):**
- "Compare [metric] for [filter1] vs [filter2]"
- "Show [metric] by [dimension] for [time_period]"

**Advanced (Multi-metric, calculated fields, joins):**
- "Show [entities] with high [metric1] but low [metric2]"
- "Compare [metric1] and [metric2] across [dimension1] and [dimension2]"

**Complex (Cross-domain, window functions, multiple data sources):**
- "Show [metric] trend with [comparison] for [filtered_entities]"
- "Analyze [dimension1] by [dimension2] with [calculated_metric]"

### Minimum Coverage

Ensure benchmark questions cover:
- [ ] All primary metric views (at least 3 questions each)
- [ ] All TVFs (at least 1 question each)
- [ ] Common time periods (this month, last quarter, YTD, rolling windows)
- [ ] All major dimensions (geographic, product, time, customer segments)
- [ ] Key business calculations (growth %, rates, averages, rankings)
- [ ] Edge cases (missing data, zero values, negative values)
- [ ] Multi-dimensional analysis (2+ dimensions combined)
