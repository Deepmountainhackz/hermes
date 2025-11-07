# 📊 Annual Reports Analysis Module - Feature Specification

**Status:** Planned for Phase 2 (Week 3+)  
**Priority:** High Value - Connects macro intelligence to company fundamentals  
**Complexity:** Medium - New pipeline but clear requirements

---

## 🎯 Core Concept

Build a system that:
1. Ingests company annual reports (PDFs)
2. Uses LLM (Claude/ChatGPT) to extract and summarize key information
3. Stores structured data in database
4. Enables queries like: "Which companies in my database would be hurt by rising oil prices?"
5. Connects macro events to company-level impacts

---

## 💡 The Vision

**Problem You're Solving:**
As a macro investor, you see big trends (rising rates, China slowdown, oil spike), but need to know:
- Which specific companies are exposed?
- What's their sensitivity to macro factors?
- How do they describe risks in their own words?

**Current Gap:**
- Hermes tracks macro data (GDP, commodities, forex, economic indicators)
- But no connection to individual company fundamentals
- Manual process to assess company-level impacts

**Solution:**
Annual Reports Database that stores:
- Company profiles
- Revenue breakdowns (geographic, segment)
- Risk factors
- Commodity exposures
- Currency exposures
- Debt levels
- Management outlook

**Then query:** "Show me all companies with >30% China revenue exposure"

---

## 🏗️ System Architecture

### **New Components:**

```
hermes/
├── services/
│   └── fundamentals/              ← NEW MODULE
│       ├── process_annual_report.py   # PDF → LLM → Database
│       ├── extract_key_metrics.py     # Structure extraction
│       └── query_company_data.py      # Search & analysis
│
├── database (new tables):
│   ├── companies                  # Company master data
│   ├── annual_reports             # Reports metadata
│   ├── revenue_breakdown          # Geographic/segment revenue
│   ├── risk_factors               # Extracted risks
│   ├── commodity_exposure         # Oil, metals, etc.
│   ├── currency_exposure          # FX sensitivity
│   └── financial_metrics          # Key ratios
│
├── dashboard:
│   └── "Companies" tab            # NEW - Company analysis view
│
└── uploads/
    └── annual_reports/            # PDF storage
```

---

## 📋 Database Schema Design

### **companies**
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(15, 2),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **annual_reports**
```sql
CREATE TABLE annual_reports (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    fiscal_year INTEGER NOT NULL,
    report_date DATE,
    file_path VARCHAR(500),
    processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    llm_summary TEXT,
    UNIQUE(company_id, fiscal_year)
);
```

### **revenue_breakdown**
```sql
CREATE TABLE revenue_breakdown (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES annual_reports(id),
    breakdown_type VARCHAR(50),  -- 'geographic' or 'segment'
    category VARCHAR(100),        -- e.g., 'China', 'North America', 'Cloud Services'
    revenue DECIMAL(15, 2),
    percentage DECIMAL(5, 2),
    year_over_year_change DECIMAL(5, 2)
);
```

### **risk_factors**
```sql
CREATE TABLE risk_factors (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES annual_reports(id),
    risk_category VARCHAR(100),   -- e.g., 'Currency', 'Commodity', 'Geopolitical'
    risk_description TEXT,
    severity VARCHAR(20),         -- 'High', 'Medium', 'Low'
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **commodity_exposure**
```sql
CREATE TABLE commodity_exposure (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES annual_reports(id),
    commodity VARCHAR(50),        -- 'Oil', 'Natural Gas', 'Copper', 'Wheat', etc.
    exposure_type VARCHAR(50),    -- 'Input Cost', 'Revenue Driver', 'Hedged'
    annual_cost DECIMAL(15, 2),
    percentage_of_cogs DECIMAL(5, 2),
    notes TEXT
);
```

### **currency_exposure**
```sql
CREATE TABLE currency_exposure (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES annual_reports(id),
    currency VARCHAR(10),         -- 'EUR', 'GBP', 'JPY', 'CNY', etc.
    exposure_amount DECIMAL(15, 2),
    hedged_percentage DECIMAL(5, 2),
    sensitivity_analysis TEXT     -- "10% move in EUR = $X impact"
);
```

### **financial_metrics**
```sql
CREATE TABLE financial_metrics (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES annual_reports(id),
    metric_name VARCHAR(100),
    metric_value DECIMAL(15, 2),
    year_over_year_change DECIMAL(5, 2),
    notes TEXT
);
```

---

## 🔄 Workflow

### **Phase 1: Manual Processing**

**Step 1: Upload Annual Report**
```bash
python services/fundamentals/process_annual_report.py \
    --file uploads/annual_reports/AAPL_2024_10K.pdf \
    --ticker AAPL \
    --year 2024
