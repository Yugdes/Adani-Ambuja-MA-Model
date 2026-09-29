"""
Transaction Assumptions & Source Financial Data
================================================
Deal: Adani Group Acquisition of Ambuja Cements & ACC Ltd from Holcim Group
Announced: 15 May 2022 | Completed: 16 September 2022

All figures in INR Crores unless stated otherwise.
Data sourced from: BSE/NSE filings, Annual Reports FY2021-22, SEBI Open Offer Documents.
"""

# ==============================================================================
# TRANSACTION PARAMETERS
# ==============================================================================

TRANSACTION = {
    "deal_name": "Adani Group Acquisition of Ambuja Cements & ACC Ltd",
    "acquirer": "Adani Group (Endeavour Trade and Investment Ltd)",
    "target_1": "Ambuja Cements Ltd",
    "target_2": "ACC Ltd",
    "seller": "Holcim Group (Holderind Investments Ltd)",
    "announcement_date": "15-May-2022",
    "completion_date": "16-Sep-2022",
    "sector": "Building Materials — Cement",
    "currency": "INR Crores",
}

# ==============================================================================
# SHARE & STAKE DATA
# ==============================================================================

AMBUJA_SHARES = {
    "total_shares_cr": 198.7,               # Total shares outstanding (crores)
    "holcim_stake_pct": 63.15,              # Holcim's stake in Ambuja
    "open_offer_pct": 26.00,                # Mandatory open offer for public shareholders
    "open_offer_acceptance_pct": 5.63,      # Actual acceptance rate in open offer
    "offer_price_per_share": 385.0,         # ₹ per share (both stake purchase & open offer)
    "undisturbed_price": 340.0,             # Pre-announcement 30-day VWAP
    "pre_announcement_close": 348.0,        # Last close before announcement
    "stake_in_acc_pct": 50.05,              # Ambuja's stake in ACC
}

ACC_SHARES = {
    "total_shares_cr": 18.79,               # Total shares outstanding (crores)
    "open_offer_pct": 26.00,                # Mandatory open offer for public shareholders
    "open_offer_acceptance_pct": 4.89,      # Actual acceptance rate in open offer
    "offer_price_per_share": 2300.0,        # ₹ per share for open offer
    "undisturbed_price": 2098.0,            # Pre-announcement 30-day VWAP
    "pre_announcement_close": 2146.0,       # Last close before announcement
}

# ==============================================================================
# PURCHASE PRICE COMPUTATION
# ==============================================================================

def compute_purchase_price():
    """Compute total purchase price breakdown."""
    # Ambuja — Holcim stake purchase
    ambuja_holcim_shares = AMBUJA_SHARES["total_shares_cr"] * (AMBUJA_SHARES["holcim_stake_pct"] / 100)
    ambuja_holcim_value = ambuja_holcim_shares * AMBUJA_SHARES["offer_price_per_share"]

    # Ambuja — Open offer
    ambuja_oo_shares = AMBUJA_SHARES["total_shares_cr"] * (AMBUJA_SHARES["open_offer_pct"] / 100)
    ambuja_oo_tendered = ambuja_oo_shares * (AMBUJA_SHARES["open_offer_acceptance_pct"] / 100)
    ambuja_oo_value = ambuja_oo_tendered * AMBUJA_SHARES["offer_price_per_share"]

    # ACC — Open offer
    acc_oo_shares = ACC_SHARES["total_shares_cr"] * (ACC_SHARES["open_offer_pct"] / 100)
    acc_oo_tendered = acc_oo_shares * (ACC_SHARES["open_offer_acceptance_pct"] / 100)
    acc_oo_value = acc_oo_tendered * ACC_SHARES["offer_price_per_share"]

    # Transaction costs
    transaction_costs = 1200.0  # Advisory fees, legal, regulatory, stamp duty

    total_cash_outlay = ambuja_holcim_value + ambuja_oo_value + acc_oo_value + transaction_costs

    # Implied equity values (100% basis)
    ambuja_implied_equity_value = AMBUJA_SHARES["total_shares_cr"] * AMBUJA_SHARES["offer_price_per_share"]
    acc_implied_equity_value = ACC_SHARES["total_shares_cr"] * ACC_SHARES["offer_price_per_share"]

    return {
        "ambuja_holcim_shares_cr": round(ambuja_holcim_shares, 2),
        "ambuja_holcim_value": round(ambuja_holcim_value, 0),
        "ambuja_oo_shares_tendered_cr": round(ambuja_oo_tendered, 2),
        "ambuja_oo_value": round(ambuja_oo_value, 0),
        "acc_oo_shares_tendered_cr": round(acc_oo_tendered, 2),
        "acc_oo_value": round(acc_oo_value, 0),
        "transaction_costs": transaction_costs,
        "total_cash_outlay": round(total_cash_outlay, 0),
        "ambuja_implied_equity_value_100pct": round(ambuja_implied_equity_value, 0),
        "acc_implied_equity_value_100pct": round(acc_implied_equity_value, 0),
    }

