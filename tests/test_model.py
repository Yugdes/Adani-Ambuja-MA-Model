"""Integrity, tie-out and input-sensitivity tests for the merger model."""

import pytest

from model.assumptions import default_inputs


def rerun(base_model, mutate):
    """Re-run the model with changed inputs (no global state is touched)."""
    return base_model._rerun(mutate)


# ---------------------------------------------------------------- integrity

def test_balance_sheet_balances(model):
    assert abs(model.bs["total_assets"] - model.bs["total_liabilities_and_equity"]) < 1


def test_sources_equal_uses_and_equity_is_positive(model):
    f = model.financing
    assert abs(f["total_sources"] - f["total_uses"]) < 1
    assert f["sources"]["sponsor_equity"] > 0


def test_target_cash_is_not_a_source(model):
    assert set(model.financing["sources"]) == {"sponsor_equity", "acq_term_loan", "acq_bridge_loan"}


def test_lookthrough_consideration_equals_consideration_paid(model):
    g = model.goodwill
    assert abs(g["consideration_ambuja_ex_acc"] + g["consideration_acc_lookthrough"] - model.deal["total_consideration"]) < 1


def test_attributable_plus_nci_equals_consolidated(model):
    for r in model.pf:
        assert abs(r["attributable_net_income"] + r["nci_net_income"] - r["consolidated_net_income"]) < 1e-6


def test_goodwill_positive_for_both_entities(model):
    assert model.goodwill["ambuja_goodwill"] > 0 and model.goodwill["acc_goodwill"] > 0


# ---------------------------------------------------------------- ties to public data

def test_ownership_ties_to_adani_release(model):
    tr = model.inp["transaction"]
    assert model.own["adani_in_ambuja"] * 100 == pytest.approx(tr["post_deal_ambuja_pct_reported"], abs=0.05)
    assert model.own["adani_controlled_in_acc"] * 100 == pytest.approx(tr["post_deal_acc_pct_reported"], abs=0.05)


def test_consideration_ties_to_reported_usd(model):
    d = model.deal
    assert d["total_consideration_usd_bn"] == pytest.approx(d["reported_consideration_usd_bn"], rel=0.03)


def test_acquisition_debt_is_reported_facility(model):
    inp = model.inp
    expected = inp["transaction"]["acq_debt_usd_bn"] * inp["fx"]["inr_per_usd_at_close"] * 100
    assert model.financing["acq_debt_total"] == pytest.approx(expected)


@pytest.mark.parametrize("entity", ["ambuja_hist", "acc_hist"])
def test_historicals_tie_out(entity):
    h = default_inputs()[entity]
    for i in range(3):
        assert h["revenue"][i] - h["operating_expenses"][i] == pytest.approx(h["ebitda"][i], abs=1)
        pbt = h["ebitda"][i] + h["other_income_normal"][i] + h["exceptional_items"][i] - h["interest_expense"][i] - h["depreciation"][i]
        assert pbt == pytest.approx(h["pbt"][i], abs=2)


@pytest.mark.parametrize("entity", ["ambuja_bs", "acc_bs"])
def test_balance_sheet_inputs_tie_out(entity):
    b = default_inputs()[entity]
    assets = sum(b[k] for k in ("fixed_assets", "cwip", "investments", "inventories", "trade_receivables", "cash", "other_assets"))
    liabilities = sum(b[k] for k in ("share_capital", "reserves", "borrowings", "other_liabilities"))
    assert assets == pytest.approx(b["total_assets"], abs=1)
    assert liabilities == pytest.approx(b["total_assets"], abs=1)


# ---------------------------------------------------------------- the model responds to its inputs

def test_goodwill_rises_one_for_one_with_price_paid(model):
    m2 = rerun(model, lambda i: [i["ambuja_shares"].__setitem__("offer_price", i["ambuja_shares"]["offer_price"] * 1.1),
                                 i["acc_shares"].__setitem__("offer_price", i["acc_shares"]["offer_price"] * 1.1)])
    d_consideration = m2.deal["total_consideration"] - model.deal["total_consideration"]
    d_goodwill = m2.goodwill["total_goodwill"] - model.goodwill["total_goodwill"]
    assert d_consideration > 0
    assert d_goodwill == pytest.approx(d_consideration, abs=1)
    assert abs(m2.bs["total_assets"] - m2.bs["total_liabilities_and_equity"]) < 1


def test_extra_price_is_funded_by_sponsor_equity(model):
    m2 = rerun(model, lambda i: i["acc_shares"].__setitem__("offer_price", 2500.0))
    d_uses = m2.deal["total_uses"] - model.deal["total_uses"]
    d_equity = m2.financing["sources"]["sponsor_equity"] - model.financing["sources"]["sponsor_equity"]
    assert d_equity == pytest.approx(d_uses)


def test_more_debt_means_less_equity_and_more_interest(model):
    m2 = rerun(model, lambda i: i["transaction"].__setitem__("acq_debt_usd_bn", 5.0))
    assert m2.financing["sources"]["sponsor_equity"] < model.financing["sources"]["sponsor_equity"]
    assert m2.pf[-1]["holdco_interest"] > model.pf[-1]["holdco_interest"]


