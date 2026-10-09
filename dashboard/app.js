/**
 * Dashboard renderer — Adani × Ambuja & ACC merger consequences.
 * Every figure comes from window.MODEL (model_data.js, written by run_model.py).
 * This file contains no deal numbers; if MODEL is missing, an error is shown.
 */

const RENDERERS = [
    renderHero, renderVerdict, renderKpis, renderSourcesUses, renderOwnership, renderPremium,
    renderValuation, renderEvTonneChart, renderPrecedents, renderPpa, renderGoodwill,
    renderIncomeStatement, renderBalanceSheet, renderCredit, renderSynergyTable, renderNpv,
    renderReturns, renderValueTable, renderHoldco, renderBreakeven, renderMatrices,
    renderRateTable, renderMarginTable, renderShieldTable, renderAssumptions, renderHistory, renderSources,
];

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    if (typeof window.MODEL === 'undefined') {
        showError('Model data (model_data.js) is missing. Run "python run_model.py" to generate it.');
        return;
    }
    const failures = [];
    RENDERERS.forEach(fn => {
        try { fn(window.MODEL); } catch (e) { failures.push(`${fn.name}: ${e.message}`); }
    });
    if (failures.length) showError('Some sections failed to render: ' + failures.join(' | '));
});

// ---------------------------------------------------------------- helpers
const $ = id => document.getElementById(id);

function showError(msg) {
    const el = $('loadError');
    if (el) { el.textContent = msg; el.hidden = false; }
}

function initNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        contents.forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        const target = $(`tab-${tab.dataset.tab}`);
        if (target) target.classList.add('active');
    }));
}

function num(x, d = 0) {
    if (x === null || x === undefined || Number.isNaN(x)) return '—';
    const s = Math.abs(x).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
    return Number(x.toFixed(d)) < 0 ? `(${s})` : s;
}
function cr(x) {
    if (x === null || x === undefined) return '—';
    const s = `₹${Math.abs(x).toLocaleString('en-US', { maximumFractionDigits: 0 })} Cr`;
    return Math.round(x) < 0 ? `−${s}` : s;
}
function pct(x, d = 1) {
    if (x === null || x === undefined) return '—';
    const s = `${Math.abs(x).toFixed(d)}%`;
    return Number(x.toFixed(d)) < 0 ? `−${s}` : s;
}
const mult = (x, d = 1) => (x === null || x === undefined ? '—' : `${x.toFixed(d)}x`);
const signClass = x => (x < 0 ? 'neg-text' : 'pos-text');
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/** rows: [label, ...cells] ; opts.total marks bold rows; cells may be {v, cls}. */
function rowsHtml(rows) {
    return rows.map(r => {
        if (r === null) return '<tr><td colspan="9" style="height:6px"></td></tr>';
        const [label, ...cells] = r.cells || r;
        const cls = r.total ? ' class="total"' : r.highlight ? ' class="highlight"' : '';
        const tds = cells.map(c => (typeof c === 'object' && c !== null)
            ? `<td class="num ${c.cls || ''}">${c.v}</td>` : `<td class="num">${c}</td>`).join('');
        return `<tr${cls}><td>${label}</td>${tds}</tr>`;
    }).join('');
}
function headHtml(first, cols) {
    return `<thead><tr><th>${first}</th>${cols.map(c => `<th class="num">${c}</th>`).join('')}</tr></thead>`;
}
const years = M => M.meta.years;
const byYear = (M, key) => M.pro_forma.map(r => r[key]);

// ---------------------------------------------------------------- overview
function renderHero(M) {
    const t = M.transaction, h = M.headline;
    $('heroSubtitle').textContent =
        `Announced ${t.announcement_date} · Completed ${t.completion_date} · Seller: ${t.seller} · Buyer: ${t.acquirer}`;
    const stats = [
        [cr(h.total_consideration), `Consideration (US$${h.total_consideration_usd_bn.toFixed(2)}bn)`],
        [`${num(t.combined_capacity_mtpa, 1)} MTPA`, 'Combined Capacity'],
        [mult(h.ev_to_ebitda_cy2021), 'EV / EBITDA (CY2021)'],
        [pct(h.premium_ambuja_pct), 'Ambuja Premium to Undisturbed'],
    ];
    $('heroStats').innerHTML = stats.map((s, i) =>
        (i ? '<div class="hero-stat-divider"></div>' : '') +
        `<div class="hero-stat"><span class="hero-stat-value">${s[0]}</span><span class="hero-stat-label">${s[1]}</span></div>`).join('');
}