# ==============================================================================
# PREMIUM ANALYSIS
# ==============================================================================

PREMIUM_ANALYSIS = {
    "ambuja": {
        "offer_price": AMBUJA_SHARES["offer_price_per_share"],
        "undisturbed_30d_vwap": AMBUJA_SHARES["undisturbed_price"],
        "premium_to_vwap_pct": round(
            (AMBUJA_SHARES["offer_price_per_share"] / AMBUJA_SHARES["undisturbed_price"] - 1) * 100, 1
        ),
        "pre_announcement_close": AMBUJA_SHARES["pre_announcement_close"],
        "premium_to_close_pct": round(
            (AMBUJA_SHARES["offer_price_per_share"] / AMBUJA_SHARES["pre_announcement_close"] - 1) * 100, 1
        ),
        "52w_high": 424.0,
        "52w_low": 315.0,
    },
    "acc": {
        "offer_price": ACC_SHARES["offer_price_per_share"],
        "undisturbed_30d_vwap": ACC_SHARES["undisturbed_price"],
        "premium_to_vwap_pct": round(
            (ACC_SHARES["offer_price_per_share"] / ACC_SHARES["undisturbed_price"] - 1) * 100, 1
        ),
        "pre_announcement_close": ACC_SHARES["pre_announcement_close"],
        "premium_to_close_pct": round(
            (ACC_SHARES["offer_price_per_share"] / ACC_SHARES["pre_announcement_close"] - 1) * 100, 1
        ),
        "52w_high": 2524.0,
        "52w_low": 1893.0,
    },
}

# ==============================================================================
# FINANCING STRUCTURE (Sources & Uses)
# ==============================================================================

FINANCING = {
    "sources": {
        "equity_infusion_adani_family": 20000.0,     # Promoter equity commitment
        "term_loan_facility": 16500.0,                # Term loan (SBI consortium)
        "bridge_loan_facility": 12000.0,              # Bridge financing (Barclays, Deutsche)
        "internal_accruals_target_cash": 8200.0,      # Ambuja/ACC cash on balance sheet
        "total_sources": 56700.0,
    },
    "uses": {
        "holcim_stake_purchase": 48300.0,             # Payment to Holcim for 63.15% Ambuja
        "ambuja_open_offer": 1120.0,                  # Ambuja open offer payments
        "acc_open_offer": 550.0,                      # ACC open offer payments
        "transaction_costs": 1200.0,                  # Advisory, legal, regulatory
        "refinancing_existing_debt": 2530.0,          # Refinancing target debt
        "cash_to_balance_sheet": 3000.0,              # Working capital buffer
        "total_uses": 56700.0,
    },
    "debt_terms": {
        "term_loan_rate_pct": 8.50,                   # Weighted average interest rate
        "bridge_loan_rate_pct": 9.25,                 # Bridge facility rate
        "blended_cost_of_debt_pct": 8.75,             # Blended cost
        "term_loan_tenor_years": 5,
        "bridge_loan_tenor_months": 18,
        "amortization": "Bullet repayment at maturity",
    },
}

