"""
Model Inputs — Adani Group acquisition of Ambuja Cements & ACC from Holcim
==========================================================================
Every hard-coded number in the project lives in this file. Each one is tagged:

  [FILED]       reported figure; the source key points into SOURCES below
  [DERIVED]     arithmetic on filed figures (formula shown in the comment)
  [ASSUMPTION]  analyst judgement as at deal close (Sep-2022); change freely

All money is INR crore (1 crore = 10 million) unless a key says otherwise.
Ambuja and ACC reported on a January–December year until 2022, so the last
full pre-deal year is CY2021 (year ended 31-Dec-2021). Historical figures are
STANDALONE (Ambuja standalone excludes ACC except for dividends received).

The model never imports these dicts directly. It calls default_inputs(), which
returns a deep copy, so sensitivities and tests can change inputs without side
effects.
"""

import copy

SOURCES = {
    "holcim_release": "Holcim media release, May-2022 — https://www.holcim.com/media/media-releases/holcim-india-business-acquired",
    "adani_release": "Adani media release, 16-Sep-2022 — https://www.adani.com/newsroom/media-releases/adani-becomes-indias-second-largest-cement-player",
    "bs_open_offer": "Business Standard, 10-Sep-2022 — https://www.business-standard.com/article/companies/ambuja-cements-acc-receive-lukewarm-response-from-public-shareholders-122091000362_1.html",
    "bs_refi": "Business Standard, 1-Dec-2022 — https://www.business-standard.com/article/companies/adani-group-to-refinance-ambuja-cement-acc-debt-worth-3-5-billion-122120100944_1.html",
    "screener_ambuja": "Ambuja standalone financials (company filings via Screener) — https://www.screener.in/company/AMBUJACEM/",
    "screener_acc": "ACC standalone financials (company filings via Screener) — https://www.screener.in/company/ACC/",
    "nse_prices": "NSE daily closes (Yahoo Finance history: AMBUJACEM.NS, ACC.NS, USDINR=X)",
    "bs_jaypee_2013": "Business Standard, 12-Sep-2013 — https://www.business-standard.com/article/companies/birla-buys-jaypee-s-gujarat-cement-unit-for-rs-3-800-cr-113091200054_1.html",
    "bs_jaypee_2016": "Business Standard, 5-Jul-2016 — https://www.business-standard.com/article/markets/jp-deal-big-leap-for-ultratech-116070501043_1.html",
    "bs_lafarge_2016": "Business Standard, 11-Jul-2016 — https://www.business-standard.com/article/companies/nirma-cements-1-4-bn-lafarge-india-buyout-116071100403_1.html",
    "li_century_2018": "Legally India, 22-May-2018 (EV) — https://www.legallyindia.com/corporatemna/trilegal-khaitan-vaish-on-ultratech-cem-s-buy-of-century-textile-s-cement-biz-20180522-9362 ; capacity per CARE Ratings report on UltraTech",
    "bs_binani_2018": "Business Standard, 25-Dec-2019 (Kotak estimate of EV) — https://www.business-standard.com/amp/article/companies/ultratech-cement-street-watchful-on-valuations-of-new-acquisition-119122500555_1.html",
    "nuvoco_emami_2020": "Nuvoco press release, Feb-2020 — https://admin.nuvoco.com/public/MediaRalationsDetails/Nirma%20Group%20announces%20the%20acquisition%20of%20Emami%20Cement%20-%20Feb%202020.pdf",
}