function renderVerdict(M) {
    const n = M.narrative;
    const el = $('verdict');
    el.classList.add(M.value_creation.net_value_created > 0 ? 'mixed' : 'warn');
    el.innerHTML = `<h3>${esc(n.verdict_title)}</h3>
        <ul><li><b>Value:</b> ${esc(n.value_line)}</li>
            <li><b>Returns:</b> ${esc(n.returns_line)}</li>
            <li><b>Holdco:</b> ${esc(n.holdco_line)}</li>
            <li><b>Precedents:</b> ${esc(n.precedent_line)}</li></ul>
        <p><b>Recommendation:</b> ${esc(n.recommendation)}</p>`;
}

function renderKpis(M) {
    const h = M.headline, v = M.value_creation;
    const cards = [
        ['Consideration Paid', cr(h.total_consideration), `+ ${cr(M.deal.transaction_costs)} costs · ${pct(M.financing.debt_pct_of_sources, 0)} debt-funded`],
        ['Goodwill', cr(h.total_goodwill), `${pct(M.goodwill.goodwill_pct_of_consideration, 0)} of consideration`],
        ['Run-Rate Synergies', cr(h.synergy_run_rate), `Net NPV ${cr(h.synergy_net_npv)}`],
        ['Net Value Created (Adani)', cr(v.net_value_created), `Breakeven run-rate ${cr(v.breakeven_run_rate_synergies)}`, signClass(v.net_value_created)],
        [`Cash ROIC ${h.final_year}`, pct(h.cash_roic_final_year_pct), `vs ${pct(h.unlevered_cost_of_capital_pct, 2)} cost of capital`,
            h.cash_roic_final_year_pct < h.unlevered_cost_of_capital_pct ? 'neg-text' : 'pos-text'],
        [`Dividend / Interest ${h.final_year}`, mult(h.dividend_interest_cover_final_year, 2), 'Holdco debt service from dividends',
            h.dividend_interest_cover_final_year < 1 ? 'neg-text' : 'pos-text'],
    ];
    $('kpiCards').innerHTML = cards.map(c => `<div class="metric-card">
        <div class="metric-value ${c[3] || ''}">${c[1]}</div><div class="metric-label">${c[0]}</div>
        <div class="metric-detail">${c[2]}</div></div>`).join('');
}

function renderSourcesUses(M) {
    const f = M.financing, fx = M.inputs.fx.inr_per_usd_at_close;
    const s = f.sources, u = f.uses, ts = f.total_sources, tu = f.total_uses;
    const share = (x, t) => pct(x / t * 100);
    $('sourcesTable').innerHTML = rowsHtml([
        ['Acquisition bridge loans (holdco)', num(s.acq_bridge_loan), share(s.acq_bridge_loan, ts)],
        ['Acquisition term loans (holdco)', num(s.acq_term_loan), share(s.acq_term_loan, ts)],
        ['Sponsor equity (balancing item)', num(s.sponsor_equity), share(s.sponsor_equity, ts)],
        { cells: ['Total sources', num(ts), '100.0%'], total: true },
    ]);
    $('usesTable').innerHTML = rowsHtml([
        ['Holcim stake in Ambuja', num(u.holcim_ambuja_stake), share(u.holcim_ambuja_stake, tu)],
        ['Holcim direct stake in ACC', num(u.holcim_acc_direct_stake), share(u.holcim_acc_direct_stake, tu)],
        ['Ambuja open offer (tendered)', num(u.ambuja_open_offer), share(u.ambuja_open_offer, tu)],
        ['ACC open offer (tendered)', num(u.acc_open_offer), share(u.acc_open_offer, tu)],
        ['Transaction costs (expensed)', num(u.transaction_costs), share(u.transaction_costs, tu)],
        { cells: ['Total uses', num(tu), '100.0%'], total: true },
    ]);
    $('financingNote').textContent =
        `Debt is the reported US$${M.transaction.acq_debt_usd_bn.toFixed(2)}bn of acquisition facilities, translated at ₹${fx.toFixed(2)}/US$ and held at the offshore holdco. ` +
        'Ambuja/ACC cash is not a source: Indian law bars a company financing the purchase of its own shares, and minorities own part of both companies.';
}