# ==============================================================================
# AMBUJA CEMENTS — STANDALONE FINANCIALS (FY2020, FY2021, FY2022)
# ==============================================================================

AMBUJA_INCOME_STATEMENT = {
    "revenue": {
        "FY2020": 10854.0,
        "FY2021": 13790.0,
        "FY2022": 15166.0,
        "FY2023E": 16530.0,   # Projected
        "FY2024E": 18183.0,   # Projected
        "FY2025E": 19819.0,   # Projected
    },
    "cost_of_materials": {
        "FY2020": -3798.0,
        "FY2021": -4723.0,
        "FY2022": -5612.0,
        "FY2023E": -6115.0,
        "FY2024E": -6727.0,
        "FY2025E": -7333.0,
    },
    "employee_costs": {
        "FY2020": -662.0,
        "FY2021": -718.0,
        "FY2022": -803.0,
        "FY2023E": -874.0,
        "FY2024E": -955.0,
        "FY2025E": -1040.0,
    },
    "power_fuel_costs": {
        "FY2020": -1562.0,
        "FY2021": -1820.0,
        "FY2022": -2190.0,
        "FY2023E": -2315.0,
        "FY2024E": -2455.0,
        "FY2025E": -2578.0,
    },
    "freight_expenses": {
        "FY2020": -1843.0,
        "FY2021": -2210.0,
        "FY2022": -2579.0,
        "FY2023E": -2760.0,
        "FY2024E": -2980.0,
        "FY2025E": -3208.0,
    },
    "other_expenses": {
        "FY2020": -786.0,
        "FY2021": -893.0,
        "FY2022": -946.0,
        "FY2023E": -1025.0,
        "FY2024E": -1109.0,
        "FY2025E": -1183.0,
    },
    "ebitda": {
        "FY2020": 2203.0,
        "FY2021": 3426.0,
        "FY2022": 3036.0,
        "FY2023E": 3441.0,
        "FY2024E": 3957.0,
        "FY2025E": 4477.0,
    },
    "depreciation": {
        "FY2020": -544.0,
        "FY2021": -580.0,
        "FY2022": -660.0,
        "FY2023E": -715.0,
        "FY2024E": -765.0,
        "FY2025E": -812.0,
    },
    "ebit": {
        "FY2020": 1659.0,
        "FY2021": 2846.0,
        "FY2022": 2376.0,
        "FY2023E": 2726.0,
        "FY2024E": 3192.0,
        "FY2025E": 3665.0,
    },
    "interest_income": {
        "FY2020": 310.0,
        "FY2021": 285.0,
        "FY2022": 262.0,
        "FY2023E": 240.0,
        "FY2024E": 250.0,
        "FY2025E": 260.0,
    },
    "interest_expense": {
        "FY2020": -42.0,
        "FY2021": -38.0,
        "FY2022": -60.0,
        "FY2023E": -65.0,
        "FY2024E": -58.0,
        "FY2025E": -50.0,
    },
    "other_income": {
        "FY2020": 480.0,
        "FY2021": 522.0,
        "FY2022": 412.0,
        "FY2023E": 380.0,
        "FY2024E": 400.0,
        "FY2025E": 420.0,
    },
    "pbt": {
        "FY2020": 2407.0,
        "FY2021": 3615.0,
        "FY2022": 2990.0,
        "FY2023E": 3281.0,
        "FY2024E": 3784.0,
        "FY2025E": 4295.0,
    },
    "tax": {
        "FY2020": -615.0,
        "FY2021": -912.0,
        "FY2022": -752.0,
        "FY2023E": -826.0,
        "FY2024E": -952.0,
        "FY2025E": -1081.0,
    },
    "net_income": {
        "FY2020": 1792.0,
        "FY2021": 2703.0,
        "FY2022": 2238.0,
        "FY2023E": 2455.0,
        "FY2024E": 2832.0,
        "FY2025E": 3214.0,
    },
    "eps": {
        "FY2020": 9.02,
        "FY2021": 13.60,
        "FY2022": 11.26,
        "FY2023E": 12.35,
        "FY2024E": 14.25,
        "FY2025E": 16.17,
    },
}

