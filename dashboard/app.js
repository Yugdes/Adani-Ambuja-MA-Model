/**
 * M&A Model Dashboard — Interactive Logic
 * Adani Group × Ambuja Cements & ACC Ltd
 * Renders all dynamic charts, tables, and interactive elements
 */

// ==========================================================================
// MODEL DATA (mirrors Python model output)
// ==========================================================================

const MODEL = {
    proForma: {
        FY2023E: {
            ambuja_revenue: 16530, acc_revenue: 18315, combined_revenue: 34845,
            ambuja_ebitda: 3441, acc_ebitda: 2823, synergy_ebitda_impact: 734,
            combined_ebitda: 6998, combined_ebitda_margin_pct: 20.1,
            combined_da: 2678, ppa_amortization: 1143,
            combined_ebit: 4320,
            combined_interest_income: 315, combined_interest_expense: 2635,
            incremental_interest: 2494, combined_other_income: 660,
            combined_pbt: 2660, combined_tax: 669,
            combined_net_income: 1991, combined_eps: 10.02,
        },
        FY2024E: {
            ambuja_revenue: 18183, acc_revenue: 20147, combined_revenue: 38330,
            ambuja_ebitda: 3957, acc_ebitda: 3395, synergy_ebitda_impact: 1911,
            combined_ebitda: 9263, combined_ebitda_margin_pct: 24.2,
            combined_da: 2786, ppa_amortization: 1143,
            combined_ebit: 6477,
            combined_interest_income: 330, combined_interest_expense: 1464,
            incremental_interest: 1331, combined_other_income: 695,
            combined_pbt: 6038, combined_tax: 1519,
            combined_net_income: 4519, combined_eps: 22.74,
        },
        FY2025E: {
            ambuja_revenue: 19819, acc_revenue: 21960, combined_revenue: 41779,
            ambuja_ebitda: 4477, acc_ebitda: 3921, synergy_ebitda_impact: 3100,
            combined_ebitda: 11498, combined_ebitda_margin_pct: 27.5,
            combined_da: 2890, ppa_amortization: 1143,
            combined_ebit: 8608,
            combined_interest_income: 345, combined_interest_expense: 1277,
            incremental_interest: 1159, combined_other_income: 730,
            combined_pbt: 8406, combined_tax: 2116,
            combined_net_income: 6290, combined_eps: 31.66,
        }
    },
    balanceSheet: {
        assets: {
            ppe: 24322, intangible_assets: 17170, goodwill: 28426,
            cash: 5660, other_assets: 12131, total_assets: 87709
        },
        liabilities: {
            total_equity: 47578, total_debt: 27445,
            other_liabilities: 14606, total_le: 89629
        },
        credit: {
            gross_debt: 27445, net_debt: 21785,
            combined_ebitda: 5352,
            gross_debt_to_ebitda: 5.1, net_debt_to_ebitda: 4.1,
            interest_coverage: 2.1
        }
    },
    accretionDilution: {
        FY2023E: {
            standalone_eps: 12.35, pf_eps_with_syn: 10.02, pf_eps_without_syn: 7.25,
            ad_with_syn_pct: -18.9, ad_without_syn_pct: -41.3,
            is_accretive_with: false, synergy_contribution: 2.77
        },
        FY2024E: {
            standalone_eps: 14.25, pf_eps_with_syn: 22.74, pf_eps_without_syn: 15.55,
            ad_with_syn_pct: 59.6, ad_without_syn_pct: 9.1,
            is_accretive_with: true, synergy_contribution: 7.19
        },
        FY2025E: {
            standalone_eps: 16.17, pf_eps_with_syn: 31.66, pf_eps_without_syn: 20.00,
            ad_with_syn_pct: 95.8, ad_without_syn_pct: 23.7,
            is_accretive_with: true, synergy_contribution: 11.66
        }
    },
    breakeven: {
        breakeven_synergy: 1240,
        actual_year1_synergy: 734,
        synergy_cushion: -506
    },
    npv: {
        pv_year1: 470, pv_year2: 1139, pv_year3: 1695,
        pv_terminal: 21830, total_npv: 25134,
        costs_to_achieve: 2800, npv_net: 22334
    },
    sensitivity: {
        premium: [
            { prem: 0, eps: 23.89, ad: 67.7 },
            { prem: 5, eps: 23.24, ad: 63.1 },
            { prem: 10, eps: 22.58, ad: 58.5 },
            { prem: 13.2, eps: 22.12, ad: 55.2 },
            { prem: 15, eps: 21.93, ad: 53.9 },
            { prem: 20, eps: 21.28, ad: 49.3 },
            { prem: 25, eps: 20.62, ad: 44.7 },
            { prem: 30, eps: 19.97, ad: 40.1 }
        ],
        debt: [
            { rate: 7.0, interest: 1155, eps: 23.26, ad: 63.2 },
            { rate: 7.5, interest: 1238, eps: 23.07, ad: 61.9 },
            { rate: 8.0, interest: 1320, eps: 22.88, ad: 60.6 },
            { rate: 8.5, interest: 1403, eps: 22.69, ad: 59.2 },
            { rate: 8.75, interest: 1444, eps: 22.60, ad: 58.6 },
            { rate: 9.0, interest: 1485, eps: 22.50, ad: 57.9 },
            { rate: 9.5, interest: 1568, eps: 22.31, ad: 56.6 },
            { rate: 10.0, interest: 1650, eps: 22.12, ad: 55.2 },
            { rate: 10.5, interest: 1733, eps: 21.93, ad: 53.9 }
        ],
        matrix: [
            { prem: 5, values: [38.2, 45.5, 52.8, 58.8, 63.1, 66.0, 70.3] },
            { prem: 10, values: [33.6, 40.9, 48.2, 54.2, 58.5, 61.4, 65.7] },
            { prem: 13.2, values: [30.7, 38.0, 45.3, 51.3, 55.2, 58.4, 62.7] },
            { prem: 15, values: [29.0, 36.3, 43.6, 49.6, 53.9, 56.8, 61.1] },
            { prem: 20, values: [24.4, 31.7, 39.0, 45.0, 49.3, 52.2, 56.5] },
            { prem: 25, values: [19.8, 27.1, 34.4, 40.4, 44.7, 47.6, 51.9] }
        ],
        synRange: [1000, 1500, 2000, 2600, 3100, 3500, 4000]
    },
    precedents: [
        { date: "Sep 2022", acquirer: "Adani Group", target: "Ambuja + ACC", ev_ebitda: 14.3, ev_tonne: 160, premium: 13.2, deal_value: 81361, thisDeal: true },
        { date: "May 2020", acquirer: "UltraTech", target: "Century Cement", ev_ebitda: 12.8, ev_tonne: 142, premium: 18.5, deal_value: 5700, thisDeal: false },
        { date: "Jan 2019", acquirer: "UltraTech", target: "Nathdwara Cement", ev_ebitda: 11.5, ev_tonne: 115, premium: 15.2, deal_value: 7266, thisDeal: false },
        { date: "Jun 2018", acquirer: "Nirma (Nuvoco)", target: "Emami Cement", ev_ebitda: 16.2, ev_tonne: 130, premium: 22.0, deal_value: 5500, thisDeal: false },
        { date: "Dec 2016", acquirer: "UltraTech", target: "Jaypee Cement", ev_ebitda: 10.8, ev_tonne: 85, premium: 0, deal_value: 16189, thisDeal: false },
        { date: "Mar 2015", acquirer: "LafargeHolcim", target: "Lafarge India", ev_ebitda: 13.5, ev_tonne: 135, premium: 16.8, deal_value: 9400, thisDeal: false },
        { date: "Sep 2013", acquirer: "UltraTech", target: "Jaypee Corp", ev_ebitda: 9.2, ev_tonne: 78, premium: 12.0, deal_value: 3800, thisDeal: false },
        { date: "Jul 2021", acquirer: "JSW Cement", target: "JSW-Bela Plant", ev_ebitda: 11.0, ev_tonne: 98, premium: 10.5, deal_value: 2700, thisDeal: false }
    ]
};