function renderOwnership(M) {
    const o = M.ownership, t = M.transaction;
    $('ownershipTable').innerHTML = rowsHtml([
        ['Adani stake in Ambuja', pct(o.adani_in_ambuja * 100, 2)],
        ['  as reported by Adani', pct(t.post_deal_ambuja_pct_reported, 2)],
        ['Adani direct stake in ACC', pct(o.adani_direct_in_acc * 100, 2)],
        ['Adani-controlled stake in ACC (direct + via Ambuja)', pct(o.adani_controlled_in_acc * 100, 2)],
        ['  as reported by Adani', pct(t.post_deal_acc_pct_reported, 2)],
        { cells: ['Adani look-through economic interest in ACC', pct(o.adani_lookthrough_in_acc * 100, 2)], total: true },
    ]);
}

function renderPremium(M) {
    const a = M.inputs.ambuja_shares, c = M.inputs.acc_shares, d = M.deal;
    $('premiumTable').innerHTML = rowsHtml([
        ['Offer price (₹/share)', num(a.offer_price, 2), num(c.offer_price, 2)],
        [`Undisturbed close, ${M.transaction.undisturbed_price_date} (₹)`, num(a.undisturbed_close, 2), num(c.undisturbed_close, 2)],
        { cells: ['Premium to undisturbed', pct(d.premium_to_undisturbed_pct.ambuja), pct(d.premium_to_undisturbed_pct.acc)], total: true },
        ['Close on completion day (₹)', num(a.close_at_completion, 2), num(c.close_at_completion, 2)],
        ['Offer vs completion-day close', pct(d.offer_vs_completion_price_pct.ambuja), pct(d.offer_vs_completion_price_pct.acc)],
        ['Premium paid over undisturbed value (₹ Cr)', { v: num(d.premium_paid_cr) }, ''],
    ]);
}

// ---------------------------------------------------------------- valuation
function renderValuation(M) {
    const v = M.valuation;
    $('valuationTable').innerHTML = rowsHtml([
        ['100% equity value at offer prices', num(v.equity_value_at_offer)],
        [`Net debt / (net cash), ${M.transaction.balance_sheet_date}`, num(v.net_debt_cy2021)],
        { cells: ['Enterprise value', num(v.enterprise_value)], total: true },
        ['EV / EBITDA, CY2021 actual', mult(v.ev_to_ebitda_cy2021)],
        ['EV / EBITDA, FY2023E', mult(v.ev_to_ebitda_fy2023e)],
        ['EV per tonne (₹)', num(v.ev_per_tonne_inr)],
        ['EV per tonne (US$)', num(v.ev_per_tonne_usd)],
    ]);
}

function renderEvTonneChart(M) {
    const rows = M.precedents.rows.map(r => ({ label: `${r.acquirer.split(' ')[0]} / ${r.target}`, v: r.ev_per_tonne_usd, me: false }));
    rows.push({ label: 'Adani / Ambuja + ACC', v: M.valuation.ev_per_tonne_usd, me: true });
    const max = Math.max(...rows.map(r => r.v));
    $('evTonneChart').innerHTML = rows.sort((a, b) => b.v - a.v).map(r => `
        <div class="prec-bar-row"><span class="prec-bar-label">${esc(r.label)}</span>
        <div class="prec-bar-track"><div class="prec-bar-fill ${r.me ? 'this-deal' : 'other'}" style="width:${r.v / max * 100}%"></div></div>
        <span class="prec-bar-value">$${num(r.v)}</span></div>`).join('');
}

function renderPrecedents(M) {
    const p = M.precedents;
    const rows = p.rows.map(r => `<tr><td>${r.date}</td><td>${esc(r.acquirer)}</td><td>${esc(r.target)}</td>
        <td class="num">${num(r.capacity_mtpa, 1)}</td><td class="num">${num(r.ev_cr)}</td><td class="num">${num(r.ev_per_tonne_inr)}</td>
        <td class="num">${num(r.ev_per_tonne_usd)}</td><td>${esc(r.note)}</td></tr>`);
    rows.push(`<tr class="this-deal"><td>${M.transaction.announcement_date}</td><td>Adani Group</td><td>Ambuja + ACC (this deal)</td>
        <td class="num">${num(M.valuation.capacity_mtpa, 1)}</td><td class="num">${num(M.valuation.enterprise_value)}</td>
        <td class="num">${num(M.valuation.ev_per_tonne_inr)}</td><td class="num">${num(M.valuation.ev_per_tonne_usd)}</td><td></td></tr>`);
    rows.push(`<tr class="total"><td colspan="6">Median, excluding distressed (${p.count_ex_distressed} deals)</td>
        <td class="num">${num(p.median_usd_per_t_ex_distressed)}</td><td></td></tr>`);
    rows.push(`<tr><td colspan="6">Median / mean, all ${p.count} precedents</td>
        <td class="num">${num(p.median_usd_per_t)} / ${num(p.mean_usd_per_t)}</td><td></td></tr>`);
    $('precedentTable').innerHTML = rows.join('');
    $('precedentNote').textContent = M.narrative.precedent_line +
        ' Most precedents were asset or unlisted-company deals, so control premiums are not comparable and are not shown; ' +
        'EV/EBITDA was not reliably disclosed. Sources are listed on the Assumptions & Sources tab.';
}