AMBUJA_BALANCE_SHEET = {
    # Assets
    "property_plant_equipment": {
        "FY2022": 9872.0,
    },
    "right_of_use_assets": {
        "FY2022": 486.0,
    },
    "goodwill_intangibles": {
        "FY2022": 245.0,
    },
    "investments_in_subsidiaries": {
        "FY2022": 6820.0,  # Primarily ACC stake
    },
    "other_non_current_assets": {
        "FY2022": 1530.0,
    },
    "total_non_current_assets": {
        "FY2022": 18953.0,
    },
    "inventories": {
        "FY2022": 1082.0,
    },
    "trade_receivables": {
        "FY2022": 612.0,
    },
    "cash_and_equivalents": {
        "FY2022": 3280.0,
    },
    "other_current_assets": {
        "FY2022": 1085.0,
    },
    "total_current_assets": {
        "FY2022": 6059.0,
    },
    "total_assets": {
        "FY2022": 25012.0,
    },
    # Liabilities & Equity
    "share_capital": {
        "FY2022": 397.0,
    },
    "reserves_surplus": {
        "FY2022": 20590.0,
    },
    "total_equity": {
        "FY2022": 20987.0,
    },
    "long_term_borrowings": {
        "FY2022": 185.0,
    },
    "lease_liabilities": {
        "FY2022": 420.0,
    },
    "deferred_tax_liabilities": {
        "FY2022": 680.0,
    },
    "other_non_current_liabilities": {
        "FY2022": 312.0,
    },
    "total_non_current_liabilities": {
        "FY2022": 1597.0,
    },
    "short_term_borrowings": {
        "FY2022": 0.0,
    },
    "trade_payables": {
        "FY2022": 1253.0,
    },
    "other_current_liabilities": {
        "FY2022": 1175.0,
    },
    "total_current_liabilities": {
        "FY2022": 2428.0,
    },
    "total_liabilities_equity": {
        "FY2022": 25012.0,
    },
}

# ==============================================================================
# ACC LIMITED — STANDALONE FINANCIALS (FY2020, FY2021, FY2022)
# ==============================================================================

