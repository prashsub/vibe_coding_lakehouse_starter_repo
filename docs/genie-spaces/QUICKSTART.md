# Wanderbricks Genie Spaces - Quick Reference

## 5-Minute Setup

### Step 1: Create Genie Space in UI

1. Navigate to **Databricks Workspace → Genie → Create New Space**
2. Use names and descriptions from [GENIE_SPACE_SETUP_COMPLETE.md](./GENIE_SPACE_SETUP_COMPLETE.md)

### Step 2: Add Trusted Assets

For each space, add in this order:

| Space | Metric View | TVFs | Dimension Tables |
|-------|-------------|------|------------------|
| Revenue | `revenue_analytics_metrics` | 6 | dim_property, dim_destination, dim_date |
| Marketing | `engagement_analytics_metrics` | 5 | dim_property, dim_date |
| Property | `property_analytics_metrics` | 5 | dim_property, dim_destination, dim_host |
| Host | `host_analytics_metrics` | 5 | dim_host, dim_property |
| Customer | `customer_analytics_metrics` | 5 | dim_user |

### Step 3: Add Agent Instructions

Copy the 15-line instructions from Section E of each space.

### Step 4: Test

Run the 10 benchmark questions from Section G and verify SQL matches.

---

## Genie Spaces Summary

| Space | Primary Use | Key TVFs |
|-------|-------------|----------|
| **Revenue Intelligence** | Revenue trends, booking analysis, cancellations | `get_revenue_by_period`, `get_top_properties_by_revenue` |
| **Marketing Intelligence** | Engagement funnels, conversion optimization | `get_conversion_funnel`, `get_property_engagement` |
| **Property Intelligence** | Portfolio management, pricing strategy | `get_property_performance`, `get_pricing_analysis` |
| **Host Intelligence** | Partner management, host quality | `get_host_performance`, `get_host_quality_metrics` |
| **Customer Intelligence** | Segmentation, LTV, behavior | `get_customer_segments`, `get_customer_ltv` |

---

## Sample Questions by Domain

### Revenue
- "What was total revenue last month?"
- "Top 10 properties by revenue"
- "Cancellation rate by destination"

### Marketing
- "What is our conversion rate?"
- "Show the view-to-booking funnel"
- "Which properties have highest engagement?"

### Property
- "How many properties do we have?"
- "Average price by destination"
- "Which properties are underperforming?"

### Host
- "Who are our top performing hosts?"
- "How many verified hosts do we have?"
- "Multi-property hosts"

### Customer
- "What are our customer segments?"
- "Who are our most valuable customers?"
- "Business vs leisure breakdown"

---

## Full Documentation

See [GENIE_SPACE_SETUP_COMPLETE.md](./GENIE_SPACE_SETUP_COMPLETE.md) for:
- Complete 7-section configurations
- All TVF signatures and examples
- 50 benchmark questions with SQL
- Deployment checklist