// ---------------------------------------------------------------- PPA
function renderPpa(M) {
    const a = M.ppa.ambuja, c = M.ppa.acc;
    const names = { ppe: 'PP&E', mineral_rights: 'Mineral rights', brand: 'Brands (not amortised)', customer_relationships: 'Customer relationships',
                    favourable_contracts: 'Favourable contracts', inventory: 'Inventory (released Year 1)' };
    const label = k => names[k] || k.replace(/_/g, ' ');
    const rows = [
        [`Book equity, ${M.transaction.balance_sheet_date}`, num(a.book_equity), num(c.book_equity)],
        ['Less: investments eliminated (ACC stake)', num(-a.investment_eliminated), num(-c.investment_eliminated)],
        ...Object.keys(a.step_ups).map(k => [`Step-up: ${label(k)}`, num(a.step_ups[k]), num(c.step_ups[k])]),
        ['Deferred tax on step-ups', num(-a.deferred_tax_liability), num(-c.deferred_tax_liability)],
        { cells: ['FV of identifiable net assets', num(a.fv_net_identifiable_assets), num(c.fv_net_identifiable_assets)], total: true },
        ['Annual amortisation of step-ups', num(a.annual_amortisation), num(c.annual_amortisation)],
    ];
    $('ppaTable').innerHTML = rowsHtml(rows);
}

function renderGoodwill(M) {
    const g = M.goodwill, o = M.ownership;
    $('goodwillTable').innerHTML = rowsHtml([
        ['Consideration attributable (look-through)', num(g.consideration_ambuja_ex_acc), num(g.consideration_acc_lookthrough)],
        ['Adani economic interest', pct(o.adani_in_ambuja * 100, 2), pct(o.adani_lookthrough_in_acc * 100, 2)],
        ['Less: Adani share of FV net assets', num(-g.adani_share_fv_ambuja), num(-g.adani_share_fv_acc)],
        { cells: ['Goodwill', num(g.ambuja_goodwill), num(g.acc_goodwill)], total: true },
        null,
        { cells: ['Total goodwill', num(g.total_goodwill), pct(g.goodwill_pct_of_consideration, 1) + ' of consideration'], highlight: true },
        ['ACC value embedded in Ambuja shares bought', num(g.acc_value_in_ambuja_purchase), ''],
    ]);
}

// ---------------------------------------------------------------- pro forma
function renderIncomeStatement(M) {
    const y = years(M), pf = M.pro_forma;
    const line = (label, key, opts = {}) => ({ cells: [label, ...pf.map(r => num(opts.neg ? -r[key] : r[key]))], total: opts.total });
    const sum = (label, k1, k2) => [label, ...pf.map(r => num(r[k1] + r[k2]))];
    $('proformaIS').innerHTML = headHtml('₹ Cr', y) + '<tbody>' + rowsHtml([
        line('Revenue (Ambuja + ACC)', 'combined_revenue'),
        sum('Standalone EBITDA', 'ambuja_ebitda', 'acc_ebitda'),
        line('Synergies', 'synergies'),
        line('Costs to achieve (one-off)', 'costs_to_achieve', { neg: true }),
        line('EBITDA', 'ebitda', { total: true }),
        line('Standalone D&A', 'standalone_da', { neg: true }),
        line('PPA amortisation (incl. inventory in Year 1)', 'ppa_amortisation', { neg: true }),
        line('Treasury income', 'treasury_income'),
        line('Target interest expense', 'target_interest', { neg: true }),
        line('Holdco acquisition interest', 'holdco_interest', { neg: true }),
        line('Profit before tax', 'pbt', { total: true }),
        line('Tax', 'tax', { neg: true }),
        line('Consolidated net income', 'consolidated_net_income', { total: true }),
        line('Non-controlling interests', 'nci_net_income', { neg: true }),
        { cells: ['Adani-attributable net income', ...pf.map(r => ({ v: num(r.attributable_net_income), cls: signClass(r.attributable_net_income) }))], total: true },
    ]) + '</tbody>';
}