def test_refi_rate_changes_interest_and_returns(model):
    m2 = rerun(model, lambda i: i["acq_debt"].__setitem__("refi_rate_pct", 9.0))
    assert m2.pf[1]["holdco_interest"] > model.pf[1]["holdco_interest"]
    assert m2.returns[-1]["roe_pct"] < model.returns[-1]["roe_pct"]
    assert m2.pf[0]["holdco_interest"] == pytest.approx(model.pf[0]["holdco_interest"])  # Year 1 uses tranche rates


def test_tax_shield_toggle_adds_exactly_the_shield(model):
    m2 = rerun(model, lambda i: i["acq_debt"].__setitem__("interest_tax_deductible", True))
    for a, b in zip(model.pf, m2.pf):
        assert b["attributable_net_income"] - a["attributable_net_income"] == pytest.approx(a["holdco_interest"] * model.tax)


def test_ppa_life_input_is_used(model):
    m2 = rerun(model, lambda i: i["ppa"].__setitem__("ppe_life_years", 10))
    assert m2.pf[-1]["ppa_amortisation"] > model.pf[-1]["ppa_amortisation"]


def test_zero_synergies_destroys_the_premium(model):
    m2 = rerun(model, lambda i: [it.__setitem__("run_rate", 0.0) for it in i["synergies"]["items"].values()])
    v = m2.value
    expected = -v["adani_share_of_synergies_pct"] / 100 * m2.syn["pv_costs_to_achieve_after_tax"] - v["premium_plus_costs"]
    assert v["net_value_created"] == pytest.approx(expected)


def test_breakeven_run_rate_gives_zero_value(model):
    be = model.value["breakeven_run_rate_synergies"]
    m2 = rerun(model, lambda i: model._scale_synergies(i, be))
    assert m2.value["net_value_created"] == pytest.approx(0, abs=1)


def test_roic_breakeven_identity(model):
    t, ku = model.tax, model.coc["unlevered_cost_of_capital_pct"] / 100
    for r, pf in zip(model.returns, model.pf):
        rebuilt = (r["cash_earnings_pre_financing"] - pf["attributable_synergies_after_tax"]
                   + pf["blended_ownership_pct"] / 100 * (1 - t) * r["breakeven_synergies_for_roic"])
        assert rebuilt == pytest.approx(ku * model.deal["total_uses"])


def test_acc_dividend_is_removed_from_ambuja_treasury_income(model):
    p = model.proj
    inp = model.inp
    expected_div = inp["intercompany"]["acc_dps_paid_in_cy2021"] * inp["acc_shares"]["total_shares_cr"] * inp["ambuja_shares"]["stake_in_acc_pct"] / 100
    assert p["acc_dividend_in_ambuja_cy2021"] == pytest.approx(expected_div)
    gross_yield = (inp["ambuja_hist"]["other_income_normal"][-1] + inp["acc_hist"]["other_income_normal"][-1]) / (inp["ambuja_bs"]["cash"] + inp["acc_bs"]["cash"])
    assert p["treasury_yield_pct"] / 100 < gross_yield


# ---------------------------------------------------------------- sensitivities

def test_sensitivity_base_cells_equal_headline(model):
    s = model.sensitivity
    base_price = next(r for r in s["offer_price"] if r["price_multiplier"] == 1.0)
    assert base_price["net_value_created"] == pytest.approx(model.value["net_value_created"])
    assert base_price["cash_roic_final_year_pct"] == pytest.approx(model.returns[-1]["cash_roic_pct"])
    key = str(int(round(model.syn["run_rate"])))
    row_v = next(r for r in s["matrix_net_value_created"] if r["price_multiplier"] == 1.0)
    row_r = next(r for r in s["matrix_cash_roic_final_year"] if r["price_multiplier"] == 1.0)
    assert row_v[key] == pytest.approx(model.value["net_value_created"])
    assert row_r[key] == pytest.approx(model.returns[-1]["cash_roic_pct"])
    base_rate = next(r for r in s["refi_rate"] if r["refi_rate_pct"] == model.inp["acq_debt"]["refi_rate_pct"])
    assert base_rate["roe_final_year_pct"] == pytest.approx(model.returns[-1]["roe_pct"])
    base_margin = next(r for r in s["ebitda_margin"] if r["margin_change_bp"] == 0)
    assert base_margin["cash_roic_final_year_pct"] == pytest.approx(model.returns[-1]["cash_roic_pct"])


def test_sensitivities_are_monotonic(model):
    s = model.sensitivity
    values = [r["net_value_created"] for r in s["offer_price"]]
    assert values == sorted(values, reverse=True)
    roe = [r["roe_final_year_pct"] for r in s["refi_rate"]]
    assert roe == sorted(roe, reverse=True)


def test_running_the_model_does_not_mutate_inputs(model):
    assert model.inp == default_inputs()
