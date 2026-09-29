# M&A Model — Adani Group Acquisition of Ambuja Cements & ACC Ltd

## Deal Overview

**Transaction**: Adani Group's acquisition of Holcim's 63.15% stake in Ambuja Cements Ltd (and indirect control of ACC Ltd through Ambuja's 50.05% stake in ACC)

| Parameter | Detail |
|---|---|
| **Acquirer** | Adani Group (via Endeavour Trade and Investment Ltd) |
| **Target** | Ambuja Cements Ltd & ACC Ltd |
| **Seller** | Holcim Group (LafargeHolcim) |
| **Announcement Date** | 15 May 2022 |
| **Completion Date** | 16 September 2022 |
| **Total Deal Value** | ₹81,361 Crores (~US$10.5 Billion) |
| **Deal Type** | Controlling stake acquisition + mandatory open offers |
| **Sector** | Building Materials — Cement |

## Project Structure

```
M&A Model/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── run_model.py                    # Main entry point — generates Excel model
│
├── model/
│   ├── __init__.py
│   ├── assumptions.py              # Transaction assumptions & source financials
│   ├── merger_model.py             # Core M&A calculations (PPA, Goodwill,
│   │                                 Accretion/Dilution, Synergies)
│   └── excel_generator.py          # Professional Excel workbook output
│
├── deal_rationale/
│   └── deal_memo.md                # Two-page deal rationale memo
│
├── output/                         # Generated Excel model output
│   └── (auto-generated)
│
└── dashboard/
    ├── index.html                  # Interactive M&A dashboard
    ├── style.css                   # Dashboard styling
    └── app.js                      # Dashboard logic & charts
```

## Model Components

### 1. Transaction Summary & Sources/Uses
- Purchase price breakdown by component (Holcim stake purchase, Ambuja open offer, ACC open offer)
- Sources of financing (equity, term loans, bridge facilities)
- Uses of funds (share purchases, transaction costs, refinancing)

### 2. Purchase Price Allocation (PPA)
- Fair value assessment of identifiable tangible assets
- Identification and valuation of intangible assets (brand, customer relationships, mineral rights)
- Goodwill calculation (excess of purchase price over fair value of net identifiable assets)
- Deferred tax impact of fair value step-ups

### 3. Pro Forma Combined Financials
- Combined income statement (Adani Cement + Ambuja + ACC)
- Pro forma balance sheet with PPA and financing adjustments
- Pro forma credit metrics

### 4. Synergy Analysis
- Revenue synergies: cross-selling, geographic expansion, pricing optimization
- Cost synergies: procurement, logistics, SG&A rationalization, plant optimization
- Synergy phasing schedule (Year 1 through Year 3 full run-rate)
- NPV of synergies at WACC

### 5. Accretion / Dilution Analysis
- Standalone vs. pro forma EPS comparison
- Accretion/dilution with and without synergies
- Breakeven synergy required for EPS accretion
- Sensitivity to purchase price premium and cost of debt

### 6. Precedent Transaction Analysis
- Comparable cement M&A transactions in India and globally
- Premium paid benchmarking
- Valuation multiple comparison (EV/EBITDA, EV/Tonne)

## Data Sources

- **Ambuja Cements Ltd** — Annual Report FY2021-22, BSE/NSE filings
- **ACC Limited** — Annual Report FY2021-22, BSE/NSE filings
- **Holcim Group** — Press releases, investor presentations
- **SEBI Open Offer Documents** — Detailed letter of offer filings
- **Precedent Transactions** — Bloomberg, Mergermarket, public filings

## How to Run

### Generate the Excel Model
```bash
pip install -r requirements.txt
python run_model.py
```
This generates a formatted Excel workbook at `output/Adani_Ambuja_MA_Model.xlsx`.

### Launch the Interactive Dashboard
Open `dashboard/index.html` in any modern browser — no server required.

## Key Findings

| Metric | Value |
|---|---|
| Implied EV/EBITDA (Ambuja) | 14.3x |
| Implied EV/EBITDA (ACC) | 12.8x |
| Premium to Undisturbed Price (Ambuja) | 13.2% |
| Premium to Undisturbed Price (ACC) | 9.5% |
| Total Identified Synergies (Run-rate) | ₹3,100 Cr/year |
| Goodwill Created | ₹28,426 Cr |
| Pro Forma EPS Accretion (Year 2, with synergies) | +8.4% |
| Breakeven Synergy for Accretion | ₹1,240 Cr/year |

## Author

**Yug Desai** — Mechanical Engineering, IIT Gandhinagar (Class of 2027). Interested in Investment Banking and Financial Analytics.

[LinkedIn](https://www.linkedin.com/in/yug-desai-9a227428b/) · [Email](mailto:yug.desai@iitgn.ac.in)
---
*Disclaimer: This model is built using publicly available data for educational and analytical purposes. Financial projections and assumptions are illustrative and do not constitute investment advice.*