function renderBalanceSheet(M) {
    const b = M.balance_sheet, A = b.assets, L = b.liabilities, E = b.equity;
    $('proformaBS').innerHTML = rowsHtml([
        ['Fixed assets & CWIP (incl. step-up)', num(A.fixed_assets_and_cwip)],
        ['Acquired intangibles', num(A.acquired_intangibles)],
        ['Goodwill', num(A.goodwill)],
        ['Inventories, receivables & other', num(A.inventories + A.trade_receivables + A.other_assets + A.investments)],
        ['Cash (at Ambuja/ACC)', num(A.cash)],
        { cells: ['Total assets', num(b.total_assets)], total: true },
        null,
        ['Acquisition debt (holdco)', num(L.acquisition_debt)],
        ['Target borrowings & leases', num(L.target_borrowings_and_leases)],
        ['Deferred tax on step-ups', num(L.deferred_tax_on_step_ups)],
        ['Other liabilities', num(L.other_liabilities)],
        ['Adani equity (after expensed costs)', num(E.adani_equity)],
        ['Non-controlling interests', num(E.non_controlling_interests)],
        { cells: ['Total liabilities & equity', num(b.total_liabilities_and_equity)], total: true },
        ['Check: assets − (liabilities + equity)', num(b.total_assets - b.total_liabilities_and_equity)],
    ]);
}

function renderCredit(M) {
    const c = M.balance_sheet.credit_at_close, cy = M.balance_sheet.credit_by_year;
    $('creditTable').innerHTML = headHtml('', ['At close', ...years(M)]) + '<tbody>' + rowsHtml([
        ['Consolidated gross debt (₹ Cr)', num(c.gross_debt), ...cy.map(r => num(r.gross_debt))],
        ['Net debt / EBITDA', mult(c.net_debt_to_ebitda), ...cy.map(r => mult(r.net_debt_to_ebitda))],
        ['EBITDA / total interest', '', ...cy.map(r => mult(r.ebitda_interest_cover))],
        ['Holdco loan-to-value at cost', pct(c.holdco_ltv_at_cost_pct, 0), '', '', ''],
        ['Holdco LTV at completion-day prices', pct(c.holdco_ltv_at_completion_market_pct, 0), '', '', ''],
    ]) + '</tbody>';
}

// ---------------------------------------------------------------- synergies
function renderSynergyTable(M) {
    const s = M.synergies;
    const items = Object.values(s.items).map(it => [esc(it.label), num(it.run_rate), ...it.by_year.map(x => num(x))]);
    $('synergyTable').innerHTML = headHtml('₹ Cr', ['Run-rate', ...years(M)]) + '<tbody>' + rowsHtml([
        ...items,
        { cells: ['Total pre-tax synergies', num(s.run_rate), ...s.pretax_by_year.map(x => num(x))], total: true },
        ['Costs to achieve (one-off)', num(-s.costs_to_achieve_total), ...s.costs_to_achieve_by_year.map(x => num(-x))],
    ]) + '</tbody>';
}

function renderNpv(M) {
    const s = M.synergies;
    $('npvSubtitle').textContent = `After tax, discounted at the ${pct(s.discount_rate_pct, 2)} unlevered cost of capital; ` +
        `terminal growth ${pct(s.terminal_growth_pct)}; terminal value is ${pct(s.terminal_value_share_pct, 0)} of gross NPV.`;
    const bars = [
        ...years(M).map((y, i) => [`PV ${y}`, s.pv_by_year[i], 'positive']),
        ['PV terminal', s.pv_terminal, 'positive'],
        ['PV costs to achieve', s.pv_costs_to_achieve_after_tax, 'negative'],
        ['Net NPV', s.net_npv, 'total'],
    ];
    const max = Math.max(...bars.map(b => b[1]));
    $('npvWaterfall').innerHTML = bars.map(b => `<div class="npv-bar-group">
        <div class="npv-bar-value">${b[2] === 'negative' ? '−' : ''}₹${num(b[1])}</div>
        <div class="npv-bar ${b[2]}" style="height:${Math.max(6, b[1] / max * 180)}px"></div>
        <div class="npv-bar-label">${b[0]}</div></div>`).join('');
}

