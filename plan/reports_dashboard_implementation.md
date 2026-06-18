# Reports Dashboard Implementation Plan

## Executive Summary

This plan transforms the existing fragmented reporting infrastructure into a unified "Command Center" style Reports Section per the PRD. The codebase already has ~60% of the required pieces (APIs, components, routing). This plan fills the gaps, consolidates duplicates, and delivers the premium, best-in-class experience.

---

## Current State Analysis

### What Already Exists (Reusable)

| PRD Requirement | Existing Asset | Status |
|---|---|---|
| Hero KPI Cards | `KPICard.vue` + `RevenueHeroCard.vue` | Partial - missing PoP comparison |
| Time Toggles | Date pickers in `ProfitIntelligence.vue` | Fragmented - needs global state |
| Hourly Sales Chart | `Revenue.vue` + `HourlyBarChart.vue` | Complete |
| Category Breakdown | `Revenue.vue` category bars | Complete |
| Team Scoreboard | `WorkforceIntelligence.vue` | Complete |
| Profit Overview | `ProfitIntelligence.vue` + store | Complete |
| Margin Heatmap | `MarginHeatmap.vue` | Complete |
| EChart Wrapper | `EChart.vue` | Complete |
| Role-based RBAC | Router + `getAccessTier()` | Complete |
| Report Catalog | `reports.py` REPORT_CATALOG | Complete |

### What Needs to Be Built

| PRD Requirement | Gap | Priority |
|---|---|---|
| **Executive Overview Page** | New unified landing page with aggregated KPIs | P0 |
| **Global Date Range State** | Pinia store for persistent date selection across tabs | P0 |
| **Period-over-Period Comparisons** | KPI cards need `+X% vs last week` indicators | P0 |
| **Sales Monitor Page** | New page with real-time pulse + product tables | P0 |
| **Dead Stock / Slow Movers Table** | New API + table component | P1 |
| **Profit Waterfall Chart** | New visualization component | P1 |
| **Payment Method Pie Chart** | New chart component | P1 |
| **Customer Mix (New vs Returning)** | New API endpoint + visualization | P2 |
| **Workforce Heatmap** | Sales Volume vs Staffing Levels visualization | P2 |
| **Auto-Refresh / Real-Time Feed** | WebSocket integration for Sales Monitor | P1 |
| **Skeleton Loaders** | Consistent loading states across all pages | P1 |
| **Empty States** | Beautiful "No Data" graphics | P2 |

---

## Architecture

### 1. Navigation Structure (Per PRD §4)

```
Reports (Parent Menu)
├── Report (Executive Overview)     ← /reports/dashboards/executive
├── Sales Monitor                   ← /reports/dashboards/sales-monitor
├── Profit Intelligence             ← /reports/dashboards/profit (EXISTING)
└── Workforce Intelligence          ← /reports/dashboards/workforce (EXISTING)
```

### 2. Component Tree

```
pages/reports/
├── ExecutiveOverview.vue           ← NEW: Main landing page
├── SalesMonitor.vue                ← NEW: Sales deep-dive
├── AnalyticsHub.vue                ← EXISTING: Keep as report catalog
└── ...

components/reports/
├── KPICard.vue                     ← ENHANCE: Add PoP comparison
├── HeroMetric.vue                  ← NEW: KPI card with period comparison
├── DateRangeToggle.vue             ← NEW: Global time toggles
├── SalesTrendChart.vue             ← NEW: Line/area chart for executive overview
├── HourlySalesChart.vue            ← NEW: Bar chart for sales monitor
├── CategoryDonut.vue               ← NEW: Donut chart for category breakdown
├── RealTimeFeed.vue                ← NEW: Auto-refreshing sales feed
├── ProductPerformanceTable.vue     ← NEW: Top/bottom items table
├── WaterfallChart.vue              ← NEW: Revenue → Profit waterfall
├── PaymentMethodPie.vue            ← NEW: Payment breakdown pie
├── StaffHeatmap.vue                ← NEW: Sales vs staffing heatmap
└── EmptyState.vue                  ← NEW: Beautiful empty state graphic

stores/
├── reports.js                      ← NEW: Global date range + report state
├── analyticsHub.js                 ← EXISTING
└── profit.js                       ← EXISTING

composables/analytics/
├── useDateRange.vue                ← NEW: Shared date range logic
├── useAutoRefresh.vue              ← NEW: Polling/WebSocket composable
└── useReportData.vue               ← NEW: Generic data fetching with loading/error
```