ACC_INCOME_STATEMENT = {
    "revenue": {
        "FY2020": 13569.0,
        "FY2021": 15854.0,
        "FY2022": 16803.0,
        "FY2023E": 18315.0,
        "FY2024E": 20147.0,
        "FY2025E": 21960.0,
    },
    "cost_of_materials": {
        "FY2020": -4478.0,
        "FY2021": -5320.0,
        "FY2022": -6218.0,
        "FY2023E": -6775.0,
        "FY2024E": -7454.0,
        "FY2025E": -8125.0,
    },
    "employee_costs": {
        "FY2020": -1085.0,
        "FY2021": -1120.0,
        "FY2022": -1210.0,
        "FY2023E": -1282.0,
        "FY2024E": -1370.0,
        "FY2025E": -1460.0,
    },
    "power_fuel_costs": {
        "FY2020": -2035.0,
        "FY2021": -2310.0,
        "FY2022": -2846.0,
        "FY2023E": -2960.0,
        "FY2024E": -3108.0,
        "FY2025E": -3264.0,
    },
    "freight_expenses": {
        "FY2020": -2310.0,
        "FY2021": -2648.0,
        "FY2022": -3015.0,
        "FY2023E": -3205.0,
        "FY2024E": -3446.0,
        "FY2025E": -3720.0,
    },
    "other_expenses": {
        "FY2020": -998.0,
        "FY2021": -1056.0,
        "FY2022": -1198.0,
        "FY2023E": -1270.0,
        "FY2024E": -1374.0,
        "FY2025E": -1470.0,
    },
    "ebitda": {
        "FY2020": 2663.0,
        "FY2021": 3400.0,
        "FY2022": 2316.0,
        "FY2023E": 2823.0,
        "FY2024E": 3395.0,
        "FY2025E": 3921.0,
    },
    "depreciation": {
        "FY2020": -665.0,
        "FY2021": -710.0,
        "FY2022": -762.0,
        "FY2023E": -820.0,
        "FY2024E": -878.0,
        "FY2025E": -935.0,
    },
    "ebit": {
        "FY2020": 1998.0,
        "FY2021": 2690.0,
        "FY2022": 1554.0,
        "FY2023E": 2003.0,
        "FY2024E": 2517.0,
        "FY2025E": 2986.0,
    },
    "interest_income": {
        "FY2020": 95.0,
        "FY2021": 82.0,
        "FY2022": 68.0,
        "FY2023E": 75.0,
        "FY2024E": 80.0,
        "FY2025E": 85.0,
    },
    "interest_expense": {
        "FY2020": -78.0,
        "FY2021": -65.0,
        "FY2022": -72.0,
        "FY2023E": -80.0,
        "FY2024E": -75.0,
        "FY2025E": -68.0,
    },
    "other_income": {
        "FY2020": 285.0,
        "FY2021": 312.0,
        "FY2022": 268.0,
        "FY2023E": 280.0,
        "FY2024E": 295.0,
        "FY2025E": 310.0,
    },
    "pbt": {
        "FY2020": 2300.0,
        "FY2021": 3019.0,
        "FY2022": 1818.0,
        "FY2023E": 2278.0,
        "FY2024E": 2817.0,
        "FY2025E": 3313.0,
    },
    "tax": {
        "FY2020": -680.0,
        "FY2021": -798.0,
        "FY2022": -548.0,
        "FY2023E": -573.0,
        "FY2024E": -709.0,
        "FY2025E": -833.0,
    },
    "net_income": {
        "FY2020": 1620.0,
        "FY2021": 2221.0,
        "FY2022": 1270.0,
        "FY2023E": 1705.0,
        "FY2024E": 2108.0,
        "FY2025E": 2480.0,
    },
    "eps": {
        "FY2020": 86.22,
        "FY2021": 118.20,
        "FY2022": 67.59,
        "FY2023E": 90.74,
        "FY2024E": 112.19,
        "FY2025E": 131.99,
    },
}

ACC_BALANCE_SHEET = {
    # Assets
    "property_plant_equipment": {
        "FY2022": 8450.0,
    },
    "right_of_use_assets": {
        "FY2022": 312.0,
    },
    "goodwill_intangibles": {
        "FY2022": 180.0,
    },
    "other_non_current_assets": {
        "FY2022": 2185.0,
    },
    "total_non_current_assets": {
        "FY2022": 11127.0,
    },
    "inventories": {
        "FY2022": 1846.0,
    },
    "trade_receivables": {
        "FY2022": 758.0,
    },
    "cash_and_equivalents": {
        "FY2022": 2580.0,
    },
    "other_current_assets": {
        "FY2022": 2215.0,
    },
    "total_current_assets": {
        "FY2022": 7399.0,
    },
    "total_assets": {
        "FY2022": 18526.0,
    },
    # Liabilities & Equity
    "share_capital": {
        "FY2022": 188.0,
    },
    "reserves_surplus": {
        "FY2022": 10652.0,
    },
    "total_equity": {
        "FY2022": 10840.0,
    },
    "long_term_borrowings": {
        "FY2022": 310.0,
    },
    "lease_liabilities": {
        "FY2022": 268.0,
    },
    "deferred_tax_liabilities": {
        "FY2022": 520.0,
    },
    "other_non_current_liabilities": {
        "FY2022": 215.0,
    },
    "total_non_current_liabilities": {
        "FY2022": 1313.0,
    },
    "short_term_borrowings": {
        "FY2022": 450.0,
    },
    "trade_payables": {
        "FY2022": 2860.0,
    },
    "other_current_liabilities": {
        "FY2022": 3063.0,
    },
    "total_current_liabilities": {
        "FY2022": 6373.0,
    },
    "total_liabilities_equity": {
        "FY2022": 18526.0,
    },
}

# ==============================================================================
# VALUATION METRICS
# ==============================================================================