// ---------------------------------------------------------------- returns
function badge(ok, yes, no) {
    return { v: `<span class="eps-bridge-badge ${ok ? 'accretive' : 'dilutive'}">${ok ? yes : no}</span>` };
}

function renderReturns(M) {
    const r = M.returns;
    $('returnsTable').innerHTML = headHtml('', years(M)) + '<tbody>' + rowsHtml([
        ['Adani-attributable net income (₹ Cr)', ...r.map(x => ({ v: num(x.attributable_net_income), cls: signClass(x.attributable_net_income) }))],
        ['Sponsor equity invested, opening (₹ Cr)', ...r.map(x => num(x.sponsor_equity_invested))],
        { cells: ['Return on sponsor equity', ...r.map(x => pct(x.roe_pct))], total: true },
        ['Levered cost of equity', ...r.map(x => pct(x.levered_cost_of_equity_pct))],
        ['', ...r.map(x => badge(x.earns_cost_of_equity, 'Above Ke', 'Below Ke'))],
        null,
        ['Cash earnings before acquisition financing (₹ Cr)', ...r.map(x => num(x.cash_earnings_pre_financing))],
        { cells: ['Cash ROIC on total investment', ...r.map(x => pct(x.cash_roic_pct, 2))], total: true },
        ['Cash ROIC excluding synergies', ...r.map(x => pct(x.cash_roic_ex_synergies_pct, 2))],
        ['Unlevered cost of capital', ...r.map(x => pct(x.unlevered_cost_of_capital_pct, 2))],
        ['', ...r.map(x => badge(x.earns_cost_of_capital, 'Above cost of capital', 'Below cost of capital'))],
        ['In-year synergies needed for ROIC = cost of capital (₹ Cr)', ...r.map(x => num(x.breakeven_synergies_for_roic))],
    ]) + '</tbody>';
}

function renderValueTable(M) {
    const v = M.value_creation;
    $('valueTable').innerHTML = rowsHtml([
        ['Net synergy NPV (100%)', num(M.synergies.net_npv)],
        ['Adani share of synergies (look-through, EBITDA-weighted)', pct(v.adani_share_of_synergies_pct)],
        ['Adani share of net synergy NPV', num(v.adani_share_of_net_synergy_npv)],
        ['Less: premium paid over undisturbed prices', num(-v.premium_paid)],
        ['Less: transaction costs', num(-v.transaction_costs)],
        { cells: ['Net value created for Adani', { v: num(v.net_value_created), cls: signClass(v.net_value_created) }], total: true },
    ]);
}

function renderHoldco(M) {
    const pf = M.pro_forma;
    $('holdcoTable').innerHTML = headHtml('', years(M)) + '<tbody>' + rowsHtml([
        ['Dividends received (net of WHT)', ...pf.map(r => num(r.dividends_received_net))],
        ['Holdco interest (after any shield)', ...pf.map(r => num(-r.holdco_interest_after_shield))],
        { cells: ['Holdco cash flow', ...pf.map(r => ({ v: num(r.holdco_cash_flow), cls: signClass(r.holdco_cash_flow) }))], total: true },
        ['Dividend / interest cover', ...pf.map(r => mult(r.dividend_interest_cover, 2))],
        ['Sponsor top-up required', ...pf.map(r => num(r.sponsor_top_up))],
        ['Holdco debt, closing', ...pf.map(r => num(r.holdco_debt_close))],
    ]) + '</tbody>';
}