_INPUTS = {
    # ------------------------------------------------------------------
    # TRANSACTION FACTS
    # ------------------------------------------------------------------
    "transaction": {
        "deal_name": "Adani Group acquisition of Ambuja Cements & ACC from Holcim",
        "acquirer": "Endeavour Trade and Investment Ltd (Adani family SPV, Mauritius)",
        "seller": "Holcim Group",
        "announcement_date": "15-May-2022",
        "completion_date": "16-Sep-2022",
        "undisturbed_price_date": "13-May-2022",  # last close before announcement
        "balance_sheet_date": "31-Dec-2021",      # latest audited balance sheet before close
        "combined_capacity_mtpa": 67.5,           # [FILED] adani_release
        "consideration_usd_bn_reported": 6.50,    # [FILED] adani_release ("Holcim stake and open offer consideration")
        "acq_debt_usd_bn": 4.50,                  # [FILED] adani_release ("facilities aggregating to USD 4.50 billion ... 14 international banks")
        "post_deal_ambuja_pct_reported": 63.15,   # [FILED] adani_release
        "post_deal_acc_pct_reported": 56.69,      # [FILED] adani_release (incl. 50.05% held via Ambuja)
    },

    "fx": {
        "inr_per_usd_at_close": 79.85,            # [FILED] nse_prices, USDINR close 16-Sep-2022
    },

    "ambuja_shares": {
        "total_shares_cr": 198.56,                # [DERIVED] share capital ₹397.13 Cr / ₹2 face value (screener_ambuja)
        "holcim_stake_pct": 63.11,                # [FILED] holcim_release
        "open_offer_shares_tendered_cr": 0.0727,  # [FILED] bs_open_offer (~7.27 lakh shares tendered)
        "offer_price": 385.0,                     # [FILED] holcim_release
        "undisturbed_close": 359.10,              # [FILED] nse_prices, close 13-May-2022 (last day before announcement)
        "close_at_completion": 516.70,            # [FILED] nse_prices, close 16-Sep-2022
        "stake_in_acc_pct": 50.05,                # [FILED] holcim_release
    },

    "acc_shares": {
        "total_shares_cr": 18.78,                 # [FILED] ACC shares outstanding (26% open offer = 4.89 Cr shares)
        "holcim_direct_stake_pct": 4.48,          # [FILED] holcim_release
        "open_offer_shares_tendered_cr": 0.4061,  # [FILED] bs_open_offer (~40.61 lakh shares tendered)
        "offer_price": 2300.0,                    # [FILED] holcim_release
        "undisturbed_close": 2113.30,             # [FILED] nse_prices, close 13-May-2022
        "close_at_completion": 2611.50,           # [FILED] nse_prices, close 16-Sep-2022
    },

    "deal_costs": {
        "transaction_costs_pct_of_consideration": 1.0,   # [ASSUMPTION] advisory, legal, stamp duty; expensed at close
    },

    # ------------------------------------------------------------------
    # ACQUISITION FINANCING (held at the offshore holdco, not at Ambuja/ACC)
    # Uses cannot be funded with Ambuja/ACC cash: Companies Act s.67 bars a
    # company financing the purchase of its own shares, and ~37% of Ambuja
    # belongs to minorities. Sponsor equity is the balancing source.
    # ------------------------------------------------------------------
    "acq_debt": {
        "bridge_usd_bn": 3.50,                    # [FILED] bs_refi ("refinance $3.5 billion of bridge loans")
        # term tranche = total facilities (4.50) - bridge (3.50)          [DERIVED]
        "term_rate_pct": 7.50,                    # [ASSUMPTION] USD SOFR (~4.5-5%) + ~275bp, all-in
        "bridge_rate_pct": 8.00,                  # [ASSUMPTION] bridge margin above term
        "refi_rate_pct": 7.50,                    # [ASSUMPTION] bridge refinanced into 5-yr term debt from Year 2 (bs_refi)
        "interest_tax_deductible": False,         # [ASSUMPTION] debt sits in a Mauritius SPV with no taxable income;
                                                  #   India has no tax consolidation, so no shield. Flip to test.
    },

    "holdco": {
        "wht_on_ambuja_dividends_pct": 5.0,       # [ASSUMPTION] India–Mauritius DTAA rate for a >=10% holding
        "wht_on_acc_dividends_pct": 15.0,         # [ASSUMPTION] DTAA rate for a <10% direct holding (6.6%)
    },

    # ------------------------------------------------------------------
    # HISTORICAL STANDALONE FINANCIALS, CY2019–CY2021 (screener_ambuja / screener_acc)
    # 'other_income_normal' is before exceptional items; exceptionals are
    # excluded from the projection base (shown for reconciliation).
    # ------------------------------------------------------------------
    "ambuja_hist": {
        "years": ["CY2019", "CY2020", "CY2021"],
        "revenue":              [11668.0, 11372.0, 13979.0],   # [FILED]
        "operating_expenses":   [9519.0, 8725.0, 10764.0],     # [FILED]
        "ebitda":               [2149.0, 2647.0, 3215.0],      # [FILED] = revenue - operating_expenses
        "other_income_normal":  [424.0, 371.0, 281.0],         # [FILED]
        "exceptional_items":    [3.0, 1.0, -66.0],             # [FILED]
        "interest_expense":     [84.0, 83.0, 91.0],            # [FILED]
        "depreciation":         [544.0, 521.0, 552.0],         # [FILED]
        "pbt":                  [1948.0, 2414.0, 2788.0],      # [FILED]
        "net_income":           [1529.0, 1790.0, 2083.0],      # [FILED]
        "eps":                  [7.70, 9.02, 10.49],           # [FILED]
        "dividend_payout_pct":  [19.0, 200.0, 60.0],           # [FILED]
    },
    "acc_hist": {
        "years": ["CY2019", "CY2020", "CY2021"],
        "revenue":              [15657.0, 13785.0, 16151.0],
        "operating_expenses":   [13247.0, 11432.0, 13151.0],
        "ebitda":               [2409.0, 2352.0, 3000.0],
        "other_income_normal":  [287.0, 204.0, 203.0],
        "exceptional_items":    [24.0, -176.0, -91.0],
        "interest_expense":     [86.0, 57.0, 55.0],
        "depreciation":         [603.0, 635.0, 597.0],
        "pbt":                  [2031.0, 1688.0, 2460.0],
        "net_income":           [1359.0, 1415.0, 1820.0],
        "eps":                  [72.36, 75.35, 96.93],
        "dividend_payout_pct":  [19.0, 19.0, 60.0],
    },

    # Balance sheets at 31-Dec-2021 (latest audited before close; used as the
    # closing balance sheet proxy). [FILED] screener_ambuja / screener_acc
    "ambuja_bs": {
        "share_capital": 397.0,
        "reserves": 21808.0,
        "borrowings": 351.0,                 # incl. lease liabilities 304
        "other_liabilities": 5627.0,
        "fixed_assets": 7671.0,              # incl. intangibles 255
        "cwip": 951.0,
        "investments": 11774.0,              # almost entirely subsidiaries, chiefly the 50.05% ACC stake
        "inventories": 1464.0,
        "trade_receivables": 295.0,
        "cash": 4169.0,
        "other_assets": 1859.0,              # loans & advances 248 + other 1,611
        "total_assets": 28183.0,
    },
    "acc_bs": {
        "share_capital": 188.0,
        "reserves": 14040.0,
        "borrowings": 126.0,                 # lease liabilities
        "other_liabilities": 6565.0,
        "fixed_assets": 6723.0,
        "cwip": 1212.0,
        "investments": 193.0,
        "inventories": 1273.0,
        "trade_receivables": 462.0,
        "cash": 7403.0,
        "other_assets": 3653.0,              # loans & advances 376 + other 3,277
        "total_assets": 20919.0,
    },

    # ACC dividend received by Ambuja in CY2021: ACC paid ₹14/share for CY2020
    # (payout 19% × NI 1,415 / 18.78 Cr shares ≈ ₹14). It sits inside Ambuja's
    # other income and is intra-group, so it is removed when deriving the
    # treasury yield and is never counted twice in consolidated earnings.
    "intercompany": {
        "acc_dps_paid_in_cy2021": 14.0,      # [DERIVED] see comment above (screener_acc payout history)
    },

    # ------------------------------------------------------------------
    # PROJECTIONS (12-month years ending March; Year 1 = FY2023E)
    # Base = CY2021 actual. Margins reflect the 2022 fuel-cost spike known at close.
    # ------------------------------------------------------------------
    "projection": {
        "years": ["FY2023E", "FY2024E", "FY2025E"],
        "ambuja_revenue_growth_pct": [12.0, 9.0, 8.0],   # [ASSUMPTION] Y1 growth is vs CY2021
        "acc_revenue_growth_pct":    [12.0, 9.0, 8.0],   # [ASSUMPTION]
        "ambuja_ebitda_margin_pct":  [18.0, 20.0, 21.0], # [ASSUMPTION] CY2021 actual 23.0%
        "acc_ebitda_margin_pct":     [12.0, 14.0, 15.0], # [ASSUMPTION] CY2021 actual 18.6%
        # D&A % of revenue, interest expense and cash are held at CY2021 levels  [ASSUMPTION]
        "tax_rate_pct": 25.17,                           # [FILED] s.115BAA rate; CY2021 effective ~25-26%
        "dividend_payout_pct": 20.0,                     # [ASSUMPTION] in line with 2019-20 history (19%)
    },

    # ------------------------------------------------------------------
    # COST OF CAPITAL
    # ------------------------------------------------------------------
    "cost_of_capital": {
        "risk_free_pct": 7.25,             # [ASSUMPTION] India 10Y G-Sec, Sep-2022 (~7.2-7.3%)
        "equity_risk_premium_pct": 6.5,    # [ASSUMPTION]
        "asset_beta": 0.85,                # [ASSUMPTION] Indian cement; Ambuja/ACC are net-cash, so equity beta ≈ asset beta
        "synergy_terminal_growth_pct": 4.0,  # [ASSUMPTION] RBI CPI target; synergies grow with inflation
    },

    # ------------------------------------------------------------------
    # SYNERGIES  [ASSUMPTION] — model estimates, not company guidance
    # ------------------------------------------------------------------
    "synergies": {
        "items": {
            "procurement": {"label": "Procurement (fly ash, gypsum, slag, coal)", "type": "cost", "run_rate": 850.0, "phasing_pct": [30, 70, 100]},
            "logistics":   {"label": "Logistics & freight (route rationalisation, ports)", "type": "cost", "run_rate": 620.0, "phasing_pct": [20, 60, 100]},
            "sga":         {"label": "SG&A and shared services", "type": "cost", "run_rate": 480.0, "phasing_pct": [40, 80, 100]},
            "energy":      {"label": "Energy (fuel mix, WHRS, renewables)", "type": "cost", "run_rate": 380.0, "phasing_pct": [15, 50, 100]},
            "plant":       {"label": "Plant optimisation (clinker factor)", "type": "cost", "run_rate": 270.0, "phasing_pct": [10, 45, 100]},
            "geography":   {"label": "Revenue: cross-selling into new regions (EBITDA impact)", "type": "revenue", "run_rate": 310.0, "phasing_pct": [10, 40, 100]},
            "pricing":     {"label": "Revenue: pricing discipline (EBITDA impact)", "type": "revenue", "run_rate": 190.0, "phasing_pct": [25, 65, 100]},
        },
        "costs_to_achieve": 2800.0,                 # one-off, pre-tax
        "costs_to_achieve_phasing_pct": [60, 40, 0],
    },

    # ------------------------------------------------------------------
    # PURCHASE PRICE ALLOCATION  [ASSUMPTION] — no public PPA exists for the
    # holdco; step-ups are illustrative estimates sized against book values.
    # ------------------------------------------------------------------
    "ppa": {
        "step_ups": {
            "ambuja": {"ppe": 3200.0, "mineral_rights": 4500.0, "brand": 2800.0,
                       "customer_relationships": 1200.0, "favourable_contracts": 650.0, "inventory": 180.0},
            "acc":    {"ppe": 2800.0, "mineral_rights": 3800.0, "brand": 2200.0,
                       "customer_relationships": 950.0, "favourable_contracts": 420.0, "inventory": 220.0},
        },
        "ppe_life_years": 15,
        "finite_intangible_life_years": 15,   # mineral rights, customer relationships, contracts
        # brand: indefinite life, not amortised (impairment-tested)
        # inventory step-up: released through cost of sales in Year 1
        "nci_method": "proportionate",        # Ind AS 103 option: NCI at share of identifiable net assets
    },

    # ------------------------------------------------------------------
    # PRECEDENT TRANSACTIONS — Indian cement, announced before this deal.
    # Most were asset or unlisted-company deals, so a control premium is not
    # meaningful; EV/tonne is the industry benchmark. EV/EBITDA was not
    # reliably disclosed and is therefore not shown.
    # ------------------------------------------------------------------
    "precedents": [
        {"date": "Sep-2013", "acquirer": "UltraTech Cement", "target": "Jaypee Gujarat unit", "capacity_mtpa": 4.8,
         "ev_cr": 3800.0, "inr_per_usd": 63.16, "note": "", "source": "bs_jaypee_2013"},
        {"date": "Mar-2016", "acquirer": "UltraTech Cement", "target": "Jaiprakash Associates (6 plants)", "capacity_mtpa": 21.2,
         "ev_cr": 16189.0, "inr_per_usd": 66.37, "note": "Seller deleveraging; EV as revised from ₹15,900 Cr", "source": "bs_jaypee_2016"},
        {"date": "Jul-2016", "acquirer": "Nirma", "target": "Lafarge India", "capacity_mtpa": 11.0,
         "ev_cr": 9400.0, "inr_per_usd": 67.13, "note": "", "source": "bs_lafarge_2016"},
        {"date": "May-2018", "acquirer": "UltraTech Cement", "target": "Century Textiles (cement)", "capacity_mtpa": 14.6,
         "ev_cr": 8621.0, "inr_per_usd": 67.97, "note": "", "source": "li_century_2018"},
        {"date": "Nov-2018", "acquirer": "UltraTech Cement", "target": "Binani Cement", "capacity_mtpa": 11.0,
         "ev_cr": 7900.0, "inr_per_usd": 71.69, "note": "Distressed (IBC); capacity incl. ~5 MTPA overseas", "source": "bs_binani_2018",
         "distressed": True},
        {"date": "Feb-2020", "acquirer": "Nuvoco Vistas (Nirma)", "target": "Emami Cement", "capacity_mtpa": 8.3,
         "ev_cr": 5500.0, "inr_per_usd": 71.28, "note": "", "source": "nuvoco_emami_2020"},
    ],
}


def default_inputs():
    """Return a fresh, independent copy of every model input."""
    return copy.deepcopy(_INPUTS)