### 3. Backend API Map

| API Endpoint | Purpose | Data Source |
|---|---|---|
| `get_executive_overview` | Hero KPIs with PoP | `Sales Invoice` + `Sale Cost Breakdown` |
| `get_sales_trend` | Daily trend data | `Daily Store Sales Rollup` (already exists) |
| `get_sales_monitor_summary` | Live sales KPIs | Delegates to `sales_monitor.get_summary` |
| `get_sales_monitor_hourly` | Hourly breakdown | Delegates to `sales_monitor.get_hourly` |
| `get_sales_monitor_top_bottom` | Top 5 / Dead stock | `Sales Invoice Item` + `Bin` |
| `get_profit_waterfall` | Waterfall data | Delegates to `profit_intelligence.get_margin_waterfall` |
| `get_profit_payment_methods` | Payment breakdown | `Sales Invoice Payment` |
| `get_profit_customer_mix` | New vs returning | `Customer` + `Sales Invoice` |
| `get_workforce_enriched` | Full workforce data | Delegates to `workforce.get_team_scorecard` + extras |

---

## Implementation Phases

### Phase 1: Foundation (Day 1-2)

#### 1.1 Global Date Range Store

**File:** `src/stores/reports.js`

```javascript
// Pinia store for persistent date range across all report sub-pages
// PRD §5.A: "Must persist state across sub-pages"

export const useReportsStore = defineStore('reports', () => {
  const dateRange = ref({
    preset: 'today',     // 'today' | 'week' | 'month' | 'ytd' | 'custom'
    from: today(),
    to: today(),
  })
  const selectedStore = ref(null)

  function setPreset(preset) {
    const now = new Date()
    const ranges = {
      today: { from: today(), to: today() },
      week: { from: startOfWeek(now), to: today() },
      month: { from: startOfMonth(now), to: today() },
      yoy: { from: startOfYear(now), to: today() },
    }
    dateRange.value = { preset, ...ranges[preset] }
  }

  function setCustom(from, to) {
    dateRange.value = { preset: 'custom', from, to }
  }

  return { dateRange, selectedStore, setPreset, setCustom }
})
```

#### 1.2 Enhanced KPICard with PoP Comparison

**File:** `src/components/reports/KPICard.vue` (modify existing)

Add props:
- `previousValue` - prior period value
- `comparisonLabel` - e.g., "vs last week"
- `trend` - 'up' | 'down' | 'flat'

Visual: Small green/red badge showing `+5.2%` with trend arrow.

#### 1.3 DateRangeToggle Component

**File:** `src/components/reports/DateRangeToggle.vue` (new)

Preset buttons: Today | This Week | This Month | YTD | Custom
- Reads/writes to `useReportsStore().dateRange`
- Custom opens inline date pickers

---

### Phase 2: Executive Overview (Day 2-3)

#### 2.1 Backend API

**File:** `zevar_core/api/reports_dashboard.py` (new)

```python
@frappe.whitelist()
def get_executive_overview(from_date=None, to_date=None, store=None):
    """Hero KPIs with period-over-period comparison."""
    # 1. Current period metrics
    #    - GTV / Net Sales
    #    - Total Transactions
    #    - Gross Profit Margin %
    # 2. Previous period (same duration, immediately before)
    # 3. Compute PoP deltas

    return {
        "current": { "net_sales": ..., "transactions": ..., "gross_margin_pct": ... },
        "previous": { "net_sales": ..., "transactions": ..., "gross_margin_pct": ... },
        "pop": { "net_sales_pct": ..., "transactions_pct": ..., "gross_margin_delta": ... },
        "period": { "from": ..., "to": ..., "prev_from": ..., "prev_to": ... },
    }
```