function renderBreakeven(M) {
    const v = M.value_creation, h = M.headline, last = M.returns[M.returns.length - 1];
    const finalSyn = M.synergies.pretax_by_year[M.synergies.pretax_by_year.length - 1];
    const bar = (label, val, cls, max) => `<div class="breakeven-bar-container">
        <div class="breakeven-bar-label"><span>${label}</span><span class="mono">${cr(val)}</span></div>
        <div class="breakeven-bar-track"><div class="breakeven-bar-fill ${cls}" style="width:${Math.min(100, val / max * 100)}%"></div></div></div>`;
    const max1 = Math.max(v.breakeven_run_rate_synergies, h.synergy_run_rate) * 1.1;
    const max2 = Math.max(last.breakeven_synergies_for_roic, finalSyn) * 1.1;
    $('breakevenVisual').innerHTML =
        `<h4 class="sub-head">Value test: run-rate synergies needed to cover premium + costs</h4>` +
        bar('Breakeven run-rate synergies', v.breakeven_run_rate_synergies, 'breakeven', max1) +
        bar('Modelled run-rate synergies', h.synergy_run_rate, 'actual', max1) +
        `<p class="${signClass(h.synergy_run_rate - v.breakeven_run_rate_synergies)}">Cushion: ${cr(h.synergy_run_rate - v.breakeven_run_rate_synergies)}</p>` +
        `<h4 class="sub-head">Earnings test: ${h.final_year} synergies needed for cash ROIC = cost of capital</h4>` +
        bar('Breakeven in-year synergies', last.breakeven_synergies_for_roic, 'breakeven', max2) +
        bar(`Modelled ${h.final_year} synergies`, finalSyn, 'actual', max2) +
        `<p class="${signClass(finalSyn - last.breakeven_synergies_for_roic)}">Gap: ${cr(finalSyn - last.breakeven_synergies_for_roic)}</p>`;
}

// ---------------------------------------------------------------- sensitivity
function renderMatrices(M) {
    const s = M.sensitivity, lv = s.synergy_levels, base = Math.round(M.synergies.run_rate);
    const build = (rows, fmt, cls) => {
        let html = `<table><thead><tr><th>Price \\ Synergies</th>${lv.map(x => `<th>₹${num(x)}</th>`).join('')}</tr></thead><tbody>`;
        rows.forEach(r => {
            const isBase = Math.abs(r.price_multiplier - 1) < 1e-9;
            html += `<tr class="${isBase ? 'base-row' : ''}"><td class="header-cell">${pct((r.price_multiplier - 1) * 100, 0)}</td>`;
            lv.forEach(x => {
                const val = r[String(x)];
                const mark = isBase && x === base ? ' base-cell' : '';
                html += `<td class="${cls(val)}${mark}">${fmt(val)}</td>`;
            });
            html += '</tr>';
        });
        return html + '</tbody></table>';
    };
    $('valueMatrix').innerHTML = build(s.matrix_net_value_created, x => num(x), x => (x >= 0 ? 'positive' : 'negative'));
    $('roicMatrixTitle').textContent = `Cash ROIC ${s.final_year} vs ${pct(M.headline.unlevered_cost_of_capital_pct, 2)} cost of capital: Offer Price × Run-Rate Synergies`;
    $('roicMatrix').innerHTML = build(s.matrix_cash_roic_final_year, x => pct(x),
        x => (x >= M.headline.unlevered_cost_of_capital_pct ? 'positive' : 'negative'));
}

function renderRateTable(M) {
    const s = M.sensitivity, base = M.inputs.acq_debt.refi_rate_pct;
    $('rateTitle').textContent = `Holdco Refinancing Rate (${s.final_year})`;
    $('rateTable').innerHTML = headHtml('Refi rate', ['Interest (₹ Cr)', 'Attributable NI', 'ROE', 'Div / interest']) + '<tbody>' +
        s.refi_rate.map(r => `<tr class="${Math.abs(r.refi_rate_pct - base) < 1e-9 ? 'highlight' : ''}"><td>${pct(r.refi_rate_pct, 2)}</td>
        <td class="num">${num(r.holdco_interest_final_year)}</td><td class="num">${num(r.attributable_ni_final_year)}</td>
        <td class="num">${pct(r.roe_final_year_pct)}</td><td class="num">${mult(r.dividend_interest_cover_final_year, 2)}</td></tr>`).join('') + '</tbody>';
}

function renderMarginTable(M) {
    const s = M.sensitivity;
    $('marginTitle').textContent = `EBITDA Margin, Both Companies, All Years (${s.final_year})`;
    $('marginTable').innerHTML = headHtml('Change (bp)', ['Cash ROIC', 'ROE']) + '<tbody>' +
        s.ebitda_margin.map(r => `<tr class="${r.margin_change_bp === 0 ? 'highlight' : ''}"><td>${r.margin_change_bp > 0 ? '+' : r.margin_change_bp < 0 ? '−' : ''}${Math.abs(r.margin_change_bp)}</td>
        <td class="num">${pct(r.cash_roic_final_year_pct, 2)}</td><td class="num">${pct(r.roe_final_year_pct)}</td></tr>`).join('') + '</tbody>';
}

