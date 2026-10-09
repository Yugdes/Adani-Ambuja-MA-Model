"""
Merger Consequences Model — Adani Group / Ambuja Cements & ACC
================================================================
Structure (all amounts INR crore):

  Deal & ownership   consideration paid to Holcim and in the open offers,
                     Adani's resulting direct and look-through stakes
  Financing          USD acquisition debt at the offshore holdco; sponsor
                     equity is the balancing source
  PPA & goodwill     look-through goodwill, NCI at proportionate share of
                     identifiable net assets (Ind AS 103 option)
  Projections        standalone Ambuja (ex ACC dividends) and ACC from the
                     CY2021 actual base
  Synergies          phased schedule, costs to achieve, NPV at the
                     unlevered cost of capital
  Pro forma          consolidated (100%) earnings, NCI, Adani-attributable
                     earnings, holdco debt and cash schedule
  Returns            ROE vs relevered cost of equity, cash ROIC vs unlevered
                     cost of capital, value creation (synergy NPV vs premium)
  Balance sheet      pro forma at close (31-Dec-2021 balance sheet proxy)
  Sensitivities      every cell is a full re-run of this model

The model reads only from the inputs dict passed in (default_inputs() when
omitted), so it can be re-run with changed inputs without side effects.
"""

import copy
import statistics

from model import narrative
from model.assumptions import default_inputs, SOURCES

ENTITIES = ("ambuja", "acc")
FINITE_INTANGIBLES = ("mineral_rights", "customer_relationships", "favourable_contracts")