**SQL Strategy:**
- Query `tabSales Invoice` (is_pos=1, docstatus=1) for current period
- Query same duration immediately before for comparison
- JOIN `tabSale Cost Breakdown` for gross margin
- Support optional `set_warehouse` store filter

#### 2.2 Executive Overview Page

**File:** `src/pages/reports/ExecutiveOverview.vue` (new)

Layout:
```
┌─────────────────────────────────────────────────┐
│  [Back]  Executive Overview    [Date Toggles]   │
├─────────────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐                  │
│  │ GTV  │  │ TXN  │  │ MARGIN│  ← Hero Metrics │
│  │+5.2% │  │+3.1% │  │-0.4% │  ← PoP badges   │
│  └──────┘  └──────┘  └──────┘                  │
├─────────────────────────────────────────────────┤
│  Sales Trend (Line/Area Chart)                  │
│  ─────────────────────────────────              │
│  [Interactive chart with hover tooltips]        │
└─────────────────────────────────────────────────┘
```

Components used:
- `HeroMetric.vue` (new) - KPI card with PoP
- `SalesTrendChart.vue` (new) - ECharts line/area
- `DateRangeToggle.vue` (new)

#### 2.3 Sales Trend Chart

**File:** `src/components/reports/SalesTrendChart.vue` (new)

- ECharts line/area chart
- X-axis: dates in selected range
- Y-axis: revenue
- Tooltip showing exact values
- Smooth curves, gradient fill under line
- Responsive height

---

### Phase 3: Sales Monitor (Day 3-5)

#### 3.1 Backend APIs

**File:** `zevar_core/api/sales_monitor.py` (extend existing)

Add new endpoint:

```python
@frappe.whitelist()
def get_top_bottom_items(from_date=None, to_date=None, store=None, limit=5):
    """Top N items by revenue + bottom N (dead stock candidates)."""
    # Top items: JOIN Sales Invoice Item + Item, GROUP BY item_code
    # Bottom items: Items with sales in range OR zero sales + current stock > 0
    # Return: { top: [...], bottom: [...], slow_movers: [...] }
```

**File:** `zevar_core/api/reports_dashboard.py` (extend)

```python
@frappe.whitelist()
def get_omnichannel_split(from_date=None, to_date=None):
    """In-Store vs Online sales split."""
    # Check if custom_transaction_stream or other field distinguishes channels
    # Fallback: all POS = in-store
```

#### 3.2 Sales Monitor Page

**File:** `src/pages/reports/SalesMonitor.vue` (new)

Layout:
```
┌─────────────────────────────────────────────────┐
│  [Back]  Sales Monitor        [Date Toggles]    │
├─────────────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │Revenue│  │AOV  │  │ UPT  │  │Units │       │
│  └──────┘  └──────┘  └──────┘  └──────┘       │
├─────────────────────────────────────────────────┤
│  [Hourly Sales Bar Chart]  [Category Donut]     │
├─────────────────────────────────────────────────┤
│  Real-Time Pulse ─── ● Live (auto-refresh 30s)  │
│  ┌─────────────────────────────────────────┐   │
│  │ Latest transactions feed                │   │
│  └─────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  [Top 5 Items Table]  [Dead Stock Table]        │
└─────────────────────────────────────────────────┘
```

#### 3.3 Components

**`HourlySalesChart.vue`** - ECharts bar chart (reuse pattern from `Revenue.vue`)

**`CategoryDonut.vue`** - ECharts donut chart
```javascript
// Option shape
{
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    data: categories.map(c => ({ name: c.dimension, value: c.revenue })),
    itemStyle: { borderRadius: 6 }
  }]
}
```

