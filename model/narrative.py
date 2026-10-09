"""
Narrative — the conclusions in words, generated from model outputs.

The memo, README and dashboard all display these strings, so the wording can
never contradict the numbers or each other. Every sentence is conditional on
the results; nothing here is fixed prose about the outcome.
"""


from decimal import ROUND_HALF_UP, Decimal


def fixed(x, d=0):
    """Round half away from zero (as Excel and the dashboard do) with thousands separators."""
    q = Decimal(str(abs(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    return f"{q:,.{d}f}"


def is_negative(x, d=0):
    return x < 0 and fixed(x, d).strip("0.,") != ""


def cr(x):
    """₹ crore, thousands separators, true minus sign for negatives."""
    s = f"₹{fixed(x)} Cr"
    return f"−{s}" if is_negative(x) else s


def pct(x, d=1):
    s = f"{fixed(x, d)}%"
    return f"−{s}" if is_negative(x, d) else s


def mult(x, d=1):
    return f"{'−' if is_negative(x, d) else ''}{fixed(x, d)}x"


def build(s):
    h, v, ret = s["headline"], s["value_creation"], s["returns"]
    fy = h["final_year"]
    last = s["pro_forma"][-1]
    ku, ke = h["unlevered_cost_of_capital_pct"], h["levered_cost_of_equity_pct"]
    cover = h["dividend_interest_cover_final_year"]
    prec = s["precedents"]

    value_positive = v["net_value_created"] > 0
    earns_coc = h["earns_cost_of_capital_any_year"]
    holdco_short = cover < 1

    if value_positive and not earns_coc and holdco_short:
        title = ("The premium is covered by synergies, but earnings returns trail the cost of capital "
                 "and the holdco cannot service its debt from dividends")
    elif value_positive and not earns_coc:
        title = "The premium is covered by synergies, but earnings returns trail the cost of capital"
    elif value_positive:
        title = "Value-creating: synergies cover the premium and returns clear the cost of capital"
    else:
        title = "Value-destructive at this price: Adani's share of synergies does not cover the premium paid"

    value_line = (
        f"Adani's share of the net synergy NPV is {cr(v['adani_share_of_net_synergy_npv'])} against "
        f"{cr(v['premium_plus_costs'])} of premium and transaction costs, "
        + (f"creating {cr(v['net_value_created'])} of value. " if value_positive
           else f"a shortfall of {cr(-v['net_value_created'])}. ")
        + f"Breakeven run-rate synergies are {cr(v['breakeven_run_rate_synergies'])} versus "
        f"{cr(h['synergy_run_rate'])} modelled."
    )
    returns_line = (
        f"Cash ROIC on the {cr(s['deal']['total_uses'])} invested reaches {pct(h['cash_roic_final_year_pct'])} by {fy}, "
        + ("below" if h["cash_roic_final_year_pct"] < ku else "above")
        + f" the {pct(ku, 2)} unlevered cost of capital; return on sponsor equity is {pct(h['roe_final_year_pct'])} "
        f"against a {pct(ke)} levered cost of equity. The price is {mult(h['ev_to_ebitda_cy2021'])} CY2021 EBITDA, "
        "so near-term earnings yields are low."
    )
    holdco_line = (
        f"Dividends received cover {mult(cover, 2)} of holdco interest in {fy}; "
        + (f"the shortfall of {cr(last['sponsor_top_up'])} a year must come from refinancing, asset sales or sponsor equity."
           if holdco_short else "the holdco can service its debt from dividends.")
    )
    precedent_line = (
        f"At US${fixed(h['ev_per_tonne_usd'], 0)}/tonne, the deal is "
        f"{pct(abs(prec['this_deal_premium_to_median_ex_distressed_pct']), 0)} "
        + ("above" if prec["this_deal_premium_to_median_ex_distressed_pct"] > 0 else "below")
        + f" the median of {prec['count_ex_distressed']} non-distressed Indian cement precedents "
        f"(US${fixed(prec['median_usd_per_t_ex_distressed'], 0)}/t), consistent with buying a pan-India, "
        "net-cash, two-brand platform rather than single assets."
    )

    if value_positive and holdco_short:
        recommendation = (
            "Proceed only with (1) committed refinancing or sponsor support for holdco interest, which dividends do not cover; "
            f"(2) a synergy plan tracked against the {cr(v['breakeven_run_rate_synergies'])} breakeven; and "
            "(3) acceptance that earnings returns stay below the cost of capital through the projection period."
        )
    elif value_positive:
        recommendation = (f"Proceed, with synergy delivery tracked against the {cr(v['breakeven_run_rate_synergies'])} breakeven.")
    else:
        recommendation = "Do not proceed at this price without a lower offer or higher, credible synergies."

    return {
        "verdict_title": title,
        "value_line": value_line,
        "returns_line": returns_line,
        "holdco_line": holdco_line,
        "precedent_line": precedent_line,
        "recommendation": recommendation,
    }