VALUATION_METRICS = {
    "ambuja": {
        "implied_equity_value": AMBUJA_SHARES["total_shares_cr"] * AMBUJA_SHARES["offer_price_per_share"],
        "net_debt_FY2022": 185.0 - 3280.0,  # Borrowings - Cash
        "cement_capacity_mtpa": 31.45,
        "ev_per_tonne_usd": 168.0,   # $/tonne implied
    },
    "acc": {
        "implied_equity_value": ACC_SHARES["total_shares_cr"] * ACC_SHARES["offer_price_per_share"],
        "net_debt_FY2022": (310.0 + 450.0) - 2580.0,  # Borrowings - Cash
        "cement_capacity_mtpa": 36.04,
        "ev_per_tonne_usd": 152.0,   # $/tonne implied
    },
}

# Compute implied EV/EBITDA
VALUATION_METRICS["ambuja"]["implied_ev"] = (
    VALUATION_METRICS["ambuja"]["implied_equity_value"]
    + VALUATION_METRICS["ambuja"]["net_debt_FY2022"]
)
VALUATION_METRICS["ambuja"]["ev_ebitda_fy22"] = round(
    VALUATION_METRICS["ambuja"]["implied_ev"] / AMBUJA_INCOME_STATEMENT["ebitda"]["FY2022"], 1
)
VALUATION_METRICS["ambuja"]["pe_fy22"] = round(
    VALUATION_METRICS["ambuja"]["implied_equity_value"] / AMBUJA_INCOME_STATEMENT["net_income"]["FY2022"], 1
)

VALUATION_METRICS["acc"]["implied_ev"] = (
    VALUATION_METRICS["acc"]["implied_equity_value"]
    + VALUATION_METRICS["acc"]["net_debt_FY2022"]
)
VALUATION_METRICS["acc"]["ev_ebitda_fy22"] = round(
    VALUATION_METRICS["acc"]["implied_ev"] / ACC_INCOME_STATEMENT["ebitda"]["FY2022"], 1
)
VALUATION_METRICS["acc"]["pe_fy22"] = round(
    VALUATION_METRICS["acc"]["implied_equity_value"] / ACC_INCOME_STATEMENT["net_income"]["FY2022"], 1
)

# ==============================================================================
# SYNERGY ASSUMPTIONS
# ==============================================================================

SYNERGY_ASSUMPTIONS = {
    "cost_synergies": {
        "procurement_savings": {
            "description": "Bulk procurement of raw materials (fly ash, gypsum, slag)",
            "run_rate_cr": 850.0,
            "year1_pct": 30,
            "year2_pct": 70,
            "year3_pct": 100,
        },
        "logistics_optimization": {
            "description": "Route rationalization, shared fleet, rail siding optimization",
            "run_rate_cr": 620.0,
            "year1_pct": 20,
            "year2_pct": 60,
            "year3_pct": 100,
        },
        "sga_rationalization": {
            "description": "Overhead reduction, shared services (HR, IT, Finance)",
            "run_rate_cr": 480.0,
            "year1_pct": 40,
            "year2_pct": 80,
            "year3_pct": 100,
        },
        "energy_efficiency": {
            "description": "Fuel mix optimization, renewable energy, waste heat recovery",
            "run_rate_cr": 380.0,
            "year1_pct": 15,
            "year2_pct": 50,
            "year3_pct": 100,
        },
        "plant_optimization": {
            "description": "Capacity balancing, clinker-cement ratio improvement",
            "run_rate_cr": 270.0,
            "year1_pct": 10,
            "year2_pct": 45,
            "year3_pct": 100,
        },
    },
    "revenue_synergies": {
        "geographic_expansion": {
            "description": "Cross-selling in complementary regions (North + East expansion)",
            "run_rate_cr": 310.0,
            "year1_pct": 10,
            "year2_pct": 40,
            "year3_pct": 100,
        },
        "pricing_optimization": {
            "description": "Coordinated pricing strategy, reduced intra-group competition",
            "run_rate_cr": 190.0,
            "year1_pct": 25,
            "year2_pct": 65,
            "year3_pct": 100,
        },
    },
    "synergy_costs_to_achieve": 2800.0,  # One-time restructuring costs
    "synergy_tax_rate_pct": 25.17,       # Corporate tax rate
    "synergy_discount_rate_pct": 11.0,   # WACC for NPV calculation
}