class MergerModel:

    def __init__(self, inputs=None, run_sensitivities=True):
        self.inp = inputs if inputs is not None else default_inputs()
        self.years = self.inp["projection"]["years"]
        self.tax = self.inp["projection"]["tax_rate_pct"] / 100.0
        self.notes = []

        self._deal()
        self._ownership()
        self._financing()
        self._cost_of_capital()
        self._ppa_goodwill()
        self._projections()
        self._synergies()
        self._pro_forma()
        self._returns()
        self._balance_sheet()
        self._valuation()
        self._precedents()
        self.sensitivity = self._sensitivities() if run_sensitivities else {}

    # ======================================================================
    # DEAL & OWNERSHIP
    # ======================================================================

    def _deal(self):
        amb, acc = self.inp["ambuja_shares"], self.inp["acc_shares"]

        sh = {
            "holcim_ambuja": amb["total_shares_cr"] * amb["holcim_stake_pct"] / 100,
            "open_offer_ambuja": amb["open_offer_shares_tendered_cr"],
            "holcim_acc": acc["total_shares_cr"] * acc["holcim_direct_stake_pct"] / 100,
            "open_offer_acc": acc["open_offer_shares_tendered_cr"],
        }
        price = {"holcim_ambuja": amb["offer_price"], "open_offer_ambuja": amb["offer_price"],
                 "holcim_acc": acc["offer_price"], "open_offer_acc": acc["offer_price"]}
        undisturbed = {"holcim_ambuja": amb["undisturbed_close"], "open_offer_ambuja": amb["undisturbed_close"],
                       "holcim_acc": acc["undisturbed_close"], "open_offer_acc": acc["undisturbed_close"]}
        at_close = {"holcim_ambuja": amb["close_at_completion"], "open_offer_ambuja": amb["close_at_completion"],
                    "holcim_acc": acc["close_at_completion"], "open_offer_acc": acc["close_at_completion"]}

        value = {k: sh[k] * price[k] for k in sh}
        consideration = sum(value.values())
        costs = consideration * self.inp["deal_costs"]["transaction_costs_pct_of_consideration"] / 100
        fx = self.inp["fx"]["inr_per_usd_at_close"]

        premium_paid = sum(sh[k] * (price[k] - undisturbed[k]) for k in sh)
        market_value_at_completion = sum(sh[k] * at_close[k] for k in sh)

        self.deal = {
            "shares_acquired_cr": sh,
            "consideration_by_component": value,
            "consideration_ambuja_shares": value["holcim_ambuja"] + value["open_offer_ambuja"],
            "consideration_acc_shares": value["holcim_acc"] + value["open_offer_acc"],
            "total_consideration": consideration,
            "transaction_costs": costs,
            "total_uses": consideration + costs,
            "total_consideration_usd_bn": consideration / fx / 100,
            "reported_consideration_usd_bn": self.inp["transaction"]["consideration_usd_bn_reported"],
            "premium_to_undisturbed_pct": {
                "ambuja": (amb["offer_price"] / amb["undisturbed_close"] - 1) * 100,
                "acc": (acc["offer_price"] / acc["undisturbed_close"] - 1) * 100,
            },
            "premium_paid_cr": premium_paid,
            "market_value_of_stakes_at_completion": market_value_at_completion,
            "offer_vs_completion_price_pct": {
                "ambuja": (amb["offer_price"] / amb["close_at_completion"] - 1) * 100,
                "acc": (acc["offer_price"] / acc["close_at_completion"] - 1) * 100,
            },
        }

    def _ownership(self):
        amb, acc = self.inp["ambuja_shares"], self.inp["acc_shares"]
        sh = self.deal["shares_acquired_cr"]
        in_ambuja = (sh["holcim_ambuja"] + sh["open_offer_ambuja"]) / amb["total_shares_cr"]
        direct_acc = (sh["holcim_acc"] + sh["open_offer_acc"]) / acc["total_shares_cr"]
        ambuja_in_acc = amb["stake_in_acc_pct"] / 100
        lookthrough_acc = in_ambuja * ambuja_in_acc + direct_acc
        self.own = {
            "adani_in_ambuja": in_ambuja,
            "adani_direct_in_acc": direct_acc,
            "ambuja_in_acc": ambuja_in_acc,
            "adani_lookthrough_in_acc": lookthrough_acc,
            "adani_controlled_in_acc": ambuja_in_acc + direct_acc,
            "nci_in_ambuja": 1 - in_ambuja,
            "nci_lookthrough_in_acc": 1 - lookthrough_acc,
        }

    def _financing(self):
        fx = self.inp["fx"]["inr_per_usd_at_close"]
        tr = self.inp["transaction"]
        debt = self.inp["acq_debt"]
        total_debt = tr["acq_debt_usd_bn"] * fx * 100
        bridge = debt["bridge_usd_bn"] * fx * 100
        term = total_debt - bridge
        equity = self.deal["total_uses"] - total_debt
        assert equity > 0, f"Sponsor equity plug is negative ({equity:,.0f}); debt exceeds uses"

        sources = {"sponsor_equity": equity, "acq_term_loan": term, "acq_bridge_loan": bridge}
        uses = {
            "holcim_ambuja_stake": self.deal["consideration_by_component"]["holcim_ambuja"],
            "holcim_acc_direct_stake": self.deal["consideration_by_component"]["holcim_acc"],
            "ambuja_open_offer": self.deal["consideration_by_component"]["open_offer_ambuja"],
            "acc_open_offer": self.deal["consideration_by_component"]["open_offer_acc"],
            "transaction_costs": self.deal["transaction_costs"],
        }
        self.financing = {
            "sources": sources,
            "uses": uses,
            "total_sources": sum(sources.values()),
            "total_uses": sum(uses.values()),
            "acq_debt_total": total_debt,
            "sponsor_equity_usd_bn": equity / fx / 100,
            "debt_pct_of_sources": total_debt / sum(sources.values()) * 100,
        }

    def _cost_of_capital(self):
        cc = self.inp["cost_of_capital"]
        debt = self.financing["acq_debt_total"]
        equity_value = self.deal["total_consideration"] - debt
        shield = self.tax if self.inp["acq_debt"]["interest_tax_deductible"] else 0.0
        d_to_e = debt / equity_value
        levered_beta = cc["asset_beta"] * (1 + (1 - shield) * d_to_e)
        self.coc = {
            "unlevered_cost_of_capital_pct": cc["risk_free_pct"] + cc["asset_beta"] * cc["equity_risk_premium_pct"],
            "holdco_debt_to_equity": d_to_e,
            "levered_beta": levered_beta,
            "levered_cost_of_equity_pct": cc["risk_free_pct"] + levered_beta * cc["equity_risk_premium_pct"],
        }

    # ======================================================================
    # PURCHASE PRICE ALLOCATION & GOODWILL
    # ======================================================================

    def _ppa_goodwill(self):
        p = self.inp["ppa"]
        t = self.tax
        bs = {"ambuja": self.inp["ambuja_bs"], "acc": self.inp["acc_bs"]}
        out = {}
        for e in ENTITIES:
            su = p["step_ups"][e]
            gross = sum(su.values())
            dtl = gross * t
            book_equity = bs[e]["share_capital"] + bs[e]["reserves"]
            # Ambuja's investments (chiefly the ACC stake) are eliminated: ACC is valued separately
            eliminated = bs[e]["investments"] if e == "ambuja" else 0.0
            fv_net = book_equity - eliminated + gross - dtl
            annual_amort = su["ppe"] / p["ppe_life_years"] + sum(su[k] for k in FINITE_INTANGIBLES) / p["finite_intangible_life_years"]
            out[e] = {
                "step_ups": dict(su),
                "gross_step_up": gross,
                "deferred_tax_liability": dtl,
                "book_equity": book_equity,
                "investment_eliminated": eliminated,
                "fv_net_identifiable_assets": fv_net,
                "annual_amortisation": annual_amort,
                "inventory_release_year1": su["inventory"],
            }

        acc = self.inp["acc_shares"]
        acc_equity_at_offer = acc["total_shares_cr"] * acc["offer_price"]
        # ACC value embedded in the Ambuja shares Adani bought (look-through 50.05% stake), at the ACC offer price
        acc_value_in_ambuja_purchase = self.own["adani_in_ambuja"] * self.own["ambuja_in_acc"] * acc_equity_at_offer
        consideration_ambuja_ex_acc = self.deal["consideration_ambuja_shares"] - acc_value_in_ambuja_purchase
        consideration_acc_lookthrough = acc_value_in_ambuja_purchase + self.deal["consideration_acc_shares"]

        share_amb = self.own["adani_in_ambuja"] * out["ambuja"]["fv_net_identifiable_assets"]
        share_acc = self.own["adani_lookthrough_in_acc"] * out["acc"]["fv_net_identifiable_assets"]
        gw_amb = consideration_ambuja_ex_acc - share_amb
        gw_acc = consideration_acc_lookthrough - share_acc
        if min(gw_amb, gw_acc) < 0:
            self.notes.append("Negative goodwill (bargain purchase) on at least one entity — review step-ups.")

        self.ppa = out
        self.goodwill = {
            "acc_equity_value_at_offer_100pct": acc_equity_at_offer,
            "ambuja_equity_value_at_offer_100pct": self.inp["ambuja_shares"]["total_shares_cr"] * self.inp["ambuja_shares"]["offer_price"],
            "acc_value_in_ambuja_purchase": acc_value_in_ambuja_purchase,
            "consideration_ambuja_ex_acc": consideration_ambuja_ex_acc,
            "consideration_acc_lookthrough": consideration_acc_lookthrough,
            "adani_share_fv_ambuja": share_amb,
            "adani_share_fv_acc": share_acc,
            "ambuja_goodwill": gw_amb,
            "acc_goodwill": gw_acc,
            "total_goodwill": gw_amb + gw_acc,
            "goodwill_pct_of_consideration": (gw_amb + gw_acc) / self.deal["total_consideration"] * 100,
            "new_intangibles": sum(out[e]["step_ups"][k] for e in ENTITIES for k in FINITE_INTANGIBLES + ("brand",)),
        }

    # ======================================================================
    # STANDALONE PROJECTIONS
    # ======================================================================

    def _projections(self):
        pr = self.inp["projection"]
        t = self.tax
        acc_sh = self.inp["acc_shares"]["total_shares_cr"]
        hist = {"ambuja": self.inp["ambuja_hist"], "acc": self.inp["acc_hist"]}
        bs = {"ambuja": self.inp["ambuja_bs"], "acc": self.inp["acc_bs"]}

        acc_div_to_ambuja_cy21 = self.inp["intercompany"]["acc_dps_paid_in_cy2021"] * acc_sh * self.own["ambuja_in_acc"]
        treasury_income_cy21 = (hist["ambuja"]["other_income_normal"][-1] - acc_div_to_ambuja_cy21
                                + hist["acc"]["other_income_normal"][-1])
        treasury_yield = treasury_income_cy21 / (bs["ambuja"]["cash"] + bs["acc"]["cash"])

        proj = {}
        for e in ENTITIES:
            h = hist[e]
            da_pct = h["depreciation"][-1] / h["revenue"][-1]
            growth = pr[f"{e}_revenue_growth_pct"]
            margin = pr[f"{e}_ebitda_margin_pct"]
            rows = {k: [] for k in ("revenue", "ebitda", "depreciation", "treasury_income", "interest_expense", "pbt", "tax", "net_income")}
            rev = h["revenue"][-1]
            for i in range(len(self.years)):
                rev = rev * (1 + growth[i] / 100)
                ebitda = rev * margin[i] / 100
                da = rev * da_pct
                ti = treasury_yield * bs[e]["cash"]
                ie = h["interest_expense"][-1]
                pbt = ebitda - da + ti - ie
                for k, v in (("revenue", rev), ("ebitda", ebitda), ("depreciation", da), ("treasury_income", ti),
                             ("interest_expense", ie), ("pbt", pbt), ("tax", pbt * t), ("net_income", pbt * (1 - t))):
                    rows[k].append(v)
            rows["da_pct_of_revenue"] = da_pct * 100
            proj[e] = rows

        payout = pr["dividend_payout_pct"] / 100
        acc_divs = [payout * ni for ni in proj["acc"]["net_income"]]
        acc_div_to_ambuja = [d * self.own["ambuja_in_acc"] for d in acc_divs]
        # Inter-corporate dividends passed on to shareholders are deductible (s.80M), so they flow through untaxed
        amb_divs = [payout * (ni + d) for ni, d in zip(proj["ambuja"]["net_income"], acc_div_to_ambuja)]
        proj["dividends"] = {"acc_total": acc_divs, "acc_to_ambuja": acc_div_to_ambuja, "ambuja_total": amb_divs}
        proj["treasury_yield_pct"] = treasury_yield * 100
        proj["acc_dividend_in_ambuja_cy2021"] = acc_div_to_ambuja_cy21
        self.proj = proj

    # ======================================================================
    # SYNERGIES
    # ======================================================================

    def _synergies(self):
        s = self.inp["synergies"]
        t = self.tax
        r = self.coc["unlevered_cost_of_capital_pct"] / 100
        g = self.inp["cost_of_capital"]["synergy_terminal_growth_pct"] / 100
        n = len(self.years)

        items = {}
        for key, it in s["items"].items():
            items[key] = {"label": it["label"], "type": it["type"], "run_rate": it["run_rate"],
                          "by_year": [it["run_rate"] * it["phasing_pct"][i] / 100 for i in range(n)]}
        pretax = [sum(it["by_year"][i] for it in items.values()) for i in range(n)]
        run_rate = sum(it["run_rate"] for it in items.values())
        cost_rr = sum(it["run_rate"] for it in items.values() if it["type"] == "cost")
        cta = [s["costs_to_achieve"] * s["costs_to_achieve_phasing_pct"][i] / 100 for i in range(n)]

        disc = [(1 + r) ** (i + 1) for i in range(n)]
        pv_years = [pretax[i] * (1 - t) / disc[i] for i in range(n)]
        terminal_value = run_rate * (1 - t) * (1 + g) / (r - g)
        pv_terminal = terminal_value / disc[-1]
        gross_npv = sum(pv_years) + pv_terminal
        pv_costs = sum(cta[i] * (1 - t) / disc[i] for i in range(n))
        net_npv = gross_npv - pv_costs

        self.syn = {
            "items": items,
            "pretax_by_year": pretax,
            "after_tax_by_year": [x * (1 - t) for x in pretax],
            "run_rate": run_rate,
            "cost_run_rate": cost_rr,
            "revenue_run_rate": run_rate - cost_rr,
            "costs_to_achieve_by_year": cta,
            "costs_to_achieve_total": s["costs_to_achieve"],
            "discount_rate_pct": r * 100,
            "terminal_growth_pct": g * 100,
            "pv_by_year": pv_years,
            "pv_terminal": pv_terminal,
            "gross_npv": gross_npv,
            "pv_costs_to_achieve_after_tax": pv_costs,
            "net_npv": net_npv,
            "terminal_value_share_pct": pv_terminal / gross_npv * 100 if gross_npv else 0.0,
            "gross_npv_per_rupee_of_run_rate": gross_npv / run_rate if run_rate else 0.0,
        }

    # ======================================================================
    # PRO FORMA EARNINGS & HOLDCO DEBT
    # ======================================================================

    def _pro_forma(self):
        t = self.tax
        own = self.own
        d = self.inp["acq_debt"]
        h = self.inp["holdco"]
        pa, pc = self.proj["ambuja"], self.proj["acc"]
        divs = self.proj["dividends"]
        fx = self.inp["fx"]["inr_per_usd_at_close"]
        bridge0 = d["bridge_usd_bn"] * fx * 100
        term0 = self.financing["acq_debt_total"] - bridge0

        debt_open = self.financing["acq_debt_total"]
        equity_open = self.financing["sources"]["sponsor_equity"]
        rows = []
        for i, yr in enumerate(self.years):
            syn = self.syn["pretax_by_year"][i]
            cta = self.syn["costs_to_achieve_by_year"][i]
            ppa_amb = self.ppa["ambuja"]["annual_amortisation"] + (self.ppa["ambuja"]["inventory_release_year1"] if i == 0 else 0.0)
            ppa_acc = self.ppa["acc"]["annual_amortisation"] + (self.ppa["acc"]["inventory_release_year1"] if i == 0 else 0.0)

            if i == 0:
                holdco_interest = term0 * d["term_rate_pct"] / 100 + bridge0 * d["bridge_rate_pct"] / 100
            else:
                holdco_interest = debt_open * d["refi_rate_pct"] / 100
            shield = holdco_interest * t if d["interest_tax_deductible"] else 0.0

            ebitda = pa["ebitda"][i] + pc["ebitda"][i] + syn - cta
            da = pa["depreciation"][i] + pc["depreciation"][i] + ppa_amb + ppa_acc
            ebit = ebitda - da
            treasury = pa["treasury_income"][i] + pc["treasury_income"][i]
            target_interest = pa["interest_expense"][i] + pc["interest_expense"][i]
            pbt = ebit + treasury - target_interest - holdco_interest
            operating_pbt = pbt + holdco_interest
            tax = operating_pbt * t - shield
            ni = pbt - tax

            amb_e, acc_e = pa["ebitda"][i], pc["ebitda"][i]
            blended = (own["adani_in_ambuja"] * amb_e + own["adani_lookthrough_in_acc"] * acc_e) / (amb_e + acc_e)
            attributable = (
                own["adani_in_ambuja"] * pa["net_income"][i]
                + own["adani_lookthrough_in_acc"] * pc["net_income"][i]
                + blended * (syn - cta) * (1 - t)
                - (own["adani_in_ambuja"] * ppa_amb + own["adani_lookthrough_in_acc"] * ppa_acc) * (1 - t)
                - (holdco_interest - shield)
            )
            attributable_ppa_at = (own["adani_in_ambuja"] * ppa_amb + own["adani_lookthrough_in_acc"] * ppa_acc) * (1 - t)
            attributable_cta_at = blended * cta * (1 - t)
            attributable_syn_at = blended * syn * (1 - t)

            div_received = (own["adani_in_ambuja"] * divs["ambuja_total"][i] * (1 - h["wht_on_ambuja_dividends_pct"] / 100)
                            + own["adani_direct_in_acc"] * divs["acc_total"][i] * (1 - h["wht_on_acc_dividends_pct"] / 100))
            holdco_cash_flow = div_received - (holdco_interest - shield)
            repayment = max(holdco_cash_flow, 0.0)
            sponsor_top_up = max(-holdco_cash_flow, 0.0)
            debt_close = debt_open - repayment

            rows.append({
                "year": yr,
                "ambuja_revenue": pa["revenue"][i], "acc_revenue": pc["revenue"][i],
                "combined_revenue": pa["revenue"][i] + pc["revenue"][i],
                "ambuja_ebitda": amb_e, "acc_ebitda": acc_e,
                "synergies": syn, "costs_to_achieve": cta,
                "ebitda": ebitda, "ebitda_margin_pct": ebitda / (pa["revenue"][i] + pc["revenue"][i]) * 100,
                "standalone_da": pa["depreciation"][i] + pc["depreciation"][i],
                "ppa_amortisation": ppa_amb + ppa_acc,
                "ebit": ebit,
                "treasury_income": treasury,
                "target_interest": target_interest,
                "holdco_interest": holdco_interest,
                "pbt": pbt, "tax": tax,
                "consolidated_net_income": ni,
                "blended_ownership_pct": blended * 100,
                "attributable_net_income": attributable,
                "nci_net_income": ni - attributable,
                "attributable_synergies_after_tax": attributable_syn_at,
                "attributable_ppa_after_tax": attributable_ppa_at,
                "attributable_costs_to_achieve_after_tax": attributable_cta_at,
                "holdco_interest_after_shield": holdco_interest - shield,
                "dividends_received_net": div_received,
                "holdco_cash_flow": holdco_cash_flow,
                "dividend_interest_cover": div_received / (holdco_interest - shield) if holdco_interest - shield else None,
                "sponsor_top_up": sponsor_top_up,
                "debt_repayment": repayment,
                "holdco_debt_open": debt_open, "holdco_debt_close": debt_close,
                "sponsor_equity_open": equity_open,
            })
            debt_open = debt_close
            equity_open = equity_open + sponsor_top_up
        self.pf = rows

    # ======================================================================
    # RETURNS
    # ======================================================================

    def _returns(self):
        t = self.tax
        ku = self.coc["unlevered_cost_of_capital_pct"] / 100
        ke = self.coc["levered_cost_of_equity_pct"] / 100
        invested = self.deal["total_uses"]
        out = []
        for r in self.pf:
            # Cash return on the total investment, before acquisition financing:
            # excludes non-cash PPA amortisation and one-off costs to achieve
            cash_earnings = (r["attributable_net_income"] + r["holdco_interest_after_shield"]
                             + r["attributable_ppa_after_tax"] + r["attributable_costs_to_achieve_after_tax"])
            roic = cash_earnings / invested
            ex_syn = cash_earnings - r["attributable_synergies_after_tax"]
            blended = r["blended_ownership_pct"] / 100
            breakeven_syn = max(0.0, (ku * invested - ex_syn) / (blended * (1 - t)))
            roe = r["attributable_net_income"] / r["sponsor_equity_open"]
            out.append({
                "year": r["year"],
                "attributable_net_income": r["attributable_net_income"],
                "sponsor_equity_invested": r["sponsor_equity_open"],
                "roe_pct": roe * 100,
                "levered_cost_of_equity_pct": ke * 100,
                "earns_cost_of_equity": roe > ke,
                "cash_earnings_pre_financing": cash_earnings,
                "cash_roic_pct": roic * 100,
                "cash_roic_ex_synergies_pct": ex_syn / invested * 100,
                "unlevered_cost_of_capital_pct": ku * 100,
                "earns_cost_of_capital": roic > ku,
                "breakeven_synergies_for_roic": breakeven_syn,
                "dividend_interest_cover": r["dividend_interest_cover"],
            })
        self.returns = out

        blended_rr = self.pf[-1]["blended_ownership_pct"] / 100
        adani_npv = blended_rr * self.syn["net_npv"]
        hurdle = self.deal["premium_paid_cr"] + self.deal["transaction_costs"]
        k = self.syn["gross_npv_per_rupee_of_run_rate"]
        # Net synergy NPV is linear in run-rate (phasing shape fixed): solve blended × (k·R − PV costs) = premium + costs
        breakeven_rr = (hurdle / blended_rr + self.syn["pv_costs_to_achieve_after_tax"]) / k if k else None
        self.value = {
            "adani_share_of_synergies_pct": blended_rr * 100,
            "adani_share_of_net_synergy_npv": adani_npv,
            "premium_paid": self.deal["premium_paid_cr"],
            "transaction_costs": self.deal["transaction_costs"],
            "premium_plus_costs": hurdle,
            "net_value_created": adani_npv - hurdle,
            "breakeven_run_rate_synergies": breakeven_rr,
            "synergy_cushion_vs_breakeven_pct": (self.syn["run_rate"] / breakeven_rr - 1) * 100 if breakeven_rr else None,
        }

    # ======================================================================
    # PRO FORMA BALANCE SHEET AT CLOSE
    # ======================================================================

    def _balance_sheet(self):
        a, c = self.inp["ambuja_bs"], self.inp["acc_bs"]
        su = {e: self.ppa[e]["step_ups"] for e in ENTITIES}
        assets = {
            "fixed_assets_and_cwip": a["fixed_assets"] + a["cwip"] + c["fixed_assets"] + c["cwip"] + su["ambuja"]["ppe"] + su["acc"]["ppe"],
            "acquired_intangibles": self.goodwill["new_intangibles"],
            "goodwill": self.goodwill["total_goodwill"],
            "inventories": a["inventories"] + c["inventories"] + su["ambuja"]["inventory"] + su["acc"]["inventory"],
            "trade_receivables": a["trade_receivables"] + c["trade_receivables"],
            "cash": a["cash"] + c["cash"],
            "investments": c["investments"],   # Ambuja's investments (ACC stake) eliminated on consolidation
            "other_assets": a["other_assets"] + c["other_assets"],
        }
        target_borrowings = a["borrowings"] + c["borrowings"]
        liabilities = {
            "acquisition_debt": self.financing["acq_debt_total"],
            "target_borrowings_and_leases": target_borrowings,
            "deferred_tax_on_step_ups": self.ppa["ambuja"]["deferred_tax_liability"] + self.ppa["acc"]["deferred_tax_liability"],
            "other_liabilities": a["other_liabilities"] + c["other_liabilities"],
        }
        nci = (self.own["nci_in_ambuja"] * self.ppa["ambuja"]["fv_net_identifiable_assets"]
               + self.own["nci_lookthrough_in_acc"] * self.ppa["acc"]["fv_net_identifiable_assets"])
        equity = {
            "adani_equity": self.financing["sources"]["sponsor_equity"] - self.deal["transaction_costs"],
            "non_controlling_interests": nci,
        }
        ta = sum(assets.values())
        tle = sum(liabilities.values()) + sum(equity.values())
        assert abs(ta - tle) < 1, f"Balance sheet does not balance: {ta:,.1f} vs {tle:,.1f}"

        ebitda_cy21 = self.inp["ambuja_hist"]["ebitda"][-1] + self.inp["acc_hist"]["ebitda"][-1]
        gross_debt = liabilities["acquisition_debt"] + target_borrowings
        stake_value_completion = self.deal["market_value_of_stakes_at_completion"]
        credit_by_year = []
        for r in self.pf:
            gd = r["holdco_debt_close"] + target_borrowings
            credit_by_year.append({
                "year": r["year"],
                "gross_debt": gd,
                "net_debt": gd - assets["cash"],
                "net_debt_to_ebitda": (gd - assets["cash"]) / r["ebitda"],
                "ebitda_interest_cover": r["ebitda"] / (r["holdco_interest"] + r["target_interest"]),
            })
        self.bs = {
            "assets": assets, "liabilities": liabilities, "equity": equity,
            "total_assets": ta, "total_liabilities_and_equity": tle,
            "credit_at_close": {
                "gross_debt": gross_debt,
                "net_debt": gross_debt - assets["cash"],
                "ebitda_cy2021": ebitda_cy21,
                "gross_debt_to_ebitda": gross_debt / ebitda_cy21,
                "net_debt_to_ebitda": (gross_debt - assets["cash"]) / ebitda_cy21,
                "holdco_ltv_at_cost_pct": liabilities["acquisition_debt"] / self.deal["total_consideration"] * 100,
                "holdco_ltv_at_completion_market_pct": liabilities["acquisition_debt"] / stake_value_completion * 100,
            },
            "credit_by_year": credit_by_year,
        }

    # ======================================================================
    # VALUATION & PRECEDENTS
    # ======================================================================

    def _valuation(self):
        a, c = self.inp["ambuja_bs"], self.inp["acc_bs"]
        own = self.own
        g = self.goodwill
        # 100% equity at offer prices: Ambuja (which includes its 50.05% of ACC) + the 49.95% of ACC Ambuja does not own
        equity_value = g["ambuja_equity_value_at_offer_100pct"] + (1 - own["ambuja_in_acc"]) * g["acc_equity_value_at_offer_100pct"]
        net_debt = a["borrowings"] + c["borrowings"] - a["cash"] - c["cash"]
        ev = equity_value + net_debt
        ebitda = self.inp["ambuja_hist"]["ebitda"][-1] + self.inp["acc_hist"]["ebitda"][-1]
        cap = self.inp["transaction"]["combined_capacity_mtpa"]
        fx = self.inp["fx"]["inr_per_usd_at_close"]
        inr_per_t = ev * 1e7 / (cap * 1e6)
        self.valuation = {
            "equity_value_at_offer": equity_value,
            "net_debt_cy2021": net_debt,
            "enterprise_value": ev,
            "ebitda_cy2021": ebitda,
            "ev_to_ebitda_cy2021": ev / ebitda,
            "ev_to_ebitda_fy2023e": ev / (self.proj["ambuja"]["ebitda"][0] + self.proj["acc"]["ebitda"][0]),
            "capacity_mtpa": cap,
            "ev_per_tonne_inr": inr_per_t,
            "ev_per_tonne_usd": inr_per_t / fx,
        }

    def _precedents(self):
        rows = []
        for p in self.inp["precedents"]:
            inr_t = p["ev_cr"] * 1e7 / (p["capacity_mtpa"] * 1e6)
            rows.append({**p, "ev_per_tonne_inr": inr_t, "ev_per_tonne_usd": inr_t / p["inr_per_usd"],
                         "distressed": p.get("distressed", False), "source_text": SOURCES[p["source"]]})
        usd = [r["ev_per_tonne_usd"] for r in rows]
        usd_clean = [r["ev_per_tonne_usd"] for r in rows if not r["distressed"]]
        this = self.valuation["ev_per_tonne_usd"]
        self.precedents = {
            "rows": rows,
            "count": len(rows),
            "count_ex_distressed": len(usd_clean),
            "mean_usd_per_t": statistics.mean(usd),
            "median_usd_per_t": statistics.median(usd),
            "mean_usd_per_t_ex_distressed": statistics.mean(usd_clean),
            "median_usd_per_t_ex_distressed": statistics.median(usd_clean),
            "this_deal_usd_per_t": this,
            "this_deal_premium_to_median_ex_distressed_pct": (this / statistics.median(usd_clean) - 1) * 100,
        }

    # ======================================================================
    # SENSITIVITIES — each cell is a full re-run of the model
    # ======================================================================

    def _rerun(self, mutate):
        inp = copy.deepcopy(self.inp)
        mutate(inp)
        return MergerModel(inp, run_sensitivities=False)

    @staticmethod
    def _scale_prices(inp, mult):
        inp["ambuja_shares"]["offer_price"] *= mult
        inp["acc_shares"]["offer_price"] *= mult

    @staticmethod
    def _scale_synergies(inp, run_rate):
        base = sum(it["run_rate"] for it in inp["synergies"]["items"].values())
        for it in inp["synergies"]["items"].values():
            it["run_rate"] *= run_rate / base

    def _sensitivities(self):
        last = -1
        price_mults = [0.95, 1.00, 1.05, 1.10, 1.15, 1.20]
        price_rows = []
        for m in price_mults:
            mm = self._rerun(lambda inp: self._scale_prices(inp, m))
            price_rows.append({
                "price_multiplier": m,
                "ambuja_offer_price": mm.inp["ambuja_shares"]["offer_price"],
                "ambuja_premium_pct": mm.deal["premium_to_undisturbed_pct"]["ambuja"],
                "total_consideration": mm.deal["total_consideration"],
                "sponsor_equity": mm.financing["sources"]["sponsor_equity"],
                "goodwill": mm.goodwill["total_goodwill"],
                "cash_roic_final_year_pct": mm.returns[last]["cash_roic_pct"],
                "roe_final_year_pct": mm.returns[last]["roe_pct"],
                "net_value_created": mm.value["net_value_created"],
            })

        rates = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5]
        rate_rows = []
        for rt in rates:
            def mut(inp, rt=rt):
                inp["acq_debt"]["refi_rate_pct"] = rt
            mm = self._rerun(mut)
            rate_rows.append({
                "refi_rate_pct": rt,
                "holdco_interest_final_year": mm.pf[last]["holdco_interest"],
                "attributable_ni_final_year": mm.pf[last]["attributable_net_income"],
                "roe_final_year_pct": mm.returns[last]["roe_pct"],
                "dividend_interest_cover_final_year": mm.pf[last]["dividend_interest_cover"],
            })

        synergy_levels = [0.0, 1000.0, 2000.0, self.syn["run_rate"], 4000.0, 5000.0]
        matrix_value, matrix_roic = [], []
        for m in price_mults:
            row_v, row_r = {"price_multiplier": m}, {"price_multiplier": m}
            for s in synergy_levels:
                def mut(inp, m=m, s=s):
                    self._scale_prices(inp, m)
                    self._scale_synergies(inp, s)
                mm = self._rerun(mut)
                row_v[str(int(round(s)))] = mm.value["net_value_created"]
                row_r[str(int(round(s)))] = mm.returns[last]["cash_roic_pct"]
            matrix_value.append(row_v)
            matrix_roic.append(row_r)

        margin_rows = []
        for bp in [-300, -200, -100, 0, 100, 200, 300]:
            def mut(inp, bp=bp):
                for e in ENTITIES:
                    inp["projection"][f"{e}_ebitda_margin_pct"] = [x + bp / 100 for x in inp["projection"][f"{e}_ebitda_margin_pct"]]
            mm = self._rerun(mut)
            margin_rows.append({"margin_change_bp": bp,
                                "cash_roic_final_year_pct": mm.returns[last]["cash_roic_pct"],
                                "roe_final_year_pct": mm.returns[last]["roe_pct"]})

        shield_rows = []
        for flag in (False, True):
            def mut(inp, flag=flag):
                inp["acq_debt"]["interest_tax_deductible"] = flag
            mm = self._rerun(mut)
            shield_rows.append({"interest_tax_deductible": flag,
                                "attributable_ni_final_year": mm.pf[last]["attributable_net_income"],
                                "roe_final_year_pct": mm.returns[last]["roe_pct"],
                                "levered_cost_of_equity_pct": mm.coc["levered_cost_of_equity_pct"]})

        return {
            "final_year": self.years[last],
            "offer_price": price_rows,
            "refi_rate": rate_rows,
            "synergy_levels": [int(round(s)) for s in synergy_levels],
            "matrix_net_value_created": matrix_value,
            "matrix_cash_roic_final_year": matrix_roic,
            "ebitda_margin": margin_rows,
            "interest_tax_shield": shield_rows,
        }

    # ======================================================================
    # OUTPUT
    # ======================================================================

    def get_summary(self):
        """Every number shown anywhere in the project comes from this dict."""
        fy = self.years
        headline = {
            "total_consideration": self.deal["total_consideration"],
            "total_consideration_usd_bn": self.deal["total_consideration_usd_bn"],
            "acq_debt": self.financing["acq_debt_total"],
            "sponsor_equity": self.financing["sources"]["sponsor_equity"],
            "total_goodwill": self.goodwill["total_goodwill"],
            "ev_to_ebitda_cy2021": self.valuation["ev_to_ebitda_cy2021"],
            "ev_per_tonne_usd": self.valuation["ev_per_tonne_usd"],
            "premium_ambuja_pct": self.deal["premium_to_undisturbed_pct"]["ambuja"],
            "premium_acc_pct": self.deal["premium_to_undisturbed_pct"]["acc"],
            "synergy_run_rate": self.syn["run_rate"],
            "synergy_net_npv": self.syn["net_npv"],
            "net_value_created": self.value["net_value_created"],
            "breakeven_run_rate_synergies": self.value["breakeven_run_rate_synergies"],
            "final_year": fy[-1],
            "cash_roic_final_year_pct": self.returns[-1]["cash_roic_pct"],
            "unlevered_cost_of_capital_pct": self.coc["unlevered_cost_of_capital_pct"],
            "roe_final_year_pct": self.returns[-1]["roe_pct"],
            "levered_cost_of_equity_pct": self.coc["levered_cost_of_equity_pct"],
            "earns_cost_of_capital_any_year": any(r["earns_cost_of_capital"] for r in self.returns),
            "earns_cost_of_equity_any_year": any(r["earns_cost_of_equity"] for r in self.returns),
            "dividend_interest_cover_final_year": self.pf[-1]["dividend_interest_cover"],
        }
        out = _clean({
            "meta": {"years": fy, "currency": "INR crore", "base_year": "CY2021 (year ended 31-Dec-2021)",
                     "notes": self.notes},
            "headline": headline,
            "transaction": self.inp["transaction"],
            "inputs": {k: self.inp[k] for k in ("fx", "ambuja_shares", "acc_shares", "deal_costs", "acq_debt", "holdco",
                                                 "projection", "cost_of_capital", "intercompany")},
            "historicals": {"ambuja": self.inp["ambuja_hist"], "acc": self.inp["acc_hist"],
                            "ambuja_bs": self.inp["ambuja_bs"], "acc_bs": self.inp["acc_bs"]},
            "deal": self.deal,
            "ownership": self.own,
            "financing": self.financing,
            "cost_of_capital": self.coc,
            "ppa": self.ppa,
            "goodwill": self.goodwill,
            "projections": self.proj,
            "synergies": self.syn,
            "pro_forma": self.pf,
            "returns": self.returns,
            "value_creation": self.value,
            "balance_sheet": self.bs,
            "valuation": self.valuation,
            "precedents": self.precedents,
            "sensitivity": self.sensitivity,
            "sources": SOURCES,
        })
        out["narrative"] = narrative.build(out)
        return out

    def print_summary(self):
        s = self.get_summary()
        h = s["headline"]
        line = "=" * 78
        print(line)
        print("ADANI / AMBUJA + ACC — MERGER CONSEQUENCES (INR crore)")
        print(line)
        print(f"Consideration paid          ₹{h['total_consideration']:>10,.0f}  (US${h['total_consideration_usd_bn']:.2f}bn)")
        print(f"  funded by holdco debt     ₹{h['acq_debt']:>10,.0f}  | sponsor equity ₹{h['sponsor_equity']:,.0f}")
        print(f"Premium to undisturbed      Ambuja {h['premium_ambuja_pct']:.1f}% | ACC {h['premium_acc_pct']:.1f}%")
        print(f"EV / EBITDA (CY2021)        {h['ev_to_ebitda_cy2021']:.1f}x | EV/tonne US${h['ev_per_tonne_usd']:.0f}")
        print(f"Goodwill                    ₹{h['total_goodwill']:>10,.0f}")
        print(f"Synergy run-rate            ₹{h['synergy_run_rate']:>10,.0f} | net NPV ₹{h['synergy_net_npv']:,.0f}")
        print(f"Net value created (Adani)   ₹{h['net_value_created']:>10,.0f} | breakeven run-rate ₹{h['breakeven_run_rate_synergies']:,.0f}")
        for r in s["returns"]:
            print(f"  {r['year']}: attributable NI ₹{r['attributable_net_income']:>7,.0f} | ROE {r['roe_pct']:>6.1f}% vs Ke {r['levered_cost_of_equity_pct']:.1f}%"
                  f" | cash ROIC {r['cash_roic_pct']:.1f}% vs {r['unlevered_cost_of_capital_pct']:.2f}%"
                  f" | dividend/interest {r['dividend_interest_cover']:.2f}x")
        print(f"Balance sheet               assets ₹{s['balance_sheet']['total_assets']:,.0f} = L+E ₹{s['balance_sheet']['total_liabilities_and_equity']:,.0f}")
        for n in s["meta"]["notes"]:
            print("NOTE:", n)
        print(line)


def _clean(obj):
    """Round floats for publication so every output shows identical figures."""
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 4)
    return obj