```

**Step 2: LLM Extraction**
```python
def process_report(pdf_path, ticker, year):
    # 1. Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # 2. Send to Claude/ChatGPT with structured prompt
    analysis = llm.analyze(f"""
    Analyze this annual report and extract:
    
    1. REVENUE BREAKDOWN:
       - Geographic (Americas, Europe, China, Asia Pacific, etc.)
       - Segments (Products, Services, etc.)
       - YoY changes
    
    2. RISK FACTORS:
       - Currency risks
       - Commodity price risks
       - Geopolitical risks
       - Supply chain risks
    
    3. COMMODITY EXPOSURE:
       - Which commodities affect COGS?
       - Estimated annual impact
    
    4. CURRENCY EXPOSURE:
       - Revenue by currency
       - Hedging programs
       - Sensitivity to FX moves
    
    5. KEY METRICS:
       - Debt/Equity
       - Operating margin
       - Free cash flow
       - Return on invested capital
    
    Return as structured JSON.
    
    TEXT:
    {text}
    """)
    
    # 3. Parse JSON response
    # 4. Insert into database tables
    save_to_database(analysis)
```

**Step 3: Query & Analyze**
```python
# Find companies exposed to oil prices
exposed_companies = query("""
    SELECT c.ticker, c.name, ce.annual_cost, ce.percentage_of_cogs
    FROM companies c
    JOIN annual_reports ar ON c.id = ar.company_id
    JOIN commodity_exposure ce ON ar.id = ce.report_id
    WHERE ce.commodity = 'Oil'
    AND ce.percentage_of_cogs > 10
    ORDER BY ce.percentage_of_cogs DESC
""")

# Find companies with China exposure
china_exposed = query("""
    SELECT c.ticker, c.name, rb.revenue, rb.percentage
    FROM companies c
    JOIN annual_reports ar ON c.id = ar.company_id
    JOIN revenue_breakdown rb ON ar.id = rb.report_id
    WHERE rb.category = 'China'
    AND rb.percentage > 20
    ORDER BY rb.percentage DESC
""")
```

---

## 💰 Investment Use Cases

### **Use Case 1: Oil Price Spike**
**Hermes detects:** Oil jumps from $75 → $85

**Query:**
```sql
-- Which companies hurt by higher oil?
SELECT c.ticker, c.name, ce.percentage_of_cogs, ce.annual_cost
FROM companies c
JOIN commodity_exposure ce ON c.id = ce.company_id
WHERE ce.commodity IN ('Oil', 'Natural Gas')
ORDER BY ce.percentage_of_cogs DESC;
```

**Result:** Airlines, logistics companies most exposed → Potential shorts

---

### **Use Case 2: China Slowdown**
**Hermes detects:** China GDP growth slowing (5.2% → 4.5%)

**Query:**
```sql
-- Which companies have significant China revenue?
SELECT c.ticker, c.name, rb.percentage, rb.revenue
FROM companies c
JOIN revenue_breakdown rb ON c.id = rb.company_id
WHERE rb.category = 'China'
AND rb.percentage > 15
ORDER BY rb.percentage DESC;
```

**Result:** Apple, Nike, luxury brands exposed → Reduce positions

---

### **Use Case 3: USD Strengthening**
**Hermes detects:** USD up 5% vs basket of currencies

**Query:**
```sql
-- Which companies have unhedged foreign revenue?
SELECT c.ticker, c.name, ce.currency, ce.exposure_amount, ce.hedged_percentage
FROM companies c
JOIN currency_exposure ce ON c.id = ce.company_id
WHERE ce.hedged_percentage < 50
AND ce.exposure_amount > 1000000000  -- $1B+
ORDER BY ce.exposure_amount DESC;
```

**Result:** Large multinationals with unhedged FX → Potential headwind

---

### **Use Case 4: Recession Signals**
**Hermes detects:** Unemployment rising, GDP slowing

**Query:**
```sql
-- Which companies have high debt levels?
SELECT c.ticker, c.name, fm.metric_value as debt_to_equity
FROM companies c
JOIN financial_metrics fm ON c.id = fm.company_id
WHERE fm.metric_name = 'Debt/Equity'
AND fm.metric_value > 2.0
ORDER BY fm.metric_value DESC;
```

**Result:** Highly leveraged companies → Higher risk in downturn

---

## 🎯 LLM Prompt Template

```
SYSTEM PROMPT:
You are a financial analyst extracting structured data from annual reports.
Extract information accurately and return it in JSON format.
If information is not available, return null for that field.