// ==========================================================================
// TAB NAVIGATION
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    renderProFormaIS();
    renderProFormaBS();
    renderCreditMetrics();
    renderAccretionDilution();
    renderBreakeven();
    renderNPVWaterfall();
    renderSensitivityMatrix();
    renderPremiumSensitivity();
    renderDebtSensitivity();
    renderPrecedentTable();
    renderPrecedentCharts();
    renderEPSBridge();
});

function initNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const target = document.getElementById(`tab-${tab.dataset.tab}`);
            if (target) target.classList.add('active');
        });
    });
}

// ==========================================================================
// FORMATTERS
// ==========================================================================

function fmt(num) {
    if (num === null || num === undefined) return '—';
    return Math.round(num).toLocaleString('en-IN');
}

function fmtDec(num, d = 2) {
    if (num === null || num === undefined) return '—';
    return num.toFixed(d);
}

// ==========================================================================
// PRO FORMA INCOME STATEMENT
// ==========================================================================

function renderProFormaIS() {
    const tbody = document.querySelector('#proformaIS tbody');
    if (!tbody) return;
    const pf = MODEL.proForma;
    const periods = ['FY2023E', 'FY2024E', 'FY2025E'];

    const rows = [
        { label: 'Ambuja Revenue', key: 'ambuja_revenue' },
        { label: 'ACC Revenue', key: 'acc_revenue' },
        { label: 'Combined Revenue', key: 'combined_revenue', total: true },
        { label: '', spacer: true },
        { label: 'Ambuja EBITDA', key: 'ambuja_ebitda' },
        { label: 'ACC EBITDA', key: 'acc_ebitda' },
        { label: 'Synergy Contribution', key: 'synergy_ebitda_impact', accent: true },
        { label: 'Combined EBITDA', key: 'combined_ebitda', total: true },
        { label: '  EBITDA Margin (%)', key: 'combined_ebitda_margin_pct', pct: true },
        { label: '', spacer: true },
        { label: 'Combined D&A', key: 'combined_da', neg: true },
        { label: '  of which PPA Amortization', key: 'ppa_amortization', sub: true },
        { label: 'Combined EBIT', key: 'combined_ebit', total: true },
        { label: '', spacer: true },
        { label: 'Interest Income', key: 'combined_interest_income' },
        { label: 'Interest Expense', key: 'combined_interest_expense', neg: true },
        { label: '  Incremental (Acq. Debt)', key: 'incremental_interest', sub: true },
        { label: 'Other Income', key: 'combined_other_income' },
        { label: '', spacer: true },
        { label: 'Combined PBT', key: 'combined_pbt', total: true },
        { label: 'Tax (25.17%)', key: 'combined_tax', neg: true },
        { label: 'Combined Net Income', key: 'combined_net_income', total: true },
        { label: '', spacer: true },
        { label: 'Pro Forma EPS (₹)', key: 'combined_eps', total: true, eps: true },
    ];

    rows.forEach(row => {
        if (row.spacer) {
            tbody.innerHTML += '<tr><td colspan="4" style="height:8px"></td></tr>';
            return;
        }

        let tr = document.createElement('tr');
        if (row.total) tr.classList.add('total');
        if (row.accent) tr.style.color = 'var(--accent-cyan)';

        let labelTd = document.createElement('td');
        labelTd.textContent = row.label;
        if (row.sub) labelTd.style.color = 'var(--text-muted)';
        tr.appendChild(labelTd);

        periods.forEach(p => {
            let td = document.createElement('td');
            td.classList.add('num');
            const val = pf[p][row.key];
            if (row.pct) {
                td.textContent = `${fmtDec(val, 1)}%`;
            } else if (row.eps) {
                td.textContent = `₹${fmtDec(val)}`;
            } else {
                td.textContent = fmt(val);
                if (row.neg && val > 0) td.textContent = `(${fmt(val)})`;
            }
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}

// ==========================================================================
// PRO FORMA BALANCE SHEET
// ==========================================================================

function renderProFormaBS() {
    const tbody = document.querySelector('#proformaBS tbody');
    if (!tbody) return;
    const bs = MODEL.balanceSheet;

    const items = [
        { label: 'ASSETS', section: true },
        { label: '  PP&E', val: bs.assets.ppe },
        { label: '  Intangible Assets (PPA)', val: bs.assets.intangible_assets },
        { label: '  Goodwill', val: bs.assets.goodwill },
        { label: '  Cash & Equivalents', val: bs.assets.cash },
        { label: '  Other Assets', val: bs.assets.other_assets },
        { label: 'Total Assets', val: bs.assets.total_assets, total: true },
        { spacer: true },
        { label: 'LIABILITIES & EQUITY', section: true },
        { label: '  Total Equity', val: bs.liabilities.total_equity },
        { label: '  Total Debt', val: bs.liabilities.total_debt },
        { label: '  Other Liabilities', val: bs.liabilities.other_liabilities },
        { label: 'Total L&E', val: bs.liabilities.total_le, total: true },
    ];

    items.forEach(item => {
        if (item.spacer) {
            tbody.innerHTML += '<tr><td colspan="2" style="height:8px"></td></tr>';
            return;
        }
        let tr = document.createElement('tr');
        if (item.total) tr.classList.add('total');

        let td1 = document.createElement('td');
        td1.textContent = item.label;
        if (item.section) { td1.style.fontWeight = '700'; td1.style.color = 'var(--accent-secondary)'; }
        tr.appendChild(td1);

        let td2 = document.createElement('td');
        td2.classList.add('num');
        if (item.val !== undefined) td2.textContent = fmt(item.val);
        tr.appendChild(td2);

        tbody.appendChild(tr);
    });
}

// ==========================================================================
// CREDIT METRICS
// ==========================================================================

function renderCreditMetrics() {
    const container = document.getElementById('creditMetrics');
    if (!container) return;
    const cm = MODEL.balanceSheet.credit;

    const metrics = [
        { label: 'Gross Debt / EBITDA', value: `${cm.gross_debt_to_ebitda}x`, pct: cm.gross_debt_to_ebitda / 8 * 100, color: cm.gross_debt_to_ebitda > 4 ? 'var(--negative)' : 'var(--positive)' },
        { label: 'Net Debt / EBITDA', value: `${cm.net_debt_to_ebitda}x`, pct: cm.net_debt_to_ebitda / 8 * 100, color: cm.net_debt_to_ebitda > 3.5 ? '#f59e0b' : 'var(--positive)' },
        { label: 'Interest Coverage', value: `${cm.interest_coverage}x`, pct: cm.interest_coverage / 5 * 100, color: cm.interest_coverage < 2.5 ? '#f59e0b' : 'var(--positive)' },
    ];

    metrics.forEach(m => {
        container.innerHTML += `
            <div class="credit-metric">
                <div class="credit-metric-header">
                    <span class="credit-metric-label">${m.label}</span>
                    <span class="credit-metric-value" style="color:${m.color}">${m.value}</span>
                </div>
                <div class="credit-bar">
                    <div class="credit-bar-fill" style="width:${Math.min(m.pct, 100)}%;background:${m.color}"></div>
                </div>
            </div>
        `;
    });
}

// ==========================================================================
// ACCRETION / DILUTION TABLE
// ==========================================================================

function renderAccretionDilution() {
    const tbody = document.getElementById('adTable');
    if (!tbody) return;
    const ad = MODEL.accretionDilution;
    const periods = ['FY2023E', 'FY2024E', 'FY2025E'];

    const rows = [
        { label: 'Standalone EPS (Ambuja)', key: 'standalone_eps', eps: true },
        { spacer: true },
        { label: 'PF EPS (with Synergies)', key: 'pf_eps_with_syn', eps: true, total: true },
        { label: '  Accretion/(Dilution) %', key: 'ad_with_syn_pct', adBadge: true },
        { spacer: true },
        { label: 'PF EPS (without Synergies)', key: 'pf_eps_without_syn', eps: true },
        { label: '  Accretion/(Dilution) %', key: 'ad_without_syn_pct', adBadge: true },
        { spacer: true },
        { label: 'Synergy Contribution (₹/share)', key: 'synergy_contribution', eps: true },
    ];

    rows.forEach(row => {
        if (row.spacer) {
            tbody.innerHTML += '<tr><td colspan="4" style="height:6px"></td></tr>';
            return;
        }

        let tr = document.createElement('tr');
        if (row.total) tr.classList.add('total');

        let td = document.createElement('td');
        td.textContent = row.label;
        tr.appendChild(td);

        periods.forEach(p => {
            let td = document.createElement('td');
            td.classList.add('num');
            const val = ad[p][row.key];

            if (row.adBadge) {
                const cls = val > 0 ? 'accretive' : 'dilutive';
                td.innerHTML = `<span class="eps-bridge-badge ${cls}">${val > 0 ? '+' : ''}${fmtDec(val, 1)}%</span>`;
            } else if (row.eps) {
                td.textContent = `₹${fmtDec(val)}`;
            } else {
                td.textContent = fmt(val);
            }
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}

// ==========================================================================
// EPS BRIDGE CHART
// ==========================================================================

function renderEPSBridge() {
    const container = document.getElementById('epsBridge');
    if (!container) return;
    const ad = MODEL.accretionDilution;
    const periods = ['FY2023E', 'FY2024E', 'FY2025E'];

    const maxEps = 35;

    periods.forEach(p => {
        const d = ad[p];
        const standaloneW = (d.standalone_eps / maxEps * 100);
        const withSynW = (d.pf_eps_with_syn / maxEps * 100);
        const adVal = d.ad_with_syn_pct;
        const cls = adVal > 0 ? 'accretive' : 'dilutive';

        container.innerHTML += `
            <div style="margin-bottom:1.5rem">
                <div style="font-weight:600;margin-bottom:0.5rem;color:var(--text-secondary)">${p}</div>
                <div class="eps-bridge-row">
                    <span class="eps-bridge-label">Standalone EPS</span>
                    <div class="eps-bridge-bar-container">
                        <div class="eps-bridge-bar standalone" style="width:${standaloneW}%"></div>
                    </div>
                    <span class="eps-bridge-value">₹${fmtDec(d.standalone_eps)}</span>
                    <span style="min-width:65px"></span>
                </div>
                <div class="eps-bridge-row">
                    <span class="eps-bridge-label">PF EPS (with Synergies)</span>
                    <div class="eps-bridge-bar-container">
                        <div class="eps-bridge-bar with-syn" style="width:${Math.min(withSynW, 100)}%"></div>
                    </div>
                    <span class="eps-bridge-value">₹${fmtDec(d.pf_eps_with_syn)}</span>
                    <span class="eps-bridge-badge ${cls}">${adVal > 0 ? '+' : ''}${fmtDec(adVal, 1)}%</span>
                </div>
            </div>
        `;
    });
}

// ==========================================================================
// BREAKEVEN VISUAL
// ==========================================================================

function renderBreakeven() {
    const container = document.getElementById('breakevenVisual');
    if (!container) return;
    const be = MODEL.breakeven;
    const maxSyn = 3100;

    container.innerHTML = `
        <div class="breakeven-bar-container">
            <div class="breakeven-bar-label">
                <span style="color:var(--text-secondary)">Breakeven Synergy Required</span>
                <span style="color:#f59e0b;font-family:var(--font-mono);font-weight:600">₹${fmt(be.breakeven_synergy)} Cr/year</span>
            </div>
            <div class="breakeven-bar-track">
                <div class="breakeven-bar-fill breakeven" style="width:${be.breakeven_synergy / maxSyn * 100}%"></div>
            </div>
        </div>
        <div class="breakeven-bar-container">
            <div class="breakeven-bar-label">
                <span style="color:var(--text-secondary)">Actual Year 1 Synergy</span>
                <span style="color:var(--accent-cyan);font-family:var(--font-mono);font-weight:600">₹${fmt(be.actual_year1_synergy)} Cr/year</span>
            </div>
            <div class="breakeven-bar-track">
                <div class="breakeven-bar-fill actual" style="width:${be.actual_year1_synergy / maxSyn * 100}%"></div>
                <div class="breakeven-bar-marker" style="left:${be.breakeven_synergy / maxSyn * 100}%"></div>
            </div>
        </div>
        <div class="breakeven-info" style="margin-top:1.5rem">
            <div class="breakeven-stat">
                <div class="breakeven-stat-value" style="color:#f59e0b">₹${fmt(be.breakeven_synergy)} Cr</div>
                <div class="breakeven-stat-label">Breakeven Synergy</div>
            </div>
            <div class="breakeven-stat">
                <div class="breakeven-stat-value" style="color:var(--accent-cyan)">₹${fmt(be.actual_year1_synergy)} Cr</div>
                <div class="breakeven-stat-label">Year 1 Synergy</div>
            </div>
            <div class="breakeven-stat">
                <div class="breakeven-stat-value" style="color:${be.synergy_cushion >= 0 ? 'var(--positive)' : 'var(--negative)'}">
                    ₹${fmt(Math.abs(be.synergy_cushion))} Cr ${be.synergy_cushion >= 0 ? 'Cushion' : 'Shortfall'}
                </div>
                <div class="breakeven-stat-label">Year 1 ${be.synergy_cushion >= 0 ? 'Surplus' : 'Gap'}</div>
            </div>
        </div>
    `;
}

// ==========================================================================
// NPV WATERFALL
// ==========================================================================

function renderNPVWaterfall() {
    const container = document.getElementById('npvWaterfall');
    if (!container) return;
    const npv = MODEL.npv;
    const maxVal = npv.total_npv;

    const bars = [
        { label: 'PV Year 1', value: npv.pv_year1, type: 'positive' },
        { label: 'PV Year 2', value: npv.pv_year2, type: 'positive' },
        { label: 'PV Year 3', value: npv.pv_year3, type: 'positive' },
        { label: 'PV Terminal', value: npv.pv_terminal, type: 'positive' },
        { label: 'Costs to\nAchieve', value: npv.costs_to_achieve, type: 'negative' },
        { label: 'Net NPV', value: npv.npv_net, type: 'total' },
    ];

    bars.forEach(bar => {
        const height = Math.max(15, (bar.value / maxVal) * 180);
        container.innerHTML += `
            <div class="npv-bar-group">
                <div class="npv-bar-value">₹${fmt(bar.value)} Cr</div>
                <div class="npv-bar ${bar.type}" style="height:${height}px"></div>
                <div class="npv-bar-label">${bar.label}</div>
            </div>
        `;
    });
}

// ==========================================================================
// SENSITIVITY MATRIX
// ==========================================================================

function renderSensitivityMatrix() {
    const container = document.getElementById('sensitivityMatrix');
    if (!container) return;
    const sens = MODEL.sensitivity;

    let html = '<table><thead><tr><th>Premium \\ Synergy (₹ Cr)</th>';
    sens.synRange.forEach(s => { html += `<th>${fmt(s)}</th>`; });
    html += '</tr></thead><tbody>';

    sens.matrix.forEach(row => {
        const isBase = Math.abs(row.prem - 13.2) < 0.5;
        html += `<tr class="${isBase ? 'base-row' : ''}">`;
        html += `<td class="header-cell">${row.prem}%</td>`;
        row.values.forEach(val => {
            const cls = val > 0 ? 'positive' : 'negative';
            html += `<td class="${cls}">${val > 0 ? '+' : ''}${fmtDec(val, 1)}%</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// ==========================================================================
// PREMIUM SENSITIVITY
// ==========================================================================

function renderPremiumSensitivity() {
    const container = document.getElementById('premiumSensitivity');
    if (!container) return;
    const data = MODEL.sensitivity.premium;
    const maxAd = Math.max(...data.map(d => Math.abs(d.ad)));

    data.forEach(d => {
        const isBase = Math.abs(d.prem - 13.2) < 0.5;
        const cls = d.ad > 0 ? 'positive' : 'negative';
        const width = Math.abs(d.ad) / maxAd * 45;

        container.innerHTML += `
            <div class="sens-bar-row ${isBase ? 'base' : ''}">
                <span class="sens-bar-label">${d.prem}%</span>
                <div class="sens-bar-track">
                    <div class="sens-bar-center"></div>
                    <div class="sens-bar-fill ${cls}" style="width:${width}%"></div>
                </div>
                <span class="sens-bar-value ${cls}">${d.ad > 0 ? '+' : ''}${fmtDec(d.ad, 1)}%</span>
            </div>
        `;
    });
}

// ==========================================================================
// DEBT COST SENSITIVITY
// ==========================================================================

function renderDebtSensitivity() {
    const container = document.getElementById('debtSensitivity');
    if (!container) return;
    const data = MODEL.sensitivity.debt;
    const maxAd = Math.max(...data.map(d => Math.abs(d.ad)));

    data.forEach(d => {
        const isBase = Math.abs(d.rate - 8.75) < 0.1;
        const cls = d.ad > 0 ? 'positive' : 'negative';
        const width = Math.abs(d.ad) / maxAd * 45;

        container.innerHTML += `
            <div class="sens-bar-row ${isBase ? 'base' : ''}">
                <span class="sens-bar-label">${fmtDec(d.rate, 1)}%</span>
                <div class="sens-bar-track">
                    <div class="sens-bar-center"></div>
                    <div class="sens-bar-fill ${cls}" style="width:${width}%"></div>
                </div>
                <span class="sens-bar-value ${cls}">${d.ad > 0 ? '+' : ''}${fmtDec(d.ad, 1)}%</span>
            </div>
        `;
    });
}

// ==========================================================================
// PRECEDENT TRANSACTIONS
// ==========================================================================

function renderPrecedentTable() {
    const tbody = document.getElementById('precedentTable');
    if (!tbody) return;

    MODEL.precedents.forEach(txn => {
        let tr = document.createElement('tr');
        if (txn.thisDeal) tr.classList.add('this-deal');

        const premText = txn.premium > 0 ? `${fmtDec(txn.premium, 1)}%` : 'N/A';
        const cells = [
            txn.date, txn.acquirer, txn.target,
            `${fmtDec(txn.ev_ebitda, 1)}x`, `$${txn.ev_tonne}`,
            premText, fmt(txn.deal_value)
        ];

        cells.forEach((val, i) => {
            let td = document.createElement('td');
            td.textContent = val;
            if (i >= 3) { td.classList.add('num'); }
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}

function renderPrecedentCharts() {
    // EV/EBITDA Chart
    const evContainer = document.getElementById('evEbitdaChart');
    if (evContainer) {
        const maxEv = 18;
        MODEL.precedents.forEach(txn => {
            const width = (txn.ev_ebitda / maxEv) * 100;
            const cls = txn.thisDeal ? 'this-deal' : 'other';
            evContainer.innerHTML += `
                <div class="prec-bar-row">
                    <span class="prec-bar-label">${txn.target}</span>
                    <div class="prec-bar-track">
                        <div class="prec-bar-fill ${cls}" style="width:${width}%"></div>
                    </div>
                    <span class="prec-bar-value">${fmtDec(txn.ev_ebitda, 1)}x</span>
                </div>
            `;
        });
    }

    // Premium Chart
    const premContainer = document.getElementById('premiumChart');
    if (premContainer) {
        const maxPrem = 25;
        MODEL.precedents.filter(t => t.premium > 0).forEach(txn => {
            const width = (txn.premium / maxPrem) * 100;
            const cls = txn.thisDeal ? 'this-deal' : 'other';
            premContainer.innerHTML += `
                <div class="prec-bar-row">
                    <span class="prec-bar-label">${txn.target}</span>
                    <div class="prec-bar-track">
                        <div class="prec-bar-fill ${cls}" style="width:${width}%"></div>
                    </div>
                    <span class="prec-bar-value">${fmtDec(txn.premium, 1)}%</span>
                </div>
            `;
        });
    }
}