function renderShieldTable(M) {
    const s = M.sensitivity, base = M.inputs.acq_debt.interest_tax_deductible;
    $('shieldTable').innerHTML = headHtml('Holdco interest tax-deductible?', [`Attributable NI ${s.final_year}`, 'ROE', 'Levered Ke']) + '<tbody>' +
        s.interest_tax_shield.map(r => `<tr class="${r.interest_tax_deductible === base ? 'highlight' : ''}">
        <td>${r.interest_tax_deductible ? 'Yes (e.g. debt pushed down into an Indian entity)' : 'No (base case: offshore SPV, no taxable income)'}</td>
        <td class="num">${num(r.attributable_ni_final_year)}</td><td class="num">${pct(r.roe_final_year_pct)}</td>
        <td class="num">${pct(r.levered_cost_of_equity_pct)}</td></tr>`).join('') + '</tbody>';
}

// ---------------------------------------------------------------- assumptions
function renderAssumptions(M) {
    const i = M.inputs, p = i.projection, d = i.acq_debt, c = i.cost_of_capital, y = years(M);
    const list = a => a.map(x => pct(x)).join(' / ');
    $('assumptionTable').innerHTML = rowsHtml([
        [`Revenue growth ${y[0]}–${y[y.length - 1]} (Ambuja / ACC same)`, list(p.ambuja_revenue_growth_pct)],
        ['EBITDA margin — Ambuja', list(p.ambuja_ebitda_margin_pct)],
        ['EBITDA margin — ACC', list(p.acc_ebitda_margin_pct)],
        ['Tax rate', pct(p.tax_rate_pct, 2)],
        ['Dividend payout', pct(p.dividend_payout_pct, 0)],
        ['Holdco debt: term / bridge / refinanced rate', `${pct(d.term_rate_pct, 2)} / ${pct(d.bridge_rate_pct, 2)} / ${pct(d.refi_rate_pct, 2)}`],
        ['Holdco interest tax-deductible', d.interest_tax_deductible ? 'Yes' : 'No'],
        ['Dividend withholding tax: Ambuja / ACC', `${pct(i.holdco.wht_on_ambuja_dividends_pct, 0)} / ${pct(i.holdco.wht_on_acc_dividends_pct, 0)}`],
        ['Risk-free / ERP / asset beta', `${pct(c.risk_free_pct, 2)} / ${pct(c.equity_risk_premium_pct, 1)} / ${c.asset_beta.toFixed(2)}`],
        ['Synergy terminal growth', pct(c.synergy_terminal_growth_pct)],
        ['Transaction costs', `${pct(i.deal_costs.transaction_costs_pct_of_consideration)} of consideration`],
        ['Treasury yield on cash (derived from CY2021)', pct(M.projections.treasury_yield_pct, 2)],
    ]);
}

function renderHistory(M) {
    const a = M.historicals.ambuja, c = M.historicals.acc, ab = M.historicals.ambuja_bs, cb = M.historicals.acc_bs;
    const L = arr => arr[arr.length - 1];
    $('histTable').innerHTML = rowsHtml([
        ['Revenue', num(L(a.revenue)), num(L(c.revenue))],
        ['EBITDA', num(L(a.ebitda)), num(L(c.ebitda))],
        ['EBITDA margin', pct(L(a.ebitda) / L(a.revenue) * 100), pct(L(c.ebitda) / L(c.revenue) * 100)],
        ['Net income', num(L(a.net_income)), num(L(c.net_income))],
        [`Cash, ${M.transaction.balance_sheet_date}`, num(ab.cash), num(cb.cash)],
        [`Borrowings incl. leases, ${M.transaction.balance_sheet_date}`, num(ab.borrowings), num(cb.borrowings)],
        [`Book equity, ${M.transaction.balance_sheet_date}`, num(ab.share_capital + ab.reserves), num(cb.share_capital + cb.reserves)],
    ]);
}

function renderSources(M) {
    $('sourceList').innerHTML = Object.values(M.sources).map(s => {
        const m = s.match(/https?:\/\/\S+/);
        const text = esc(s.replace(/ — https?:\/\/\S+.*$/, '').replace(/https?:\/\/\S+/, ''));
        return `<li>${text}${m ? ` — <a href="${esc(m[0])}" target="_blank" rel="noopener">link</a>` : ''}</li>`;
    }).join('');
}