**`RealTimeFeed.vue`** - Auto-refreshing list
- Uses `useAutoRefresh` composable (30s interval)
- Shows latest transactions with amount, items, timestamp
- Subtle slide-in animation for new entries

**`ProductPerformanceTable.vue`** - Dual table
- Top 5 by revenue (sortable)
- Bottom 5 / Dead Stock (items with stock but zero/minimal sales)
- Columns: Rank, Item Name, Units Sold, Revenue, Stock Level

---

### Phase 4: Profit Intelligence Enhancements (Day 5-6)

#### 4.1 Backend APIs

**File:** `zevar_core/api/profit_intelligence.py` (extend existing)

Add:

```python
@frappe.whitelist()
def get_payment_method_breakdown(from_date=None, to_date=None):
    """Payment method distribution for pie chart."""
    # Query Sales Invoice Payment grouped by mode_of_payment

@frappe.whitelist()
def get_customer_mix(from_date=None, to_date=None):
    """New vs returning customer ratio."""
    # New: first purchase in period
    # Returning: had prior purchases before period
```

#### 4.2 Waterfall Chart Component

**File:** `src/components/profit/WaterfallChart.vue` (new)

- ECharts bar chart with floating bars
- Steps: Revenue → Metal COGS → Gemstone → Labor → Commission → Payment → Overhead → Profit
- Green for revenue/profit, red for deductions
- Connects to existing `get_margin_waterfall` API

#### 4.3 Payment Method Pie

**File:** `src/components/profit/PaymentMethodPie.vue` (new)

- ECharts pie/donut
- Cash, Card, UPI, Gift Card, Financing
- Legend + percentage labels

#### 4.4 Customer Mix Visualization

**File:** `src/components/profit/CustomerMix.vue` (new)

- Simple horizontal bar or two-card comparison
- "New Customers: 42%" vs "Returning: 58%"
- Period-over-period comparison

---

### Phase 5: Workforce Intelligence Enhancements (Day 6-7)

#### 5.1 Backend APIs

**File:** `zevar_core/api/workforce.py` (extend existing)

Add:

```python
@frappe.whitelist()
def get_employee_efficiency(from_date=None, to_date=None, store=None):
    """ATV, capture rate, checkout time per employee."""
    # ATV: revenue / txn_count per employee
    # Capture Rate: loyalty_signups / total_customers_served
    # Checkout Time: avg(seconds) from cart_open to payment_complete

@frappe.whitelist()
def get_staffing_heatmap(from_date=None, to_date=None, store=None):
    """Sales volume vs staffing levels by hour."""
    # Hourly sales from Sales Invoice
    # Staffing from Attendance or Shift Assignment
    # Return: [{hour, sales, staff_count, sales_per_staff}]
```

#### 5.2 Enhanced Workforce Page

**File:** `src/pages/dashboards/WorkforceIntelligence.vue` (modify existing)

Add tabs:
- **Scoreboard** (existing) - Team rankings
- **Efficiency** (new) - ATV, capture rate, checkout time
- **Heatmap** (new) - Sales vs staffing visualization

#### 5.3 Components

**`StaffHeatmap.vue`** - ECharts heatmap
- X-axis: hours (6am-10pm)
- Y-axis: days of week
- Color intensity: sales volume
- Overlay: staff count labels

**`EfficiencyMetrics.vue`** - Table + mini charts
- Per-employee: ATV, capture rate, avg checkout time
- Sparkline trend for each metric

---

### Phase 6: Polish & Edge Cases (Day 7-8)

#### 6.1 Skeleton Loaders

All data-loading sections use consistent skeleton patterns:
```html
<div v-if="loading" class="space-y-2">
  <div v-for="n in 3" :key="n" class="h-10 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
</div>
```

#### 6.2 Empty States

**File:** `src/components/reports/EmptyState.vue` (new)

- Beautiful SVG illustration
- "No data for this period" message
- Suggestion: "Try selecting a different date range"

#### 6.3 Error Handling

