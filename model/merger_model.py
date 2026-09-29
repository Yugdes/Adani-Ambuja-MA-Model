"""
M&A Merger Model — Core Calculations
=====================================
Implements: Purchase Price Allocation (PPA), Goodwill, Pro Forma Financials,
            Accretion/Dilution Analysis, Synergy Analysis, Sensitivity Tables.

Deal: Adani Group Acquisition of Ambuja Cements & ACC Ltd
"""

from model.assumptions import (
    TRANSACTION, AMBUJA_SHARES, ACC_SHARES,
    AMBUJA_INCOME_STATEMENT, AMBUJA_BALANCE_SHEET,
    ACC_INCOME_STATEMENT, ACC_BALANCE_SHEET,
    FINANCING, SYNERGY_ASSUMPTIONS, VALUATION_METRICS,
    PRECEDENT_TRANSACTIONS, PREMIUM_ANALYSIS,
    compute_purchase_price,
)


class MergerModel:
    """Complete M&A merger consequences model."""

    def __init__(self):
        self.purchase_price = compute_purchase_price()
        self.ppa = {}
        self.goodwill = {}
        self.pro_forma = {}
        self.synergies = {}
        self.accretion_dilution = {}
        self.sensitivity = {}

        # Run all calculations
        self._compute_ppa()
        self._compute_synergies()
        self._compute_pro_forma()
        self._compute_accretion_dilution()
        self._compute_sensitivity()

    # ==========================================================================
    # PURCHASE PRICE ALLOCATION (PPA)
    # ==========================================================================

    def _compute_ppa(self):
        """
        Allocate purchase price to fair value of identifiable net assets.
        Excess = Goodwill.
        """
        # ---- Book Values (from balance sheets) ----
        ambuja_book_equity = AMBUJA_BALANCE_SHEET["total_equity"]["FY2022"]
        acc_book_equity = ACC_BALANCE_SHEET["total_equity"]["FY2022"]

        # ---- Fair Value Adjustments (Step-up from book to fair value) ----
        # These are typical PPA adjustments for a cement company acquisition

        # Ambuja FV Adjustments
        ambuja_fv_adjustments = {
            "ppe_step_up": {
                "description": "Fair value step-up on Property, Plant & Equipment",
                "book_value": AMBUJA_BALANCE_SHEET["property_plant_equipment"]["FY2022"],
                "fair_value_adjustment": 3200.0,  # Replacement cost > book value
                "fair_value": AMBUJA_BALANCE_SHEET["property_plant_equipment"]["FY2022"] + 3200.0,
            },
            "mineral_rights": {
                "description": "Limestone & mining rights (not on books)",
                "book_value": 0.0,
                "fair_value_adjustment": 4500.0,   # Valued based on reserves & DCF
                "fair_value": 4500.0,
            },
            "brand_value": {
                "description": "Ambuja brand — relief from royalty method",
                "book_value": 0.0,
                "fair_value_adjustment": 2800.0,
                "fair_value": 2800.0,
            },
            "customer_relationships": {
                "description": "Customer contracts & relationships — MEEM method",
                "book_value": 0.0,
                "fair_value_adjustment": 1200.0,
                "fair_value": 1200.0,
            },
            "inventory_step_up": {
                "description": "Fair value of finished goods inventory",
                "book_value": AMBUJA_BALANCE_SHEET["inventories"]["FY2022"],
                "fair_value_adjustment": 180.0,
                "fair_value": AMBUJA_BALANCE_SHEET["inventories"]["FY2022"] + 180.0,
            },
            "favorable_contracts": {
                "description": "Below-market power purchase agreements",
                "book_value": 0.0,
                "fair_value_adjustment": 650.0,
                "fair_value": 650.0,
            },
            "deferred_tax_on_stepup": {
                "description": "Deferred tax liability on fair value step-ups",
                "book_value": 0.0,
                "fair_value_adjustment": -3153.0,  # 25.17% * total step-ups
                "fair_value": -3153.0,
            },
        }

        # ACC FV Adjustments
        acc_fv_adjustments = {
            "ppe_step_up": {
                "description": "Fair value step-up on Property, Plant & Equipment",
                "book_value": ACC_BALANCE_SHEET["property_plant_equipment"]["FY2022"],
                "fair_value_adjustment": 2800.0,
                "fair_value": ACC_BALANCE_SHEET["property_plant_equipment"]["FY2022"] + 2800.0,
            },
            "mineral_rights": {
                "description": "Limestone & mining rights (not on books)",
                "book_value": 0.0,
                "fair_value_adjustment": 3800.0,
                "fair_value": 3800.0,
            },
            "brand_value": {
                "description": "ACC brand — relief from royalty method",
                "book_value": 0.0,
                "fair_value_adjustment": 2200.0,
                "fair_value": 2200.0,
            },
            "customer_relationships": {
                "description": "Customer contracts & relationships — MEEM method",
                "book_value": 0.0,
                "fair_value_adjustment": 950.0,
                "fair_value": 950.0,
            },
            "inventory_step_up": {
                "description": "Fair value of finished goods inventory",
                "book_value": ACC_BALANCE_SHEET["inventories"]["FY2022"],
                "fair_value_adjustment": 220.0,
                "fair_value": ACC_BALANCE_SHEET["inventories"]["FY2022"] + 220.0,
            },
            "favorable_contracts": {
                "description": "Below-market fuel supply agreements",
                "book_value": 0.0,
                "fair_value_adjustment": 420.0,
                "fair_value": 420.0,
            },
            "deferred_tax_on_stepup": {
                "description": "Deferred tax liability on fair value step-ups",
                "book_value": 0.0,
                "fair_value_adjustment": -2616.0,  # 25.17% * total step-ups
                "fair_value": -2616.0,
            },
        }

        # ---- Compute Fair Value of Net Identifiable Assets ----
        ambuja_total_fv_adj = sum(
            item["fair_value_adjustment"] for item in ambuja_fv_adjustments.values()
        )
        acc_total_fv_adj = sum(
            item["fair_value_adjustment"] for item in acc_fv_adjustments.values()
        )

        ambuja_fv_net_assets = ambuja_book_equity + ambuja_total_fv_adj
        acc_fv_net_assets = acc_book_equity + acc_total_fv_adj

        # ---- Purchase Price (for stake acquired) ----
        # Ambuja: 63.15% from Holcim + 5.63% of 26% from open offer = ~64.6% total
        ambuja_stake_acquired_pct = (
            AMBUJA_SHARES["holcim_stake_pct"]
            + AMBUJA_SHARES["open_offer_pct"] * AMBUJA_SHARES["open_offer_acceptance_pct"] / 100
        )
        # ACC: controlled via Ambuja's 50.05% stake + 4.89% of 26% from open offer
        acc_direct_stake_pct = (
            ACC_SHARES["open_offer_pct"] * ACC_SHARES["open_offer_acceptance_pct"] / 100
        )
        acc_effective_stake_pct = AMBUJA_SHARES["stake_in_acc_pct"] + acc_direct_stake_pct

        # Purchase price for 100% equivalent
        ambuja_pp_100pct = self.purchase_price["ambuja_implied_equity_value_100pct"]
        acc_pp_100pct = self.purchase_price["acc_implied_equity_value_100pct"]

        # ---- Goodwill Calculation ----
        # Goodwill = Purchase Price (100% implied) - Fair Value of Net Identifiable Assets
        ambuja_goodwill = ambuja_pp_100pct - ambuja_fv_net_assets
        acc_goodwill = acc_pp_100pct - acc_fv_net_assets
        total_goodwill = ambuja_goodwill + acc_goodwill

        self.ppa = {
            "ambuja": {
                "book_equity": ambuja_book_equity,
                "fv_adjustments": ambuja_fv_adjustments,
                "total_fv_adjustment": round(ambuja_total_fv_adj, 0),
                "fv_net_assets": round(ambuja_fv_net_assets, 0),
                "implied_equity_value_100pct": ambuja_pp_100pct,
                "stake_acquired_pct": round(ambuja_stake_acquired_pct, 2),
            },
            "acc": {
                "book_equity": acc_book_equity,
                "fv_adjustments": acc_fv_adjustments,
                "total_fv_adjustment": round(acc_total_fv_adj, 0),
                "fv_net_assets": round(acc_fv_net_assets, 0),
                "implied_equity_value_100pct": acc_pp_100pct,
                "stake_acquired_pct": round(acc_effective_stake_pct, 2),
            },
        }

        self.goodwill = {
            "ambuja_goodwill": round(ambuja_goodwill, 0),
            "acc_goodwill": round(acc_goodwill, 0),
            "total_goodwill": round(total_goodwill, 0),
            "goodwill_as_pct_of_pp": round(
                total_goodwill / (ambuja_pp_100pct + acc_pp_100pct) * 100, 1
            ),
        }

    # ==========================================================================
    # SYNERGY ANALYSIS
    # ==========================================================================

    def _compute_synergies(self):
        """Compute synergy values with phasing and NPV."""
        sa = SYNERGY_ASSUMPTIONS

        cost_synergies = sa["cost_synergies"]
        revenue_synergies = sa["revenue_synergies"]

        # ---- Cost Synergy Schedule ----
        cost_syn_details = {}
        total_cost_syn_runrate = 0.0
        total_cost_syn_y1 = 0.0
        total_cost_syn_y2 = 0.0
        total_cost_syn_y3 = 0.0

        for key, syn in cost_synergies.items():
            y1 = syn["run_rate_cr"] * syn["year1_pct"] / 100
            y2 = syn["run_rate_cr"] * syn["year2_pct"] / 100
            y3 = syn["run_rate_cr"] * syn["year3_pct"] / 100
            cost_syn_details[key] = {
                "description": syn["description"],
                "run_rate": syn["run_rate_cr"],
                "year1": round(y1, 0),
                "year2": round(y2, 0),
                "year3": round(y3, 0),
            }
            total_cost_syn_runrate += syn["run_rate_cr"]
            total_cost_syn_y1 += y1
            total_cost_syn_y2 += y2
            total_cost_syn_y3 += y3

        # ---- Revenue Synergy Schedule ----
        rev_syn_details = {}
        total_rev_syn_runrate = 0.0
        total_rev_syn_y1 = 0.0
        total_rev_syn_y2 = 0.0
        total_rev_syn_y3 = 0.0

        for key, syn in revenue_synergies.items():
            y1 = syn["run_rate_cr"] * syn["year1_pct"] / 100
            y2 = syn["run_rate_cr"] * syn["year2_pct"] / 100
            y3 = syn["run_rate_cr"] * syn["year3_pct"] / 100
            rev_syn_details[key] = {
                "description": syn["description"],
                "run_rate": syn["run_rate_cr"],
                "year1": round(y1, 0),
                "year2": round(y2, 0),
                "year3": round(y3, 0),
            }
            total_rev_syn_runrate += syn["run_rate_cr"]
            total_rev_syn_y1 += y1
            total_rev_syn_y2 += y2
            total_rev_syn_y3 += y3

        # ---- Total Synergies ----
        total_runrate = total_cost_syn_runrate + total_rev_syn_runrate
        total_y1 = total_cost_syn_y1 + total_rev_syn_y1
        total_y2 = total_cost_syn_y2 + total_rev_syn_y2
        total_y3 = total_cost_syn_y3 + total_rev_syn_y3

        # ---- After-Tax Synergies ----
        tax_rate = sa["synergy_tax_rate_pct"] / 100
        at_y1 = total_y1 * (1 - tax_rate)
        at_y2 = total_y2 * (1 - tax_rate)
        at_y3 = total_y3 * (1 - tax_rate)
        at_runrate = total_runrate * (1 - tax_rate)

        # ---- NPV of Synergies ----
        discount_rate = sa["synergy_discount_rate_pct"] / 100
        # Year 1-3 phased synergies + terminal value of run-rate synergies
        terminal_growth = 0.03  # 3% growth in synergies beyond year 3
        terminal_value = at_runrate * (1 + terminal_growth) / (discount_rate - terminal_growth)

        pv_y1 = at_y1 / (1 + discount_rate) ** 1
        pv_y2 = at_y2 / (1 + discount_rate) ** 2
        pv_y3 = at_y3 / (1 + discount_rate) ** 3
        pv_terminal = terminal_value / (1 + discount_rate) ** 3

        npv_synergies = pv_y1 + pv_y2 + pv_y3 + pv_terminal
        npv_net_of_costs = npv_synergies - sa["synergy_costs_to_achieve"]

        self.synergies = {
            "cost_synergies": cost_syn_details,
            "revenue_synergies": rev_syn_details,
            "totals": {
                "cost_synergy_runrate": round(total_cost_syn_runrate, 0),
                "revenue_synergy_runrate": round(total_rev_syn_runrate, 0),
                "total_runrate": round(total_runrate, 0),
                "year1": round(total_y1, 0),
                "year2": round(total_y2, 0),
                "year3": round(total_y3, 0),
            },
            "after_tax": {
                "year1": round(at_y1, 0),
                "year2": round(at_y2, 0),
                "year3": round(at_y3, 0),
                "runrate": round(at_runrate, 0),
            },
            "npv": {
                "pv_year1": round(pv_y1, 0),
                "pv_year2": round(pv_y2, 0),
                "pv_year3": round(pv_y3, 0),
                "pv_terminal": round(pv_terminal, 0),
                "total_npv": round(npv_synergies, 0),
                "costs_to_achieve": sa["synergy_costs_to_achieve"],
                "npv_net_of_costs": round(npv_net_of_costs, 0),
            },
        }

    # ==========================================================================
    # PRO FORMA COMBINED FINANCIALS
    # ==========================================================================

    def _compute_pro_forma(self):
        """Build pro forma combined income statement and balance sheet."""
        periods = ["FY2023E", "FY2024E", "FY2025E"]

        # ---- Pro Forma Income Statement ----
        pro_forma_is = {}
        for period in periods:
            ambuja_rev = AMBUJA_INCOME_STATEMENT["revenue"][period]
            acc_rev = ACC_INCOME_STATEMENT["revenue"][period]
            combined_rev = ambuja_rev + acc_rev

            ambuja_ebitda = AMBUJA_INCOME_STATEMENT["ebitda"][period]
            acc_ebitda = ACC_INCOME_STATEMENT["ebitda"][period]

            # Synergy contribution
            year_idx = periods.index(period)
            syn_keys = ["year1", "year2", "year3"]
            syn_pretax = self.synergies["totals"][syn_keys[year_idx]]

            combined_ebitda = ambuja_ebitda + acc_ebitda + syn_pretax

            ambuja_da = abs(AMBUJA_INCOME_STATEMENT["depreciation"][period])
            acc_da = abs(ACC_INCOME_STATEMENT["depreciation"][period])
            # Additional depreciation from PPA step-ups (amortized over 15 years)
            ppa_amortization = (
                abs(self.ppa["ambuja"]["total_fv_adjustment"])
                + abs(self.ppa["acc"]["total_fv_adjustment"])
            ) / 15  # Simplified straight-line over 15 years
            combined_da = ambuja_da + acc_da + ppa_amortization

            combined_ebit = combined_ebitda - combined_da

            # Interest
            ambuja_int_inc = AMBUJA_INCOME_STATEMENT["interest_income"][period]
            acc_int_inc = ACC_INCOME_STATEMENT["interest_income"][period]
            ambuja_int_exp = abs(AMBUJA_INCOME_STATEMENT["interest_expense"][period])
            acc_int_exp = abs(ACC_INCOME_STATEMENT["interest_expense"][period])

            # Incremental interest from acquisition debt
            acq_debt = (
                FINANCING["sources"]["term_loan_facility"]
                + FINANCING["sources"]["bridge_loan_facility"]
            )
            # Assume bridge loan is refinanced by year 2
            if year_idx == 0:
                incr_interest = acq_debt * FINANCING["debt_terms"]["blended_cost_of_debt_pct"] / 100
            else:
                # Bridge refinanced into term loan
                incr_interest = (
                    FINANCING["sources"]["term_loan_facility"]
                    * FINANCING["debt_terms"]["term_loan_rate_pct"] / 100
                )
                # Some paydown
                incr_interest *= (1 - 0.05 * year_idx)  # Gradual paydown

            combined_int_inc = ambuja_int_inc + acc_int_inc
            combined_int_exp = ambuja_int_exp + acc_int_exp + incr_interest

            ambuja_other = AMBUJA_INCOME_STATEMENT["other_income"][period]
            acc_other = ACC_INCOME_STATEMENT["other_income"][period]
            combined_other = ambuja_other + acc_other

            combined_pbt = combined_ebit + combined_int_inc - combined_int_exp + combined_other

            tax_rate = 0.2517
            combined_tax = combined_pbt * tax_rate
            combined_net_income = combined_pbt - combined_tax

            # Combined shares for EPS (Ambuja basis since Adani controls through Ambuja)
            combined_shares = AMBUJA_SHARES["total_shares_cr"]
            combined_eps = combined_net_income / combined_shares

            pro_forma_is[period] = {
                "ambuja_revenue": ambuja_rev,
                "acc_revenue": acc_rev,
                "synergy_revenue_impact": 0,  # Revenue synergies reflected in EBITDA
                "combined_revenue": round(combined_rev, 0),
                "ambuja_ebitda": ambuja_ebitda,
                "acc_ebitda": acc_ebitda,
                "synergy_ebitda_impact": round(syn_pretax, 0),
                "combined_ebitda": round(combined_ebitda, 0),
                "combined_ebitda_margin_pct": round(combined_ebitda / combined_rev * 100, 1),
                "combined_da": round(combined_da, 0),
                "ppa_amortization": round(ppa_amortization, 0),
                "combined_ebit": round(combined_ebit, 0),
                "combined_interest_income": round(combined_int_inc, 0),
                "combined_interest_expense": round(combined_int_exp, 0),
                "incremental_interest": round(incr_interest, 0),
                "combined_other_income": round(combined_other, 0),
                "combined_pbt": round(combined_pbt, 0),
                "combined_tax": round(combined_tax, 0),
                "combined_net_income": round(combined_net_income, 0),
                "combined_eps": round(combined_eps, 2),
            }

        # ---- Pro Forma Balance Sheet (at close, FY2022 basis) ----
        # Combined balance sheet with PPA and financing adjustments

        # Assets
        combined_ppe = (
            AMBUJA_BALANCE_SHEET["property_plant_equipment"]["FY2022"]
            + ACC_BALANCE_SHEET["property_plant_equipment"]["FY2022"]
            + self.ppa["ambuja"]["fv_adjustments"]["ppe_step_up"]["fair_value_adjustment"]
            + self.ppa["acc"]["fv_adjustments"]["ppe_step_up"]["fair_value_adjustment"]
        )

        combined_intangibles = (
            AMBUJA_BALANCE_SHEET["goodwill_intangibles"]["FY2022"]
            + ACC_BALANCE_SHEET["goodwill_intangibles"]["FY2022"]
            # New intangible assets from PPA
            + self.ppa["ambuja"]["fv_adjustments"]["mineral_rights"]["fair_value_adjustment"]
            + self.ppa["ambuja"]["fv_adjustments"]["brand_value"]["fair_value_adjustment"]
            + self.ppa["ambuja"]["fv_adjustments"]["customer_relationships"]["fair_value_adjustment"]
            + self.ppa["ambuja"]["fv_adjustments"]["favorable_contracts"]["fair_value_adjustment"]
            + self.ppa["acc"]["fv_adjustments"]["mineral_rights"]["fair_value_adjustment"]
            + self.ppa["acc"]["fv_adjustments"]["brand_value"]["fair_value_adjustment"]
            + self.ppa["acc"]["fv_adjustments"]["customer_relationships"]["fair_value_adjustment"]
            + self.ppa["acc"]["fv_adjustments"]["favorable_contracts"]["fair_value_adjustment"]
        )

        combined_goodwill = self.goodwill["total_goodwill"]

        combined_cash = (
            AMBUJA_BALANCE_SHEET["cash_and_equivalents"]["FY2022"]
            + ACC_BALANCE_SHEET["cash_and_equivalents"]["FY2022"]
            - FINANCING["sources"]["internal_accruals_target_cash"]  # Cash used for deal
            + FINANCING["uses"]["cash_to_balance_sheet"]  # Working capital buffer
        )

        combined_other_assets = (
            AMBUJA_BALANCE_SHEET["inventories"]["FY2022"]
            + ACC_BALANCE_SHEET["inventories"]["FY2022"]
            + AMBUJA_BALANCE_SHEET["trade_receivables"]["FY2022"]
            + ACC_BALANCE_SHEET["trade_receivables"]["FY2022"]
            + AMBUJA_BALANCE_SHEET["other_current_assets"]["FY2022"]
            + ACC_BALANCE_SHEET["other_current_assets"]["FY2022"]
            + AMBUJA_BALANCE_SHEET["other_non_current_assets"]["FY2022"]
            + ACC_BALANCE_SHEET["other_non_current_assets"]["FY2022"]
            + AMBUJA_BALANCE_SHEET["right_of_use_assets"]["FY2022"]
            + ACC_BALANCE_SHEET["right_of_use_assets"]["FY2022"]
        )

        total_pro_forma_assets = (
            combined_ppe + combined_intangibles + combined_goodwill
            + combined_cash + combined_other_assets
        )

        # Liabilities
        combined_equity = (
            AMBUJA_BALANCE_SHEET["total_equity"]["FY2022"]
            + ACC_BALANCE_SHEET["total_equity"]["FY2022"]
            + FINANCING["sources"]["equity_infusion_adani_family"]  # New equity
            + self.ppa["ambuja"]["total_fv_adjustment"]  # PPA adjustments to equity
            + self.ppa["acc"]["total_fv_adjustment"]
        )

        combined_debt = (
            AMBUJA_BALANCE_SHEET["long_term_borrowings"]["FY2022"]
            + ACC_BALANCE_SHEET["long_term_borrowings"]["FY2022"]
            + ACC_BALANCE_SHEET["short_term_borrowings"]["FY2022"]
            + FINANCING["sources"]["term_loan_facility"]
            + FINANCING["sources"]["bridge_loan_facility"]
            - FINANCING["uses"]["refinancing_existing_debt"]
        )

        combined_other_liabilities = (
            AMBUJA_BALANCE_SHEET["lease_liabilities"]["FY2022"]
            + ACC_BALANCE_SHEET["lease_liabilities"]["FY2022"]
            + AMBUJA_BALANCE_SHEET["deferred_tax_liabilities"]["FY2022"]
            + ACC_BALANCE_SHEET["deferred_tax_liabilities"]["FY2022"]
            + abs(self.ppa["ambuja"]["fv_adjustments"]["deferred_tax_on_stepup"]["fair_value_adjustment"])
            + abs(self.ppa["acc"]["fv_adjustments"]["deferred_tax_on_stepup"]["fair_value_adjustment"])
            + AMBUJA_BALANCE_SHEET["other_non_current_liabilities"]["FY2022"]
            + ACC_BALANCE_SHEET["other_non_current_liabilities"]["FY2022"]
            + AMBUJA_BALANCE_SHEET["trade_payables"]["FY2022"]
            + ACC_BALANCE_SHEET["trade_payables"]["FY2022"]
            + AMBUJA_BALANCE_SHEET["other_current_liabilities"]["FY2022"]
            + ACC_BALANCE_SHEET["other_current_liabilities"]["FY2022"]
        )

        total_pro_forma_le = combined_equity + combined_debt + combined_other_liabilities

        # Credit metrics
        combined_ebitda_fy22 = (
            AMBUJA_INCOME_STATEMENT["ebitda"]["FY2022"]
            + ACC_INCOME_STATEMENT["ebitda"]["FY2022"]
        )
        net_debt = combined_debt - combined_cash

        pro_forma_bs = {
            "assets": {
                "ppe": round(combined_ppe, 0),
                "intangible_assets": round(combined_intangibles, 0),
                "goodwill": round(combined_goodwill, 0),
                "cash": round(combined_cash, 0),
                "other_assets": round(combined_other_assets, 0),
                "total_assets": round(total_pro_forma_assets, 0),
            },
            "liabilities_equity": {
                "total_equity": round(combined_equity, 0),
                "total_debt": round(combined_debt, 0),
                "other_liabilities": round(combined_other_liabilities, 0),
                "total_le": round(total_pro_forma_le, 0),
            },
            "credit_metrics": {
                "gross_debt": round(combined_debt, 0),
                "net_debt": round(net_debt, 0),
                "combined_ebitda": round(combined_ebitda_fy22, 0),
                "gross_debt_to_ebitda": round(combined_debt / combined_ebitda_fy22, 1),
                "net_debt_to_ebitda": round(net_debt / combined_ebitda_fy22, 1),
                "interest_coverage": round(
                    combined_ebitda_fy22 / (
                        abs(AMBUJA_INCOME_STATEMENT["interest_expense"]["FY2022"])
                        + abs(ACC_INCOME_STATEMENT["interest_expense"]["FY2022"])
                        + (FINANCING["sources"]["term_loan_facility"]
                           + FINANCING["sources"]["bridge_loan_facility"])
                        * FINANCING["debt_terms"]["blended_cost_of_debt_pct"] / 100
                    ), 1
                ),
            },
        }

        self.pro_forma = {
            "income_statement": pro_forma_is,
            "balance_sheet": pro_forma_bs,
        }

    # ==========================================================================
    # ACCRETION / DILUTION ANALYSIS
    # ==========================================================================

    def _compute_accretion_dilution(self):
        """
        Compare standalone acquirer EPS vs. pro forma EPS to determine
        whether the transaction is accretive or dilutive.
        """
        periods = ["FY2023E", "FY2024E", "FY2025E"]

        ad_analysis = {}
        for period in periods:
            # Standalone Acquirer EPS (Ambuja standalone)
            standalone_eps = AMBUJA_INCOME_STATEMENT["eps"][period]

            # Pro Forma EPS (with synergies)
            pf_eps_with_syn = self.pro_forma["income_statement"][period]["combined_eps"]

            # Pro Forma EPS without synergies
            year_idx = periods.index(period)
            syn_keys = ["year1", "year2", "year3"]
            syn_pretax = self.synergies["totals"][syn_keys[year_idx]]
            syn_after_tax = syn_pretax * (1 - 0.2517)

            pf_ni_without_syn = (
                self.pro_forma["income_statement"][period]["combined_net_income"]
                - syn_after_tax
            )
            pf_eps_without_syn = pf_ni_without_syn / AMBUJA_SHARES["total_shares_cr"]

            # Accretion / Dilution
            ad_with_syn_pct = (pf_eps_with_syn / standalone_eps - 1) * 100
            ad_without_syn_pct = (pf_eps_without_syn / standalone_eps - 1) * 100

            ad_analysis[period] = {
                "standalone_eps": standalone_eps,
                "pf_eps_with_synergies": round(pf_eps_with_syn, 2),
                "pf_eps_without_synergies": round(pf_eps_without_syn, 2),
                "accretion_dilution_with_syn_pct": round(ad_with_syn_pct, 1),
                "accretion_dilution_without_syn_pct": round(ad_without_syn_pct, 1),
                "is_accretive_with_syn": ad_with_syn_pct > 0,
                "is_accretive_without_syn": ad_without_syn_pct > 0,
                "synergy_contribution_to_eps": round(
                    pf_eps_with_syn - pf_eps_without_syn, 2
                ),
            }

        # ---- Breakeven Synergy ----
        # What level of pre-tax synergies would make Year 1 EPS neutral?
        fy23_standalone_ni = AMBUJA_INCOME_STATEMENT["net_income"]["FY2023E"]
        fy23_pf_ni_no_syn = (
            self.pro_forma["income_statement"]["FY2023E"]["combined_net_income"]
            - self.synergies["totals"]["year1"] * (1 - 0.2517)
        )
        eps_gap = fy23_standalone_ni - fy23_pf_ni_no_syn  # How much NI we need from synergies
        breakeven_pretax_synergy = eps_gap / (1 - 0.2517) if eps_gap > 0 else 0

        self.accretion_dilution = {
            "annual": ad_analysis,
            "breakeven_synergy_pretax_cr": round(breakeven_pretax_synergy, 0),
            "actual_year1_synergy_cr": round(self.synergies["totals"]["year1"], 0),
            "synergy_cushion_cr": round(
                self.synergies["totals"]["year1"] - breakeven_pretax_synergy, 0
            ),
        }

    # ==========================================================================
    # SENSITIVITY ANALYSIS
    # ==========================================================================

    def _compute_sensitivity(self):
        """Build sensitivity tables for key variables."""

        # ---- Sensitivity 1: EPS Accretion/Dilution to Purchase Price Premium ----
        base_premium = PREMIUM_ANALYSIS["ambuja"]["premium_to_vwap_pct"]
        premiums = [0, 5, 10, base_premium, 15, 20, 25, 30]

        premium_sensitivity = []
        for prem in premiums:
            # Adjust purchase price based on premium
            adj_price = AMBUJA_SHARES["undisturbed_price"] * (1 + prem / 100)
            adj_pp = AMBUJA_SHARES["total_shares_cr"] * adj_price

            # Simplified: higher price = more goodwill = same P&L but more debt service
            base_pp = self.purchase_price["ambuja_implied_equity_value_100pct"]
            delta_pp = adj_pp - base_pp
            delta_interest = delta_pp * FINANCING["debt_terms"]["blended_cost_of_debt_pct"] / 100

            fy24_pf_ni = self.pro_forma["income_statement"]["FY2024E"]["combined_net_income"]
            adj_ni = fy24_pf_ni - delta_interest * (1 - 0.2517)
            adj_eps = adj_ni / AMBUJA_SHARES["total_shares_cr"]

            standalone_eps = AMBUJA_INCOME_STATEMENT["eps"]["FY2024E"]
            ad_pct = (adj_eps / standalone_eps - 1) * 100

            premium_sensitivity.append({
                "premium_pct": prem,
                "offer_price": round(adj_price, 0),
                "implied_pp_cr": round(adj_pp, 0),
                "pf_eps": round(adj_eps, 2),
                "accretion_dilution_pct": round(ad_pct, 1),
            })

        # ---- Sensitivity 2: EPS to Cost of Debt ----
        cost_of_debt_range = [7.0, 7.5, 8.0, 8.5, 8.75, 9.0, 9.5, 10.0, 10.5]
        debt_sensitivity = []
        for cod in cost_of_debt_range:
            base_interest = (
                FINANCING["sources"]["term_loan_facility"]
                * FINANCING["debt_terms"]["term_loan_rate_pct"] / 100
            )
            adj_interest = (
                FINANCING["sources"]["term_loan_facility"] * cod / 100
            )
            delta_int = adj_interest - base_interest

            fy24_pf_ni = self.pro_forma["income_statement"]["FY2024E"]["combined_net_income"]
            adj_ni = fy24_pf_ni - delta_int * (1 - 0.2517)
            adj_eps = adj_ni / AMBUJA_SHARES["total_shares_cr"]

            standalone_eps = AMBUJA_INCOME_STATEMENT["eps"]["FY2024E"]
            ad_pct = (adj_eps / standalone_eps - 1) * 100

            debt_sensitivity.append({
                "cost_of_debt_pct": cod,
                "annual_interest_cr": round(adj_interest, 0),
                "pf_eps": round(adj_eps, 2),
                "accretion_dilution_pct": round(ad_pct, 1),
            })

        # ---- Sensitivity 3: 2D — Premium vs. Synergies (FY2024E) ----
        premium_range = [5, 10, 13.2, 15, 20, 25]
        synergy_range = [1000, 1500, 2000, 2600, 3100, 3500, 4000]

        matrix = []
        for prem in premium_range:
            row = {"premium_pct": prem}
            for syn in synergy_range:
                # Adjust for premium
                adj_price = AMBUJA_SHARES["undisturbed_price"] * (1 + prem / 100)
                adj_pp = AMBUJA_SHARES["total_shares_cr"] * adj_price
                base_pp = self.purchase_price["ambuja_implied_equity_value_100pct"]
                delta_pp = adj_pp - base_pp
                delta_interest = delta_pp * FINANCING["debt_terms"]["blended_cost_of_debt_pct"] / 100

                # Adjust for synergies (year 2 = ~65% of run-rate)
                syn_y2 = syn * 0.65
                base_syn_y2 = self.synergies["totals"]["year2"]
                delta_syn = syn_y2 - base_syn_y2

                fy24_pf_ni = self.pro_forma["income_statement"]["FY2024E"]["combined_net_income"]
                adj_ni = (
                    fy24_pf_ni
                    - delta_interest * (1 - 0.2517)
                    + delta_syn * (1 - 0.2517)
                )
                adj_eps = adj_ni / AMBUJA_SHARES["total_shares_cr"]
                standalone_eps = AMBUJA_INCOME_STATEMENT["eps"]["FY2024E"]
                ad_pct = (adj_eps / standalone_eps - 1) * 100

                row[f"syn_{syn}"] = round(ad_pct, 1)
            matrix.append(row)

        self.sensitivity = {
            "premium_sensitivity": premium_sensitivity,
            "debt_cost_sensitivity": debt_sensitivity,
            "premium_vs_synergy_matrix": matrix,
            "synergy_range_for_matrix": synergy_range,
        }

    # ==========================================================================
    # SUMMARY OUTPUT
    # ==========================================================================

    def get_summary(self):
        """Return a comprehensive summary dict of all model outputs."""
        return {
            "transaction": TRANSACTION,
            "purchase_price": self.purchase_price,
            "premium_analysis": PREMIUM_ANALYSIS,
            "ppa": self.ppa,
            "goodwill": self.goodwill,
            "financing": FINANCING,
            "pro_forma": self.pro_forma,
            "synergies": self.synergies,
            "accretion_dilution": self.accretion_dilution,
            "sensitivity": self.sensitivity,
            "precedent_transactions": PRECEDENT_TRANSACTIONS,
            "valuation_metrics": VALUATION_METRICS,
        }

    def print_summary(self):
        """Print a formatted summary to console."""
        print("=" * 80)
        print("M&A MERGER MODEL — ADANI GROUP / AMBUJA CEMENTS & ACC")
        print("=" * 80)

        print("\n--- PURCHASE PRICE ---")
        pp = self.purchase_price
        print(f"  Holcim Stake (63.15% Ambuja):  ₹{pp['ambuja_holcim_value']:>10,.0f} Cr")
        print(f"  Ambuja Open Offer:             ₹{pp['ambuja_oo_value']:>10,.0f} Cr")
        print(f"  ACC Open Offer:                ₹{pp['acc_oo_value']:>10,.0f} Cr")
        print(f"  Transaction Costs:             ₹{pp['transaction_costs']:>10,.0f} Cr")
        print(f"  Total Cash Outlay:             ₹{pp['total_cash_outlay']:>10,.0f} Cr")

        print("\n--- PREMIUM ANALYSIS ---")
        for entity in ["ambuja", "acc"]:
            pa = PREMIUM_ANALYSIS[entity]
            print(f"  {entity.upper()}: Offer ₹{pa['offer_price']:.0f} | "
                  f"Premium to VWAP: {pa['premium_to_vwap_pct']}% | "
                  f"Premium to Close: {pa['premium_to_close_pct']}%")

        print("\n--- GOODWILL ---")
        gw = self.goodwill
        print(f"  Ambuja Goodwill:   ₹{gw['ambuja_goodwill']:>10,.0f} Cr")
        print(f"  ACC Goodwill:      ₹{gw['acc_goodwill']:>10,.0f} Cr")
        print(f"  Total Goodwill:    ₹{gw['total_goodwill']:>10,.0f} Cr")
        print(f"  Goodwill % of PP:  {gw['goodwill_as_pct_of_pp']}%")

        print("\n--- SYNERGIES (Run-Rate) ---")
        syn = self.synergies["totals"]
        print(f"  Cost Synergies:    ₹{syn['cost_synergy_runrate']:>10,.0f} Cr/year")
        print(f"  Revenue Synergies: ₹{syn['revenue_synergy_runrate']:>10,.0f} Cr/year")
        print(f"  Total Run-Rate:    ₹{syn['total_runrate']:>10,.0f} Cr/year")
        npv = self.synergies["npv"]
        print(f"  NPV of Synergies:  ₹{npv['total_npv']:>10,.0f} Cr")
        print(f"  NPV (net of costs):₹{npv['npv_net_of_costs']:>10,.0f} Cr")

        print("\n--- ACCRETION / DILUTION ---")
        for period in ["FY2023E", "FY2024E", "FY2025E"]:
            ad = self.accretion_dilution["annual"][period]
            status = "ACCRETIVE" if ad["is_accretive_with_syn"] else "DILUTIVE"
            print(f"  {period}: Standalone EPS ₹{ad['standalone_eps']:.2f} → "
                  f"PF EPS ₹{ad['pf_eps_with_synergies']:.2f} "
                  f"({ad['accretion_dilution_with_syn_pct']:+.1f}%) — {status}")

        be = self.accretion_dilution
        print(f"\n  Breakeven Synergy: ₹{be['breakeven_synergy_pretax_cr']:,.0f} Cr/year")
        print(f"  Actual Year 1:     ₹{be['actual_year1_synergy_cr']:,.0f} Cr/year")

        print("\n--- PRO FORMA CREDIT METRICS ---")
        cm = self.pro_forma["balance_sheet"]["credit_metrics"]
        print(f"  Gross Debt / EBITDA: {cm['gross_debt_to_ebitda']}x")
        print(f"  Net Debt / EBITDA:   {cm['net_debt_to_ebitda']}x")
        print(f"  Interest Coverage:   {cm['interest_coverage']}x")

        print("\n" + "=" * 80)
        print("Model Complete. See output/Adani_Ambuja_MA_Model.xlsx for full workbook.")
        print("=" * 80)