USER PROMPT:
Analyze this annual report for {COMPANY_NAME} ({TICKER}) - Fiscal Year {YEAR}

Extract the following information:

1. REVENUE BREAKDOWN:
{
  "geographic": [
    {"region": "Americas", "revenue": 123456789, "percentage": 45.2, "yoy_change": 8.5},
    {"region": "Europe", "revenue": 67890123, "percentage": 24.8, "yoy_change": -2.3}
  ],
  "segments": [
    {"segment": "Products", "revenue": 189012345, "percentage": 69.1, "yoy_change": 5.2}
  ]
}

2. RISK FACTORS:
{
  "risks": [
    {
      "category": "Currency",
      "description": "Significant exposure to EUR/USD movements...",
      "severity": "High"
    }
  ]
}

3. COMMODITY EXPOSURE:
{
  "commodities": [
    {
      "commodity": "Oil",
      "exposure_type": "Input Cost",
      "annual_cost": 5000000000,
      "percentage_of_cogs": 15.5,
      "notes": "Primary fuel cost for transportation fleet"
    }
  ]
}

4. CURRENCY EXPOSURE:
{
  "currencies": [
    {
      "currency": "EUR",
      "exposure_amount": 25000000000,
      "hedged_percentage": 60,
      "sensitivity": "10% EUR move = $2.5B impact on revenue"
    }
  ]
}

5. KEY FINANCIAL METRICS:
{
  "metrics": [
    {"metric": "Debt/Equity", "value": 1.45, "yoy_change": 0.15},
    {"metric": "Operating Margin", "value": 28.5, "yoy_change": -1.2},
    {"metric": "Free Cash Flow", "value": 12000000000, "yoy_change": 8.5}
  ]
}

ANNUAL REPORT TEXT:
{FULL_TEXT}

Return ONLY valid JSON. No additional commentary.
```

---

## 🔧 Implementation Phases

### **Phase 1: Core Infrastructure (Week 1)**
1. Create database tables
2. Build PDF text extraction
3. Set up LLM integration (Claude API)
4. Test with 2-3 sample reports

### **Phase 2: Processing Pipeline (Week 2)**
1. Build structured extraction prompt
2. Create data parsing logic
3. Implement database insertion
4. Error handling & validation

### **Phase 3: Query Interface (Week 3)**
1. Build query functions for common use cases
2. Add to dashboard
3. Create visualization of exposures

### **Phase 4: Automation (Week 4)**
1. Batch processing for multiple reports
2. Scheduled updates (quarterly)
3. Alert system for new filings

---

## 💡 Brilliant Integrations with Existing Hermes

### **Integration 1: Commodity Price Alerts**
```python
# When oil price moves >5%
if oil_price_change > 5:
    affected_companies = get_oil_exposed_companies()
    send_alert(f"Oil up {oil_price_change}% - {len(affected_companies)} portfolio companies affected")
```

### **Integration 2: Geographic Economic Analysis**
```python
# When China GDP slows
if china_gdp_growth < 4.5:
    china_exposed = get_companies_by_region('China', min_percentage=15)
    analyze_impact(china_exposed, 'gdp_slowdown')
```

### **Integration 3: Currency Dashboard**
```python
# Daily FX impact analysis
usd_strength = calculate_usd_index_change()
if abs(usd_strength) > 2:
    currency_exposed = get_unhedged_fx_exposure()
    estimate_earnings_impact(currency_exposed, usd_strength)
```

### **Integration 4: Macro Regime → Company Impact**
```python
# Based on economic regime (from Dalio framework)
regime = analyze_economic_regime()

if regime == "STAGFLATION":
    # Find companies with pricing power
    pricing_power_companies = query("""
        SELECT c.ticker, fm.metric_value as operating_margin
        FROM companies c
        JOIN financial_metrics fm ON c.id = fm.company_id
        WHERE fm.metric_name = 'Operating Margin'
        AND fm.metric_value > 20
        ORDER BY fm.metric_value DESC
    """)
```

---

## 📊 Dashboard Visualization Ideas

### **Company Exposure Heatmap**
```
           Oil  Gas  Copper  Wheat  EUR  GBP  CNY  China