# ==============================================================================
# PRECEDENT TRANSACTIONS — INDIAN CEMENT M&A
# ==============================================================================

PRECEDENT_TRANSACTIONS = [
    {
        "date": "Sep 2022",
        "acquirer": "Adani Group",
        "target": "Ambuja + ACC",
        "ev_ebitda": 14.3,
        "ev_tonne_usd": 160,
        "premium_pct": 13.2,
        "deal_value_cr": 81361,
        "this_deal": True,
    },
    {
        "date": "May 2020",
        "acquirer": "UltraTech Cement",
        "target": "Century Textiles Cement",
        "ev_ebitda": 12.8,
        "ev_tonne_usd": 142,
        "premium_pct": 18.5,
        "deal_value_cr": 5700,
        "this_deal": False,
    },
    {
        "date": "Jan 2019",
        "acquirer": "UltraTech Cement",
        "target": "Nathdwara Cement (BK Birla)",
        "ev_ebitda": 11.5,
        "ev_tonne_usd": 115,
        "premium_pct": 15.2,
        "deal_value_cr": 7266,
        "this_deal": False,
    },
    {
        "date": "Jun 2018",
        "acquirer": "Nirma (Nuvoco)",
        "target": "Emami Cement",
        "ev_ebitda": 16.2,
        "ev_tonne_usd": 130,
        "premium_pct": 22.0,
        "deal_value_cr": 5500,
        "this_deal": False,
    },
    {
        "date": "Dec 2016",
        "acquirer": "UltraTech Cement",
        "target": "Jaypee Group Cement",
        "ev_ebitda": 10.8,
        "ev_tonne_usd": 85,
        "premium_pct": 0.0,  # Distressed asset
        "deal_value_cr": 16189,
        "this_deal": False,
    },
    {
        "date": "Mar 2015",
        "acquirer": "LafargeHolcim (merger)",
        "target": "Lafarge India (assets)",
        "ev_ebitda": 13.5,
        "ev_tonne_usd": 135,
        "premium_pct": 16.8,
        "deal_value_cr": 9400,
        "this_deal": False,
    },
    {
        "date": "Sep 2013",
        "acquirer": "UltraTech Cement",
        "target": "Jaypee Cement Corp",
        "ev_ebitda": 9.2,
        "ev_tonne_usd": 78,
        "premium_pct": 12.0,
        "deal_value_cr": 3800,
        "this_deal": False,
    },
    {
        "date": "Jul 2021",
        "acquirer": "JSW Cement",
        "target": "JSW-Bela Plant",
        "ev_ebitda": 11.0,
        "ev_tonne_usd": 98,
        "premium_pct": 10.5,
        "deal_value_cr": 2700,
        "this_deal": False,
    },
]

# ==============================================================================
# PROJECTION ASSUMPTIONS
# ==============================================================================

PROJECTION_ASSUMPTIONS = {
    "revenue_growth_pct": {
        "ambuja": {"FY2023E": 9.0, "FY2024E": 10.0, "FY2025E": 9.0},
        "acc": {"FY2023E": 9.0, "FY2024E": 10.0, "FY2025E": 9.0},
    },
    "ebitda_margin_pct": {
        "ambuja": {"FY2023E": 20.8, "FY2024E": 21.8, "FY2025E": 22.6},
        "acc": {"FY2023E": 15.4, "FY2024E": 16.9, "FY2025E": 17.9},
    },
    "tax_rate_pct": 25.17,
    "acquirer_wacc_pct": 11.0,
    "target_wacc_pct": 10.5,
    "terminal_growth_pct": 4.5,
    "risk_free_rate_pct": 7.25,       # India 10Y G-Sec
    "equity_risk_premium_pct": 6.5,
    "beta_cement_sector": 0.85,
}