All API calls wrapped in try/catch with:
- Toast notification on failure
- "Unable to load data, please refresh" message
- Retry button

#### 6.4 Responsive Design

- Mobile: Single column, horizontal scroll for KPI cards
- Tablet: 2-column grid
- Desktop: 4-column grid for KPIs, side-by-side charts

---

## File Manifest (New + Modified)

### New Files

| File | Purpose |
|---|---|
| `src/stores/reports.js` | Global date range + report state |
| `src/composables/analytics/useDateRange.vue` | Shared date range logic |
| `src/composables/analytics/useAutoRefresh.vue` | Polling/WebSocket composable |
| `src/pages/reports/ExecutiveOverview.vue` | Executive Overview page |
| `src/pages/reports/SalesMonitor.vue` | Sales Monitor page |
| `src/components/reports/HeroMetric.vue` | KPI card with PoP comparison |
| `src/components/reports/DateRangeToggle.vue` | Global time toggles |
| `src/components/reports/SalesTrendChart.vue` | Line/area chart |
| `src/components/reports/CategoryDonut.vue` | Donut chart |
| `src/components/reports/RealTimeFeed.vue` | Auto-refreshing feed |
| `src/components/reports/ProductPerformanceTable.vue` | Top/bottom items |
| `src/components/reports/EmptyState.vue` | Empty state graphic |
| `src/components/profit/WaterfallChart.vue` | Revenue→Profit waterfall |
| `src/components/profit/PaymentMethodPie.vue` | Payment breakdown |
| `src/components/profit/CustomerMix.vue` | New vs returning |
| `src/components/workforce/StaffHeatmap.vue` | Sales vs staffing |
| `src/components/workforce/EfficiencyMetrics.vue` | Employee efficiency |
| `zevar_core/api/reports_dashboard.py` | New backend APIs |

### Modified Files

| File | Changes |
|---|---|
| `src/router.js` | Add `/reports/dashboards/executive` and `/reports/dashboards/sales-monitor` routes |
| `src/components/reports/KPICard.vue` | Add PoP comparison props |
| `src/pages/dashboards/WorkforceIntelligence.vue` | Add tabs (Scoreboard/Efficiency/Heatmap) |
| `zevar_core/api/sales_monitor.py` | Add `get_top_bottom_items` endpoint |
| `zevar_core/api/profit_intelligence.py` | Add `get_payment_method_breakdown` and `get_customer_mix` |
| `zevar_core/api/workforce.py` | Add `get_employee_efficiency` and `get_staffing_heatmap` |

---

## RBAC Matrix (Per PRD §7)

| Tab | Admin | Manager | Employee |
|---|---|---|---|
| Executive Overview | ✅ All stores | ✅ Own store | ❌ |
| Sales Monitor | ✅ All stores | ✅ Own store | ❌ |
| Profit Intelligence | ✅ Full margins | ⚠️ Limited (no cost detail) | ❌ |
| Workforce Intelligence | ✅ Full | ✅ Team only | ❌ |

---

## Performance Strategy (Per PRD §6)

1. **Caching:** `Daily Store Sales Rollup` (already exists) for YTD queries
2. **Skeleton Loaders:** All sections show skeletons while fetching
3. **Lazy Loading:** Route-level code splitting via `() => import(...)`
4. **Debounced Refresh:** Auto-refresh coalesced to prevent spam
5. **Query Optimization:** Date-range indexes on `tabSales Invoice.posting_date`

---

## Testing Checklist

- [ ] All 4 sub-pages load without errors
- [ ] Date range persists when switching between tabs
- [ ] PoP comparisons show correct percentages
- [ ] Charts render with real data
- [ ] Empty states show when no data
- [ ] Skeleton loaders appear during loading
- [ ] Error states show on API failure
- [ ] RBAC: Employee cannot access Profit/Workforce
- [ ] Mobile responsive: single column layout
- [ ] Auto-refresh works on Sales Monitor
- [ ] Dark mode renders correctly