AAPL       Low  Low   Med    Low    Med  Low  High  High
XOM        High High  Low    Low    Med  Med  Low   Med
BA         Med  Med   Med    Low    High High Med   Low
```

### **Macro Event Impact Simulator**
```
Event: Oil +$10/barrel
Estimated Impact:
- XOM: +$2.5B earnings ✅
- DAL: -$800M earnings ❌
- FDX: -$450M earnings ❌
```

### **Geographic Revenue Exposure**
```
3D Globe showing:
- Company revenue concentration by region
- Color-coded by economic health
- Click to see detailed breakdown
```

---

## 🚧 Technical Considerations

### **LLM Choice:**
- **Claude API** (recommended): Better at long documents, structured output
- **ChatGPT API**: Alternative, similar capabilities
- **Cost**: ~$0.50-2.00 per report (depending on length)

### **PDF Processing:**
- **PyMuPDF** or **pdfplumber**: Extract text
- Handle tables (revenue breakdowns)
- Handle images (skip)
- Handle multi-column layouts

### **Storage:**
- PDFs: Local filesystem or S3
- Database: PostgreSQL (already using)
- Estimated: 2-5MB per report × 50 companies = 100-250MB

### **Update Frequency:**
- Annual reports: Once per year per company
- 10-Q filings: Quarterly updates
- Not time-sensitive (can process manually)

---

## 💰 Value Proposition

### **What This Adds to Hermes:**

**Before:** 
- Track macro trends (GDP, commodities, forex)
- No connection to specific companies

**After:**
- See which companies affected by each macro move
- Quantify impact (revenue %, COGS impact)
- Make informed position adjustments

**Example Scenario:**
1. Hermes alerts: "Oil up 15% in past week"
2. Query annual reports DB: "Show oil-exposed companies"
3. Result: Airlines down 12% average, consider shorts
4. Also find: Energy companies with <$50 breakeven (longs)

**This turns macro intelligence into actionable trades.**

---

## 🎯 Initial Company List (Suggested)

**Start with 10-15 companies you trade:**

**Tech:**
- AAPL (China exposure, supply chain)
- MSFT (geographic diversity)
- GOOGL (currency exposure)

**Finance:**
- JPM (interest rate sensitivity)
- GS (market exposure)

**Energy:**
- XOM (commodity producer)
- CVX (commodity producer)

**Consumer:**
- WMT (consumer spending)
- NKE (China exposure, supply chain)

**Industrial:**
- BA (supply chain, geopolitical)
- CAT (China, commodities)

**This gives cross-sector coverage and diverse macro exposures.**

---

## 📅 Recommended Timeline

**Week 3-4 (After Hermes Stabilizes):**
- Design final database schema
- Set up Claude API
- Test with 2-3 reports manually

**Week 5-6:**
- Build processing pipeline
- Process 10-15 company reports
- Create basic query functions

**Week 7-8:**
- Add dashboard visualization
- Build integration with macro data
- Create alert system

**Month 3+:**
- Automate quarterly updates
- Add more companies
- Refine LLM prompts

---

## 🏆 Success Metrics

**Phase 1 Success:**
- 10 company reports processed
- All key data extracted accurately
- Query functions working

**Phase 2 Success:**
- Connected to live Hermes macro data
- Alerts triggering on macro events
- Dashboard showing company impacts

**Phase 3 Success:**
- Using system for actual investment decisions
- Identified profitable trades based on macro-company connections
- Saved time vs manual analysis

---

## 💡 Future Enhancements

**Beyond Annual Reports:**
- Earnings call transcripts
- 10-Q quarterly filings
- Industry research reports
- Competitor analysis
- Supply chain mapping

**Advanced Analytics:**
- Peer comparison
- Historical trend analysis
- Sentiment analysis
- Management tone analysis
- Predictive modeling

---

## 📝 Notes for Implementation

**When you're ready to build this:**

1. Start with database schema (easiest first)
2. Manually process 2 reports to refine prompts
3. Build automation only after manual process works
4. Add to dashboard incrementally

**Key Success Factor:**
- Get the LLM prompt right (most important)
- Spend time on prompt engineering
- Test with multiple reports
- Iterate based on accuracy

**Estimated Build Time:**
- Phase 1: 1-2 weeks (part-time)
- Phase 2: 1-2 weeks
- Phase 3: 1 week

**Total: 3-5 weeks** to fully integrated system

---

## 🎯 The Big Picture

This feature transforms Hermes from:

**"I track macro events"**

To:

**"I track macro events AND know exactly which companies to trade based on those events"**

That's the difference between data and actionable intelligence.

---

**Documentation Date:** November 6, 2025  
**Author:** Big Cheese  
**Status:** Planned - Build after Hermes stabilization (Week 3+)  
**Priority:** High - Core value proposition for hedge fund use case
