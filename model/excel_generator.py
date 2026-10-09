"""
Excel generator — builds a LIVE formula workbook of the merger model.

Every calculated cell is an Excel formula that traces back to the single
'Inputs' sheet (blue font). Change an input in Excel and the whole workbook
recalculates. The only static tabs are 'Historicals' (filed data),
'Sensitivity' (each cell is a full Python re-run; labelled as such) and the
precedent inputs.

The 'Checks' sheet holds (a) integrity checks written as formulas and
(b) a reconciliation of every formula output against the Python model,
so the two implementations cannot drift apart unnoticed.
"""

import os
import re
import shutil
import tempfile
import zipfile
from xml.sax.saxutils import escape

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from model.merger_model import ENTITIES, FINITE_INTANGIBLES

NAVY = "1F3864"
F_TITLE = Font(name="Calibri", size=14, bold=True, color=NAVY)
F_SECTION = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
F_INPUT = Font(name="Calibri", size=10, color="0000FF")
F_CALC = Font(name="Calibri", size=10, color="000000")
F_BOLD = Font(name="Calibri", size=10, bold=True)
F_NOTE = Font(name="Calibri", size=9, italic=True, color="666666")
FILL_SECTION = PatternFill("solid", fgColor=NAVY)
FILL_INPUT = PatternFill("solid", fgColor="FFF2CC")
FILL_HEAD = PatternFill("solid", fgColor="D9E1F2")
THIN = Side(style="thin", color="BFBFBF")

CR = '#,##0;(#,##0);"–"'
CR1 = '#,##0.0;(#,##0.0);"–"'
PCT = '0.0%;(0.0%);"–"'
PCT2 = '0.00%;(0.00%);"–"'
MULT = '0.0"x"'
MULT2 = '0.00"x"'
NUM2 = '#,##0.00'
NUM4 = '0.0000'

YEAR_COLS = ["D", "E", "F"]
BASE_COL = "C"
TOKEN = re.compile(r"\{([A-Za-z0-9_]+)(?:\.(Y1|Y2|Y3|base|prev|range))?\}")


class Book:
    def __init__(self):
        self.wb = Workbook()
        self.wb.remove(self.wb.active)
        self.refs = {}       # key -> {"sheet", "row", "kind": scalar|yearly, "has_base"}
        self.recon = []      # (key, label, python value(s), fmt)
        self.pending = []    # formulas resolved after every key is registered (allows forward references)

    def put(self, cell, template, cur_col):
        self.pending.append((cell, template, cur_col))

    def finalize(self):
        for cell, template, cur_col in self.pending:
            cell.value = self.resolve(template, cell.parent.title, cur_col)

    def sheet(self, name, years=None, base_label=None):
        ws = self.wb.create_sheet(name)
        return Sheet(self, ws, years, base_label)

    def ref(self, key, suffix, cur_sheet, cur_col):
        r = self.refs[key]
        same = r["sheet"] == cur_sheet
        q = "" if same else f"'{r['sheet']}'!"
        if r["kind"] == "scalar":
            return f"{q}$C${r['row']}"
        if suffix == "range":
            return f"{q}${YEAR_COLS[0]}${r['row']}:${YEAR_COLS[-1]}${r['row']}"
        if suffix == "base":
            col = BASE_COL
        elif suffix in ("Y1", "Y2", "Y3"):
            col = YEAR_COLS[int(suffix[1]) - 1]
        elif suffix == "prev":
            idx = YEAR_COLS.index(cur_col)
            col = BASE_COL if idx == 0 else YEAR_COLS[idx - 1]
        else:
            if cur_col not in YEAR_COLS:
                raise ValueError(f"{key}: yearly ref needs a year suffix in a scalar formula")
            col = cur_col
        return f"{q}{col}{r['row']}" if same else f"{q}${col}${r['row']}"

    def resolve(self, template, cur_sheet, cur_col):
        return "=" + TOKEN.sub(lambda m: self.ref(m.group(1), m.group(2), cur_sheet, cur_col), template)


class Sheet:
    def __init__(self, book, ws, years, base_label):
        self.b, self.ws, self.row = book, ws, 1
        self.years, self.base_label = years, base_label
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 2
        ws.column_dimensions["B"].width = 50
        for c in ["C"] + YEAR_COLS:
            ws.column_dimensions[c].width = 15
        ws.column_dimensions["G"].width = 3
        ws.column_dimensions["H"].width = 70

    # ---- layout helpers -------------------------------------------------
    def title(self, text, sub=None):
        self.ws.cell(self.row, 2, text).font = F_TITLE
        self.row += 1
        if sub:
            self.ws.cell(self.row, 2, sub).font = F_NOTE
            self.row += 1
        self.row += 1

    def section(self, text, year_header=False):
        for col in range(2, 9):
            self.ws.cell(self.row, col).fill = FILL_SECTION
        self.ws.cell(self.row, 2, text).font = F_SECTION
        if year_header and self.years:
            if self.base_label:
                self.ws.cell(self.row, 3, self.base_label).font = F_SECTION
            for i, y in enumerate(self.years):
                self.ws.cell(self.row, 4 + i, y).font = F_SECTION
            for col in range(3, 7):
                self.ws.cell(self.row, col).alignment = Alignment(horizontal="right")
        self.row += 1

    def note(self, text):
        self.ws.cell(self.row, 2, text).font = F_NOTE
        self.row += 1

    def blank(self, n=1):
        self.row += n

    def text_row(self, label, *vals, bold=False, fmt=None):
        self.ws.cell(self.row, 2, label).font = F_BOLD if bold else F_CALC
        for i, v in enumerate(vals):
            c = self.ws.cell(self.row, 3 + i, v)
            c.font = F_BOLD if bold else F_CALC
            if fmt and isinstance(v, (int, float)):
                c.number_format = fmt
        self.row += 1

    def _register(self, key, kind, has_base=False):
        if key in self.b.refs:
            raise ValueError(f"duplicate key {key}")
        self.b.refs[key] = {"sheet": self.ws.title, "row": self.row, "kind": kind, "has_base": has_base}

    def _label(self, label, note, bold):
        self.ws.cell(self.row, 2, label).font = F_BOLD if bold else F_CALC
        if note:
            self.ws.cell(self.row, 8, note).font = F_NOTE

    # ---- cells ----------------------------------------------------------
    def inp(self, key, label, value, fmt=CR, note=None):
        self._register(key, "scalar")
        self._label(label, note, False)
        c = self.ws.cell(self.row, 3, value)
        c.font, c.fill, c.number_format = F_INPUT, FILL_INPUT, fmt
        self.row += 1

    def calc(self, key, label, formula, fmt=CR, py=None, note=None, bold=False, recon=True):
        self._register(key, "scalar")
        self._label(label, note, bold)
        c = self.ws.cell(self.row, 3)
        self.b.put(c, formula, "C")
        c.font, c.number_format = (F_BOLD if bold else F_CALC), fmt
        if bold:
            c.border = Border(top=THIN)
        if py is not None and recon:
            self.b.recon.append((key, label, py, fmt))
        self.row += 1

    def yinp(self, key, label, values, fmt=CR, base=None, note=None):
        self._register(key, "yearly", base is not None)
        self._label(label, note, False)
        if base is not None:
            c = self.ws.cell(self.row, 3, base)
            c.font, c.fill, c.number_format = F_INPUT, FILL_INPUT, fmt
        for i, v in enumerate(values):
            c = self.ws.cell(self.row, 4 + i, v)
            c.font, c.fill, c.number_format = F_INPUT, FILL_INPUT, fmt
        self.row += 1

    def ycalc(self, key, label, formula, fmt=CR, py=None, note=None, bold=False, base=None, recon=True):
        """formula: one template for all years, or a list with one template per year."""
        self._register(key, "yearly", base is not None)
        self._label(label, note, bold)
        if base is not None:
            c = self.ws.cell(self.row, 3)
            if isinstance(base, str):
                self.b.put(c, base, "C")
            else:
                c.value = base
            c.font, c.number_format = (F_INPUT if not isinstance(base, str) else F_CALC), fmt
        for i, col in enumerate(YEAR_COLS):
            tpl = formula[i] if isinstance(formula, list) else formula
            c = self.ws.cell(self.row, 4 + i)
            self.b.put(c, tpl, col)
            c.font, c.number_format = (F_BOLD if bold else F_CALC), fmt
            if bold:
                c.border = Border(top=THIN)
        if py is not None and recon:
            self.b.recon.append((key, label, list(py), fmt))
        self.row += 1


# ==========================================================================
# BUILD
# ==========================================================================

def generate_excel_model(model, output_path):
    b = Book()
    _cover(b, model)
    _inputs(b, model)
    _historicals(b, model)
    _deal(b, model)
    _ppa(b, model)
    _projections(b, model)
    _synergies(b, model)
    _pro_forma(b, model)
    _balance_sheet(b, model)
    _precedents(b, model)
    _sensitivity(b, model)
    _checks(b, model)
    b.finalize()

    order = ["Cover", "Checks", "Inputs", "Deal & Financing", "PPA & Goodwill", "Projections", "Synergies",
             "Pro Forma & Returns", "Balance Sheet", "Precedents", "Sensitivity", "Historicals"]
    b.wb._sheets = [b.wb[n] for n in order]
    b.wb.calculation.fullCalcOnLoad = True
    b.wb.save(output_path)
    embed_cached_values(output_path)
    return output_path


def embed_cached_values(path):
    """
    openpyxl writes formulas without results, so Excel's Protected View (and any
    viewer that does not recalculate) would show blank cells. Recalculate the
    workbook with the independent 'formulas' engine and write each result into
    the file as the formula's cached value. Excel still recalculates on open.
    """
    try:
        import formulas
    except ImportError:
        print("WARNING: 'formulas' not installed; workbook saved without cached values "
              "(cells calculate when editing is enabled in Excel). pip install formulas")
        return False

    solution = formulas.ExcelModel().loads(path).finish().calculate()
    cell_key = re.compile(r"^'\[[^\]]+\](.+)'!([A-Z]+[0-9]+)$")
    values = {}
    for key, val in solution.items():
        m = cell_key.match(str(key))
        if m and hasattr(val, "value"):
            values[(m.group(1).upper(), m.group(2))] = val.value[0][0]

    with zipfile.ZipFile(path) as z:
        files = {n: z.read(n) for n in z.namelist()}
    wb_xml = files["xl/workbook.xml"].decode("utf-8")
    rels = files["xl/_rels/workbook.xml.rels"].decode("utf-8")
    targets = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="/?(?:xl/)?([^"]+)"', rels))
    targets.update({k: v for v, k in re.findall(r'Target="/?(?:xl/)?([^"]+)"[^>]*Id="(rId\d+)"', rels)})

    def cached(sheet, m):
        attrs, ref, formula = m.group(1), m.group(2), m.group(3)
        v = values.get((sheet, ref))
        if v is None or (isinstance(v, str) and v == ""):
            return m.group(0)
        if isinstance(v, bool):
            return f'<c{attrs} t="b"><f>{formula}</f><v>{int(v)}</v></c>'
        if isinstance(v, str):
            return f'<c{attrs} t="str"><f>{formula}</f><v>{escape(v)}</v></c>'
        try:
            return f'<c{attrs}><f>{formula}</f><v>{repr(float(v))}</v></c>'
        except (TypeError, ValueError):   # Excel error values such as #DIV/0!
            return f'<c{attrs} t="e"><f>{formula}</f><v>{escape(str(v))}</v></c>'

    formula_cell = re.compile(r'<c( r="([A-Z]+[0-9]+)"[^>]*?)><f>(.*?)</f><v\s*/?>(?:</v>)?</c>')
    for name, rid in re.findall(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="(rId\d+)"', wb_xml):
        sheet = name.replace("&amp;", "&").upper()
        part = "xl/" + targets[rid]
        xml = files[part].decode("utf-8")
        files[part] = formula_cell.sub(lambda m, s=sheet: cached(s, m), xml).encode("utf-8")

    fd, tmp = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in files.items():
            z.writestr(n, data)
    shutil.move(tmp, path)
    return True


def _cover(b, m):
    s = b.sheet("Cover")
    s.title("Adani Group / Ambuja Cements & ACC — Merger Consequences Model",
            "INR crore unless stated. Deal announced 15-May-2022, completed 16-Sep-2022.")
    s.section("How this workbook works")
    for line in [
        "Blue cells on a yellow background are inputs (all on the 'Inputs' sheet; synergy items on 'Synergies'; deal data on 'Precedents').",
        "Black cells are live Excel formulas. Change any input and the workbook recalculates.",
        "'Checks' tests the model's integrity and reconciles every formula against the Python model (python run_model.py).",
        "'Sensitivity' is static: each cell is a full re-run of the Python model with one input changed.",
        "'Historicals' holds filed CY2019-CY2021 standalone figures used as the projection base.",
        "Assumptions are labelled [ASSUMPTION] with a rationale; filed data cite their source.",
    ]:
        s.note(line)
    s.blank()
    s.section("Sources")
    for k, v in m.get_summary()["sources"].items():
        s.text_row(k, v)


def _inputs(b, m):
    inp = m.inp
    s = b.sheet("Inputs", years=m.years, base_label="CY2021A")
    s.title("Inputs", "Every hard-coded number used by the formulas. Change blue cells only.")
    s.ws.column_dimensions["H"].width = 80

    a, c = inp["ambuja_shares"], inp["acc_shares"]
    s.section("Deal terms (filed)")
    s.inp("fx", "INR per USD at completion (16-Sep-2022)", inp["fx"]["inr_per_usd_at_close"], NUM2, "[FILED] NSE / Yahoo USDINR close")
    s.inp("amb_sh", "Ambuja shares outstanding (crore)", a["total_shares_cr"], NUM2, "[DERIVED] share capital ₹397.13 Cr / ₹2 face value")
    s.inp("amb_holcim", "Holcim stake in Ambuja sold", a["holcim_stake_pct"] / 100, PCT2, "[FILED] Holcim release")
    s.inp("amb_oo_sh", "Ambuja open-offer shares tendered (crore)", a["open_offer_shares_tendered_cr"], NUM4, "[FILED] Business Standard, 10-Sep-2022")
    s.inp("amb_px", "Ambuja offer price (₹/share)", a["offer_price"], NUM2, "[FILED] Holcim release")
    s.inp("amb_undist", "Ambuja undisturbed close 13-May-2022 (₹)", a["undisturbed_close"], NUM2, "[FILED] NSE close")
    s.inp("amb_close_comp", "Ambuja close at completion 16-Sep-2022 (₹)", a["close_at_completion"], NUM2, "[FILED] NSE close")
    s.inp("amb_in_acc", "Ambuja's stake in ACC", a["stake_in_acc_pct"] / 100, PCT2, "[FILED] Holcim release")
    s.inp("acc_sh", "ACC shares outstanding (crore)", c["total_shares_cr"], NUM2, "[FILED]")
    s.inp("acc_holcim", "Holcim direct stake in ACC sold", c["holcim_direct_stake_pct"] / 100, PCT2, "[FILED] Holcim release")
    s.inp("acc_oo_sh", "ACC open-offer shares tendered (crore)", c["open_offer_shares_tendered_cr"], NUM4, "[FILED] Business Standard, 10-Sep-2022")
    s.inp("acc_px", "ACC offer price (₹/share)", c["offer_price"], NUM2, "[FILED] Holcim release")
    s.inp("acc_undist", "ACC undisturbed close 13-May-2022 (₹)", c["undisturbed_close"], NUM2, "[FILED] NSE close")
    s.inp("acc_close_comp", "ACC close at completion 16-Sep-2022 (₹)", c["close_at_completion"], NUM2, "[FILED] NSE close")
    s.inp("capacity", "Combined capacity (MTPA)", inp["transaction"]["combined_capacity_mtpa"], CR1, "[FILED] Adani release")
    s.inp("rep_usd", "Reported consideration (US$ bn)", inp["transaction"]["consideration_usd_bn_reported"], NUM2, "[FILED] Adani release — used in Checks only")
    s.inp("rep_amb_pct", "Reported post-deal stake in Ambuja", inp["transaction"]["post_deal_ambuja_pct_reported"] / 100, PCT2, "[FILED] Adani release — used in Checks only")
    s.inp("rep_acc_pct", "Reported post-deal stake in ACC (incl. via Ambuja)", inp["transaction"]["post_deal_acc_pct_reported"] / 100, PCT2, "[FILED] Adani release — used in Checks only")
    s.inp("txn_pct", "Transaction costs (% of consideration)", inp["deal_costs"]["transaction_costs_pct_of_consideration"] / 100, PCT, "[ASSUMPTION] advisory, legal, stamp duty; expensed")

    d = inp["acq_debt"]
    s.blank()
    s.section("Acquisition financing (holdco)")
    s.inp("debt_usd", "Acquisition facilities (US$ bn)", inp["transaction"]["acq_debt_usd_bn"], NUM2, "[FILED] Adani release: US$4.5bn from 14 banks")
    s.inp("bridge_usd", "of which bridge loans (US$ bn)", d["bridge_usd_bn"], NUM2, "[FILED] Business Standard, 1-Dec-2022")
    s.inp("term_rate", "Term loan rate", d["term_rate_pct"] / 100, PCT2, "[ASSUMPTION] USD SOFR + ~275bp")
    s.inp("bridge_rate", "Bridge loan rate (Year 1)", d["bridge_rate_pct"] / 100, PCT2, "[ASSUMPTION]")
    s.inp("refi_rate", "Refinanced rate (Year 2 onward)", d["refi_rate_pct"] / 100, PCT2, "[ASSUMPTION] bridge refinanced into 5-yr debt")
    s.inp("deductible", "Holdco interest tax-deductible? (1 = yes, 0 = no)", 1 if d["interest_tax_deductible"] else 0, "0",
          "[ASSUMPTION] Mauritius SPV has no taxable income; no tax consolidation in India")
    s.inp("wht_amb", "Withholding tax on Ambuja dividends", inp["holdco"]["wht_on_ambuja_dividends_pct"] / 100, PCT, "[ASSUMPTION] India–Mauritius DTAA (>=10% holding)")
    s.inp("wht_acc", "Withholding tax on ACC dividends", inp["holdco"]["wht_on_acc_dividends_pct"] / 100, PCT, "[ASSUMPTION] DTAA (<10% direct holding)")

    pr = inp["projection"]
    s.blank()
    s.section("Projections and cost of capital", year_header=True)
    s.yinp("amb_g", "Ambuja revenue growth", [x / 100 for x in pr["ambuja_revenue_growth_pct"]], PCT, note="[ASSUMPTION] Year 1 vs CY2021")
    s.yinp("acc_g", "ACC revenue growth", [x / 100 for x in pr["acc_revenue_growth_pct"]], PCT, note="[ASSUMPTION]")
    s.yinp("amb_m", "Ambuja EBITDA margin", [x / 100 for x in pr["ambuja_ebitda_margin_pct"]], PCT, note="[ASSUMPTION] CY2021 actual 23.0%")
    s.yinp("acc_m", "ACC EBITDA margin", [x / 100 for x in pr["acc_ebitda_margin_pct"]], PCT, note="[ASSUMPTION] CY2021 actual 18.6%")
    s.inp("tax", "Corporate tax rate", pr["tax_rate_pct"] / 100, PCT2, "[FILED] s.115BAA")
    s.inp("payout", "Dividend payout ratio (Ambuja & ACC)", pr["dividend_payout_pct"] / 100, PCT, "[ASSUMPTION] in line with 2019-20 history (19%)")
    cc = inp["cost_of_capital"]
    s.inp("rf", "Risk-free rate (India 10Y)", cc["risk_free_pct"] / 100, PCT2, "[ASSUMPTION]")
    s.inp("erp", "Equity risk premium", cc["equity_risk_premium_pct"] / 100, PCT2, "[ASSUMPTION]")
    s.inp("beta_a", "Asset beta (Indian cement)", cc["asset_beta"], NUM2, "[ASSUMPTION] targets are net-cash, so equity beta ≈ asset beta")
    s.inp("g_syn", "Synergy terminal growth", cc["synergy_terminal_growth_pct"] / 100, PCT, "[ASSUMPTION] RBI CPI target")

    ppa = inp["ppa"]
    s.blank()
    s.section("Purchase price allocation (illustrative estimates)")
    for e in ENTITIES:
        for k, v in ppa["step_ups"][e].items():
            s.inp(f"su_{e}_{k}", f"{e.upper()} step-up: {k.replace('_', ' ')}", v, CR, "[ASSUMPTION] no public PPA for the holdco")
    s.inp("life_ppe", "PP&E step-up life (years)", ppa["ppe_life_years"], "0", "[ASSUMPTION]")
    s.inp("life_int", "Finite intangibles life (years)", ppa["finite_intangible_life_years"], "0",
          "[ASSUMPTION] mineral rights, customers, contracts; brand indefinite; inventory released in Year 1")

    s.blank()
    s.section("CY2021 base and closing balance sheet (filed, standalone)")
    for e, h, bs in (("amb", inp["ambuja_hist"], inp["ambuja_bs"]), ("acc", inp["acc_hist"], inp["acc_bs"])):
        name = "Ambuja" if e == "amb" else "ACC"
        s.inp(f"{e}_rev21", f"{name} revenue CY2021", h["revenue"][-1], CR, "[FILED] Screener (standalone)")
        s.inp(f"{e}_da21", f"{name} depreciation CY2021", h["depreciation"][-1], CR, "[FILED]")
        s.inp(f"{e}_int21", f"{name} interest expense CY2021", h["interest_expense"][-1], CR, "[FILED]")
        s.inp(f"{e}_oi21", f"{name} other income CY2021 (pre-exceptional)", h["other_income_normal"][-1], CR, "[FILED]")
        for k in ("share_capital", "reserves", "borrowings", "other_liabilities", "fixed_assets", "cwip", "investments",
                  "inventories", "trade_receivables", "cash", "other_assets"):
            s.inp(f"{e}_{k}", f"{name} 31-Dec-2021: {k.replace('_', ' ')}", bs[k], CR, "[FILED]")
    s.inp("acc_dps21", "ACC dividend per share paid in CY2021 (₹)", inp["intercompany"]["acc_dps_paid_in_cy2021"], NUM2,
          "[DERIVED] 19% payout on CY2020 NI; removed from Ambuja's income as intra-group")
    s.inp("amb_ebitda21", "Ambuja EBITDA CY2021", inp["ambuja_hist"]["ebitda"][-1], CR, "[FILED]")
    s.inp("acc_ebitda21", "ACC EBITDA CY2021", inp["acc_hist"]["ebitda"][-1], CR, "[FILED]")


def _historicals(b, m):
    s = b.sheet("Historicals")
    s.title("Historical standalone financials (filed)", "Source: company filings via Screener.in. Year ended 31 December.")
    for e, h in (("Ambuja Cements", m.inp["ambuja_hist"]), ("ACC Ltd", m.inp["acc_hist"])):
        s.section(e)
        s.text_row("INR crore", *h["years"], "Check: EBITDA = revenue − opex", bold=True)
        for k in ("revenue", "operating_expenses", "ebitda", "other_income_normal", "exceptional_items",
                  "interest_expense", "depreciation", "pbt", "net_income", "eps", "dividend_payout_pct"):
            s.text_row(k.replace("_", " ").capitalize(), *h[k], fmt=NUM2 if k == "eps" else CR)
        r_rev, r_opex, r_ebitda = s.row - 11, s.row - 10, s.row - 9
        for i, col in enumerate("CDE"):
            s.ws.cell(s.row, 3 + i, f"={col}{r_rev}-{col}{r_opex}-{col}{r_ebitda}").number_format = CR
        s.ws.cell(s.row, 2, "EBITDA tie-out (should be 0)").font = F_NOTE
        s.row += 2


def _deal(b, m):
    s = b.sheet("Deal & Financing")
    s.title("Deal, sources & uses, ownership")
    d, fin, own = m.deal, m.financing, m.own
    sh = d["shares_acquired_cr"]
    s.section("Shares acquired (crore) and consideration")
    s.calc("sh_hamb", "Ambuja shares bought from Holcim", "{amb_sh}*{amb_holcim}", NUM4, sh["holcim_ambuja"])
    s.calc("sh_hacc", "ACC shares bought from Holcim (direct)", "{acc_sh}*{acc_holcim}", NUM4, sh["holcim_acc"])
    s.calc("v_hamb", "Holcim Ambuja stake", "{sh_hamb}*{amb_px}", CR, d["consideration_by_component"]["holcim_ambuja"])
    s.calc("v_hacc", "Holcim direct ACC stake", "{sh_hacc}*{acc_px}", CR, d["consideration_by_component"]["holcim_acc"])
    s.calc("v_ooamb", "Ambuja open offer (shares tendered)", "{amb_oo_sh}*{amb_px}", CR, d["consideration_by_component"]["open_offer_ambuja"])
    s.calc("v_ooacc", "ACC open offer (shares tendered)", "{acc_oo_sh}*{acc_px}", CR, d["consideration_by_component"]["open_offer_acc"])
    s.calc("consideration", "Total consideration", "{v_hamb}+{v_hacc}+{v_ooamb}+{v_ooacc}", CR, d["total_consideration"], bold=True)
    s.calc("consideration_usd", "Total consideration (US$ bn)", "{consideration}/{fx}/100", NUM2, d["total_consideration_usd_bn"])
    s.calc("txn_costs", "Transaction costs", "{consideration}*{txn_pct}", CR, d["transaction_costs"])
    s.calc("total_uses", "Total uses", "{consideration}+{txn_costs}", CR, d["total_uses"], bold=True)
    s.blank()
    s.section("Sources (holdco)")
    s.calc("acq_debt", "Acquisition debt (INR)", "{debt_usd}*{fx}*100", CR, fin["acq_debt_total"])
    s.calc("bridge0", "  of which bridge", "{bridge_usd}*{fx}*100", CR, fin["sources"]["acq_bridge_loan"])
    s.calc("term0", "  of which term loan", "{acq_debt}-{bridge0}", CR, fin["sources"]["acq_term_loan"])
    s.calc("sponsor_eq", "Sponsor equity (balancing item)", "{total_uses}-{acq_debt}", CR, fin["sources"]["sponsor_equity"])
    s.calc("total_sources", "Total sources", "{acq_debt}+{sponsor_eq}", CR, fin["total_sources"], bold=True)
    s.note("Target cash cannot fund the purchase: Companies Act s.67 and ~37% minority ownership of Ambuja.")
    s.blank()
    s.section("Ownership after the deal")
    s.calc("own_amb", "Adani stake in Ambuja", "({sh_hamb}+{amb_oo_sh})/{amb_sh}", PCT2, own["adani_in_ambuja"])
    s.calc("own_acc_direct", "Adani direct stake in ACC", "({sh_hacc}+{acc_oo_sh})/{acc_sh}", PCT2, own["adani_direct_in_acc"])
    s.calc("own_acc_ctrl", "Adani-controlled stake in ACC (direct + via Ambuja)", "{own_acc_direct}+{amb_in_acc}", PCT2, own["adani_controlled_in_acc"])
    s.calc("own_acc_lt", "Adani look-through economic stake in ACC", "{own_amb}*{amb_in_acc}+{own_acc_direct}", PCT2, own["adani_lookthrough_in_acc"])
    s.blank()
    s.section("Premium")
    s.calc("prem_amb", "Ambuja premium to undisturbed close", "{amb_px}/{amb_undist}-1", PCT, d["premium_to_undisturbed_pct"]["ambuja"] / 100)
    s.calc("prem_acc", "ACC premium to undisturbed close", "{acc_px}/{acc_undist}-1", PCT, d["premium_to_undisturbed_pct"]["acc"] / 100)
    s.calc("prem_paid", "Premium paid over undisturbed value",
           "({sh_hamb}+{amb_oo_sh})*({amb_px}-{amb_undist})+({sh_hacc}+{acc_oo_sh})*({acc_px}-{acc_undist})", CR, d["premium_paid_cr"])
    s.calc("mv_completion", "Market value of stakes at completion-day close",
           "({sh_hamb}+{amb_oo_sh})*{amb_close_comp}+({sh_hacc}+{acc_oo_sh})*{acc_close_comp}", CR, d["market_value_of_stakes_at_completion"])
    s.blank()
    s.section("Cost of capital")
    coc = m.coc
    s.calc("ku", "Unlevered cost of capital (rf + βa × ERP)", "{rf}+{beta_a}*{erp}", PCT2, coc["unlevered_cost_of_capital_pct"] / 100)
    s.calc("de", "Holdco debt / equity at cost", "{acq_debt}/({consideration}-{acq_debt})", MULT2, coc["holdco_debt_to_equity"])
    s.calc("beta_l", "Relevered beta (Hamada; no shield unless deductible)", "{beta_a}*(1+(1-{tax}*{deductible})*{de})", NUM2, coc["levered_beta"])
    s.calc("ke", "Levered cost of equity on sponsor equity", "{rf}+{beta_l}*{erp}", PCT2, coc["levered_cost_of_equity_pct"] / 100)
    s.blank()
    s.section("Valuation at offer prices")
    v = m.valuation
    s.calc("eq_value", "100% equity value (Ambuja + ACC minority 49.95%)", "{amb_sh}*{amb_px}+(1-{amb_in_acc})*{acc_sh}*{acc_px}", CR, v["equity_value_at_offer"])
    s.calc("net_debt21", "Net debt 31-Dec-2021 (net cash shown negative)", "{amb_borrowings}+{acc_borrowings}-{amb_cash}-{acc_cash}", CR, v["net_debt_cy2021"])
    s.calc("ev", "Enterprise value", "{eq_value}+{net_debt21}", CR, v["enterprise_value"], bold=True)
    s.calc("ev_ebitda", "EV / EBITDA CY2021", "{ev}/({amb_ebitda21}+{acc_ebitda21})", MULT, v["ev_to_ebitda_cy2021"])
    s.calc("ev_t_inr", "EV per tonne of capacity (₹)", "{ev}*10/{capacity}", CR, v["ev_per_tonne_inr"])
    s.calc("ev_t_usd", "EV per tonne of capacity (US$)", "{ev_t_inr}/{fx}", CR, v["ev_per_tonne_usd"])


def _ppa(b, m):
    s = b.sheet("PPA & Goodwill")
    s.title("Purchase price allocation and goodwill",
            "Look-through method; NCI measured at its share of identifiable net assets (Ind AS 103 option).")
    for e, tag in (("ambuja", "amb"), ("acc", "acc")):
        p = m.ppa[e]
        s.section(f"{e.upper()} — fair value of identifiable net assets")
        keys = list(p["step_ups"].keys())
        s.calc(f"{tag}_su_gross", "Gross fair-value step-ups", "+".join("{su_%s_%s}" % (e, k) for k in keys), CR, p["gross_step_up"])
        s.calc(f"{tag}_dtl", "Deferred tax liability on step-ups", f"{{{tag}_su_gross}}*{{tax}}", CR, p["deferred_tax_liability"])
        s.calc(f"{tag}_book_eq", "Book equity 31-Dec-2021", f"{{{tag}_share_capital}}+{{{tag}_reserves}}", CR, p["book_equity"])
        if e == "ambuja":
            s.calc("amb_inv_elim", "Less: investments eliminated (ACC stake valued separately)", "{amb_investments}", CR, p["investment_eliminated"])
            s.calc("amb_fv", "FV of identifiable net assets (Ambuja ex-ACC)", "{amb_book_eq}-{amb_inv_elim}+{amb_su_gross}-{amb_dtl}", CR, p["fv_net_identifiable_assets"], bold=True)
        else:
            s.calc("acc_fv", "FV of identifiable net assets (ACC)", "{acc_book_eq}+{acc_su_gross}-{acc_dtl}", CR, p["fv_net_identifiable_assets"], bold=True)
        s.calc(f"{tag}_amort", "Annual amortisation of step-ups",
               f"{{su_{e}_ppe}}/{{life_ppe}}+(" + "+".join("{su_%s_%s}" % (e, k) for k in FINITE_INTANGIBLES) + ")/{life_int}",
               CR, p["annual_amortisation"])
        s.blank()

    g = m.goodwill
    s.section("Goodwill (look-through)")
    s.calc("acc_eq_offer", "ACC 100% equity at offer price", "{acc_sh}*{acc_px}", CR, g["acc_equity_value_at_offer_100pct"])
    s.calc("acc_in_amb", "ACC value embedded in Ambuja shares bought", "{own_amb}*{amb_in_acc}*{acc_eq_offer}", CR, g["acc_value_in_ambuja_purchase"])
    s.calc("c_amb_ex", "Consideration attributable to Ambuja ex-ACC", "{v_hamb}+{v_ooamb}-{acc_in_amb}", CR, g["consideration_ambuja_ex_acc"])
    s.calc("c_acc_lt", "Consideration attributable to ACC (look-through)", "{acc_in_amb}+{v_hacc}+{v_ooacc}", CR, g["consideration_acc_lookthrough"])
    s.calc("sh_fv_amb", "Adani share of Ambuja FV net assets", "{own_amb}*{amb_fv}", CR, g["adani_share_fv_ambuja"])
    s.calc("sh_fv_acc", "Adani share of ACC FV net assets", "{own_acc_lt}*{acc_fv}", CR, g["adani_share_fv_acc"])
    s.calc("gw_amb", "Goodwill — Ambuja", "{c_amb_ex}-{sh_fv_amb}", CR, g["ambuja_goodwill"])
    s.calc("gw_acc", "Goodwill — ACC", "{c_acc_lt}-{sh_fv_acc}", CR, g["acc_goodwill"])
    s.calc("goodwill", "Total goodwill", "{gw_amb}+{gw_acc}", CR, g["total_goodwill"], bold=True)
    s.calc("gw_pct", "Goodwill as % of consideration", "{goodwill}/{consideration}", PCT, g["goodwill_pct_of_consideration"] / 100)
    s.calc("new_intang", "New intangibles recognised (incl. brands)",
           "+".join("{su_%s_%s}" % (e, k) for e in ENTITIES for k in FINITE_INTANGIBLES + ("brand",)), CR, g["new_intangibles"])


def _projections(b, m):
    s = b.sheet("Projections", years=m.years, base_label="CY2021A")
    s.title("Standalone projections", "Ambuja excludes dividends from ACC (intra-group). Cash, interest expense and D&A % of revenue held at CY2021 levels.")
    p = m.proj
    s.section("Treasury yield (derived)")
    s.calc("acc_div_amb21", "ACC dividend received by Ambuja in CY2021", "{acc_dps21}*{acc_sh}*{amb_in_acc}", CR, p["acc_dividend_in_ambuja_cy2021"])
    s.calc("tyield", "Treasury yield on cash", "({amb_oi21}-{acc_div_amb21}+{acc_oi21})/({amb_cash}+{acc_cash})", PCT2, p["treasury_yield_pct"] / 100)
    s.blank()
    for e, tag in (("ambuja", "amb"), ("acc", "acc")):
        pe = p[e]
        s.section(f"{e.upper()} standalone", year_header=True)
        s.ycalc(f"{tag}_rev", "Revenue", f"{{{tag}_rev.prev}}*(1+{{{tag}_g}})", CR, pe["revenue"], base=f"{{{tag}_rev21}}")
        s.ycalc(f"{tag}_ebitda", "EBITDA", f"{{{tag}_rev}}*{{{tag}_m}}", CR, pe["ebitda"])
        s.ycalc(f"{tag}_da", "Depreciation & amortisation", f"{{{tag}_rev}}*{{{tag}_da21}}/{{{tag}_rev21}}", CR, pe["depreciation"])
        s.ycalc(f"{tag}_ti", "Treasury income", f"{{tyield}}*{{{tag}_cash}}", CR, pe["treasury_income"])
        s.ycalc(f"{tag}_ie", "Interest expense", f"{{{tag}_int21}}", CR, pe["interest_expense"])
        s.ycalc(f"{tag}_pbt", "Profit before tax", f"{{{tag}_ebitda}}-{{{tag}_da}}+{{{tag}_ti}}-{{{tag}_ie}}", CR, pe["pbt"])
        s.ycalc(f"{tag}_ni", "Net income", f"{{{tag}_pbt}}*(1-{{tax}})", CR, pe["net_income"], bold=True)
        s.blank()
    dv = p["dividends"]
    s.section("Dividends", year_header=True)
    s.ycalc("acc_div", "ACC dividends paid", "{payout}*{acc_ni}", CR, dv["acc_total"])
    s.ycalc("acc_div_to_amb", "  of which to Ambuja", "{acc_div}*{amb_in_acc}", CR, dv["acc_to_ambuja"])
    s.ycalc("amb_div", "Ambuja dividends paid (ACC dividends passed through, s.80M)", "{payout}*({amb_ni}+{acc_div_to_amb})", CR, dv["ambuja_total"])


def _synergies(b, m):
    s = b.sheet("Synergies", years=m.years, base_label="Run-rate")
    s.title("Synergies", "[ASSUMPTION] Model estimates, not company guidance. Edit run-rates and phasing here.")
    sy = m.syn
    s.section("Phasing (% of run-rate)", year_header=True)
    items = list(m.inp["synergies"]["items"].items())
    for k, it in items:
        s.yinp(f"ph_{k}", it["label"], [x / 100 for x in it["phasing_pct"]], PCT, base=it["run_rate"])
    s.blank()
    s.section("Pre-tax synergies (EBITDA)", year_header=True)
    for k, it in items:
        s.ycalc(f"syn_{k}", it["label"], f"{{ph_{k}.base}}*{{ph_{k}}}", CR, sy["items"][k]["by_year"], base=f"{{ph_{k}.base}}")
    s.ycalc("syn", "Total synergies", "+".join("{syn_%s}" % k for k, _ in items), CR, sy["pretax_by_year"], bold=True,
            base="+".join("{syn_%s.base}" % k for k, _ in items))
    s.yinp("cta_ph", "Costs to achieve phasing", [x / 100 for x in m.inp["synergies"]["costs_to_achieve_phasing_pct"]], PCT,
           base=m.inp["synergies"]["costs_to_achieve"])
    s.ycalc("cta", "Costs to achieve (one-off, pre-tax)", "{cta_ph.base}*{cta_ph}", CR, sy["costs_to_achieve_by_year"])
    s.blank()
    s.section("NPV at the unlevered cost of capital", year_header=True)
    s.ycalc("disc", "Discount factor", ["(1+{ku})^1", "(1+{ku})^2", "(1+{ku})^3"], NUM4, recon=False)
    s.ycalc("pv_syn", "PV of after-tax synergies", "{syn}*(1-{tax})/{disc}", CR, sy["pv_by_year"])
    s.ycalc("pv_cta", "PV of after-tax costs to achieve", "{cta}*(1-{tax})/{disc}", CR)
    s.calc("pv_tv", "PV of terminal value (run-rate after tax, growing)", "{syn.base}*(1-{tax})*(1+{g_syn})/({ku}-{g_syn})/{disc.Y3}", CR, sy["pv_terminal"])
    s.calc("npv_gross", "Gross synergy NPV", "SUM({pv_syn.range})+{pv_tv}", CR, sy["gross_npv"])
    s.calc("pv_cta_tot", "Less: PV of costs to achieve", "SUM({pv_cta.range})", CR, sy["pv_costs_to_achieve_after_tax"])
    s.calc("npv_net", "Net synergy NPV", "{npv_gross}-{pv_cta_tot}", CR, sy["net_npv"], bold=True)
    s.calc("tv_share", "Terminal value share of gross NPV", "{pv_tv}/{npv_gross}", PCT, sy["terminal_value_share_pct"] / 100)


def _pro_forma(b, m):
    s = b.sheet("Pro Forma & Returns", years=m.years)
    s.title("Pro forma earnings, holdco cash and returns")
    pf = {k: [r[k] for r in m.pf] for k in m.pf[0] if k != "year"}
    rt = {k: [r[k] for r in m.returns] for k in m.returns[0] if k != "year"}

    s.section("Consolidated income statement (100%)", year_header=True)
    s.ycalc("pf_rev", "Revenue (Ambuja + ACC)", "{amb_rev}+{acc_rev}", CR, pf["combined_revenue"])
    s.ycalc("pf_ebitda", "EBITDA incl. synergies, less costs to achieve", "{amb_ebitda}+{acc_ebitda}+{syn}-{cta}", CR, pf["ebitda"])
    s.ycalc("ppa_amb_y", "PPA amortisation — Ambuja (incl. inventory in Year 1)",
            ["{amb_amort}+{su_ambuja_inventory}", "{amb_amort}", "{amb_amort}"], CR)
    s.ycalc("ppa_acc_y", "PPA amortisation — ACC (incl. inventory in Year 1)",
            ["{acc_amort}+{su_acc_inventory}", "{acc_amort}", "{acc_amort}"], CR)
    s.ycalc("pf_da", "D&A incl. PPA", "{amb_da}+{acc_da}+{ppa_amb_y}+{ppa_acc_y}", CR,
            [a + c for a, c in zip(pf["standalone_da"], pf["ppa_amortisation"])])
    s.ycalc("pf_ti", "Treasury income", "{amb_ti}+{acc_ti}", CR, pf["treasury_income"])
    s.ycalc("pf_tie", "Target interest expense", "{amb_ie}+{acc_ie}", CR, pf["target_interest"])
    s.ycalc("hc_int", "Holdco acquisition interest",
            ["{term0}*{term_rate}+{bridge0}*{bridge_rate}", "{hc_open}*{refi_rate}", "{hc_open}*{refi_rate}"], CR, pf["holdco_interest"])
    s.ycalc("pf_pbt", "Profit before tax", "{pf_ebitda}-{pf_da}+{pf_ti}-{pf_tie}-{hc_int}", CR, pf["pbt"])
    s.ycalc("hc_int_at", "Holdco interest after any tax shield", "{hc_int}*(1-{tax}*{deductible})", CR, pf["holdco_interest_after_shield"])
    s.ycalc("pf_tax", "Tax (no shield on holdco interest unless deductible)", "({pf_pbt}+{hc_int})*{tax}-{hc_int}*{tax}*{deductible}", CR, pf["tax"])
    s.ycalc("pf_ni", "Consolidated net income", "{pf_pbt}-{pf_tax}", CR, pf["consolidated_net_income"], bold=True)
    s.blank()

    s.section("Attribution to Adani", year_header=True)
    s.ycalc("blend", "Adani share of synergies (EBITDA-weighted look-through)",
            "({own_amb}*{amb_ebitda}+{own_acc_lt}*{acc_ebitda})/({amb_ebitda}+{acc_ebitda})", PCT2,
            [x / 100 for x in pf["blended_ownership_pct"]])
    s.ycalc("att_base", "Share of standalone net income", "{own_amb}*{amb_ni}+{own_acc_lt}*{acc_ni}", CR)
    s.ycalc("att_syn", "Share of synergies after tax", "{blend}*{syn}*(1-{tax})", CR, pf["attributable_synergies_after_tax"])
    s.ycalc("att_cta", "Share of costs to achieve after tax", "{blend}*{cta}*(1-{tax})", CR, pf["attributable_costs_to_achieve_after_tax"])
    s.ycalc("att_ppa", "Share of PPA amortisation after tax", "({own_amb}*{ppa_amb_y}+{own_acc_lt}*{ppa_acc_y})*(1-{tax})", CR, pf["attributable_ppa_after_tax"])
    s.ycalc("att_ni", "Adani-attributable net income", "{att_base}+{att_syn}-{att_cta}-{att_ppa}-{hc_int_at}", CR, pf["attributable_net_income"], bold=True)
    s.ycalc("nci_ni", "Non-controlling interests' share", "{pf_ni}-{att_ni}", CR, pf["nci_net_income"])
    s.blank()

    s.section("Holdco cash and debt", year_header=True)
    s.ycalc("div_recv", "Dividends received, net of withholding tax",
            "{own_amb}*{amb_div}*(1-{wht_amb})+{own_acc_direct}*{acc_div}*(1-{wht_acc})", CR, pf["dividends_received_net"])
    s.ycalc("hc_cf", "Holdco cash flow (dividends − interest)", "{div_recv}-{hc_int_at}", CR, pf["holdco_cash_flow"])
    s.ycalc("div_cover", "Dividend / interest cover", "{div_recv}/{hc_int_at}", MULT2, pf["dividend_interest_cover"])
    s.ycalc("top_up", "Sponsor top-up needed", "MAX(-{hc_cf},0)", CR, pf["sponsor_top_up"])
    s.ycalc("repay", "Debt repaid from surplus", "MAX({hc_cf},0)", CR, pf["debt_repayment"])
    s.ycalc("hc_open", "Holdco debt — opening", ["{acq_debt}", "{hc_close.prev}", "{hc_close.prev}"], CR, pf["holdco_debt_open"])
    s.ycalc("hc_close", "Holdco debt — closing", "{hc_open}-{repay}", CR, pf["holdco_debt_close"])
    s.ycalc("eq_open", "Sponsor equity invested — opening", ["{sponsor_eq}", "{eq_open.prev}+{top_up.prev}", "{eq_open.prev}+{top_up.prev}"],
            CR, pf["sponsor_equity_open"])
    s.blank()

    s.section("Returns", year_header=True)
    s.ycalc("roe", "Return on sponsor equity (attributable NI / equity invested)", "{att_ni}/{eq_open}", PCT, [x / 100 for x in rt["roe_pct"]])
    s.ycalc("ke_y", "Levered cost of equity", "{ke}", PCT, recon=False)
    s.ycalc("cash_earn", "Cash earnings before acquisition financing", "{att_ni}+{hc_int_at}+{att_ppa}+{att_cta}", CR, rt["cash_earnings_pre_financing"])
    s.ycalc("roic", "Cash ROIC on total investment", "{cash_earn}/{total_uses}", PCT2, [x / 100 for x in rt["cash_roic_pct"]], bold=True)
    s.ycalc("ku_y", "Unlevered cost of capital", "{ku}", PCT2, recon=False)
    s.ycalc("be_syn", "Breakeven in-year synergies for ROIC = cost of capital",
            "MAX(0,({ku}*{total_uses}-({cash_earn}-{att_syn}))/({blend}*(1-{tax})))", CR, rt["breakeven_synergies_for_roic"])
    s.blank()

    v = m.value
    s.section("Value creation: Adani's share of synergy NPV vs premium paid")
    s.calc("adani_npv", "Adani share of net synergy NPV (final-year look-through weight)", "{blend.Y3}*{npv_net}", CR, v["adani_share_of_net_synergy_npv"])
    s.calc("hurdle", "Premium paid + transaction costs", "{prem_paid}+{txn_costs}", CR, v["premium_plus_costs"])
    s.calc("value_created", "Net value created for Adani", "{adani_npv}-{hurdle}", CR, v["net_value_created"], bold=True)
    s.calc("be_rr", "Breakeven run-rate synergies", "({hurdle}/{blend.Y3}+{pv_cta_tot})/({npv_gross}/{syn.base})", CR, v["breakeven_run_rate_synergies"])


def _balance_sheet(b, m):
    s = b.sheet("Balance Sheet")
    s.title("Pro forma balance sheet at close", "31-Dec-2021 audited balance sheets used as the closing proxy.")
    bs = m.bs
    A, L, E = bs["assets"], bs["liabilities"], bs["equity"]
    s.section("Assets")
    s.calc("bs_fa", "Fixed assets & CWIP (incl. PP&E step-up)", "{amb_fixed_assets}+{amb_cwip}+{acc_fixed_assets}+{acc_cwip}+{su_ambuja_ppe}+{su_acc_ppe}", CR, A["fixed_assets_and_cwip"])
    s.calc("bs_int", "Acquired intangibles", "{new_intang}", CR, A["acquired_intangibles"])
    s.calc("bs_gw", "Goodwill", "{goodwill}", CR, A["goodwill"])
    s.calc("bs_inv", "Inventories (incl. step-up)", "{amb_inventories}+{acc_inventories}+{su_ambuja_inventory}+{su_acc_inventory}", CR, A["inventories"])
    s.calc("bs_rec", "Trade receivables", "{amb_trade_receivables}+{acc_trade_receivables}", CR, A["trade_receivables"])
    s.calc("bs_cash", "Cash (targets; holdco holds none)", "{amb_cash}+{acc_cash}", CR, A["cash"])
    s.calc("bs_invst", "Investments (Ambuja's ACC stake eliminated)", "{acc_investments}", CR, A["investments"])
    s.calc("bs_oa", "Other assets", "{amb_other_assets}+{acc_other_assets}", CR, A["other_assets"])
    s.calc("bs_ta", "Total assets", "{bs_fa}+{bs_int}+{bs_gw}+{bs_inv}+{bs_rec}+{bs_cash}+{bs_invst}+{bs_oa}", CR, bs["total_assets"], bold=True)
    s.blank()
    s.section("Liabilities and equity")
    s.calc("bs_acq", "Acquisition debt (holdco)", "{acq_debt}", CR, L["acquisition_debt"])
    s.calc("bs_tb", "Target borrowings & leases", "{amb_borrowings}+{acc_borrowings}", CR, L["target_borrowings_and_leases"])
    s.calc("bs_dtl", "Deferred tax on step-ups", "{amb_dtl}+{acc_dtl}", CR, L["deferred_tax_on_step_ups"])
    s.calc("bs_ol", "Other liabilities", "{amb_other_liabilities}+{acc_other_liabilities}", CR, L["other_liabilities"])
    s.calc("bs_adani_eq", "Adani equity (sponsor equity less expensed costs)", "{sponsor_eq}-{txn_costs}", CR, E["adani_equity"])
    s.calc("bs_nci", "Non-controlling interests", "(1-{own_amb})*{amb_fv}+(1-{own_acc_lt})*{acc_fv}", CR, E["non_controlling_interests"])
    s.calc("bs_tle", "Total liabilities & equity", "{bs_acq}+{bs_tb}+{bs_dtl}+{bs_ol}+{bs_adani_eq}+{bs_nci}", CR, bs["total_liabilities_and_equity"], bold=True)
    s.blank()
    cr = bs["credit_at_close"]
    s.section("Credit metrics at close")
    s.calc("gross_debt", "Consolidated gross debt", "{bs_acq}+{bs_tb}", CR, cr["gross_debt"])
    s.calc("gd_ebitda", "Gross debt / CY2021 EBITDA", "{gross_debt}/({amb_ebitda21}+{acc_ebitda21})", MULT, cr["gross_debt_to_ebitda"])
    s.calc("nd_ebitda", "Net debt / CY2021 EBITDA", "({gross_debt}-{bs_cash})/({amb_ebitda21}+{acc_ebitda21})", MULT, cr["net_debt_to_ebitda"])
    s.calc("ltv_cost", "Holdco loan-to-value at cost", "{acq_debt}/{consideration}", PCT, cr["holdco_ltv_at_cost_pct"] / 100)
    s.calc("ltv_mkt", "Holdco loan-to-value at completion-day market prices", "{acq_debt}/{mv_completion}", PCT, cr["holdco_ltv_at_completion_market_pct"] / 100)


def _precedents(b, m):
    s = b.sheet("Precedents")
    s.title("Precedent transactions — Indian cement (announced before May-2022)",
            "EV/tonne is the sector benchmark. Most precedents were asset or unlisted deals, so control premiums are not comparable; EV/EBITDA was not reliably disclosed.")
    ws = s.ws
    heads = ["Date", "Acquirer", "Target", "Capacity (MTPA)", "EV (₹ Cr)", "INR/USD", "EV/t (₹)", "EV/t (US$)", "Note", "Source"]
    for i, h in enumerate(heads):
        c = ws.cell(s.row, 2 + i, h)
        c.font, c.fill = F_BOLD, FILL_HEAD
    for col, w in zip("BCDEFGHIJK", [10, 24, 32, 14, 12, 10, 12, 12, 40, 60]):
        ws.column_dimensions[col].width = w
    s.row += 1
    first = s.row
    for p in m.precedents["rows"]:
        r = s.row
        for i, v in enumerate([p["date"], p["acquirer"], p["target"]]):
            ws.cell(r, 2 + i, v)
        for i, (v, fmt) in enumerate([(p["capacity_mtpa"], CR1), (p["ev_cr"], CR), (p["inr_per_usd"], NUM2)]):
            c = ws.cell(r, 5 + i, v)
            c.font, c.fill, c.number_format = F_INPUT, FILL_INPUT, fmt
        ws.cell(r, 8, f"=F{r}*10/E{r}").number_format = CR
        ws.cell(r, 9, f"=H{r}/G{r}").number_format = CR
        ws.cell(r, 10, p["note"])
        ws.cell(r, 11, p["source_text"]).font = F_NOTE
        s.row += 1
    last = s.row - 1
    s.blank()
    clean = [first + i for i, p in enumerate(m.precedents["rows"]) if not p["distressed"]]
    clean_refs = ",".join(f"I{r}" for r in clean)
    pr = m.precedents
    s.calc("prec_mean", "Mean EV/t (US$), all", f"AVERAGE(I{first}:I{last})", CR, pr["mean_usd_per_t"])
    s.calc("prec_median", "Median EV/t (US$), all", f"MEDIAN(I{first}:I{last})", CR, pr["median_usd_per_t"])
    s.calc("prec_median_clean", "Median EV/t (US$), excluding distressed", f"MEDIAN({clean_refs})", CR, pr["median_usd_per_t_ex_distressed"])
    s.calc("prec_this", "This deal EV/t (US$)", "{ev_t_usd}", CR, pr["this_deal_usd_per_t"])
    s.calc("prec_prem", "This deal vs median (ex-distressed)", "{prec_this}/{prec_median_clean}-1", PCT,
           pr["this_deal_premium_to_median_ex_distressed_pct"] / 100)


def _sensitivity(b, m):
    s = b.sheet("Sensitivity")
    s.title("Sensitivity analysis — STATIC OUTPUT FROM PYTHON",
            "Each cell is a full re-run of the Python model with the stated input changed (python run_model.py regenerates this tab).")
    sens = m.sensitivity
    fy = sens["final_year"]
    ws = s.ws

    def table(title, heads, rows, fmts):
        s.section(title)
        for i, h in enumerate(heads):
            c = ws.cell(s.row, 2 + i, h)
            c.font, c.fill = F_BOLD, FILL_HEAD
            if isinstance(h, (int, float)):
                c.number_format = '"₹"#,##0'
        s.row += 1
        for r in rows:
            for i, (v, f) in enumerate(zip(r, fmts)):
                c = ws.cell(s.row, 2 + i, v)
                c.number_format = f
            s.row += 1
        s.blank()

    for col in "CDEFGHIJ":
        ws.column_dimensions[col].width = 15
    table(f"Offer price (both companies) — {fy}",
          ["Price vs actual", "Ambuja price (₹)", "Ambuja premium", "Consideration", "Sponsor equity", "Goodwill", "Cash ROIC", "ROE", "Value created"],
          [[r["price_multiplier"], r["ambuja_offer_price"], r["ambuja_premium_pct"] / 100, r["total_consideration"], r["sponsor_equity"],
            r["goodwill"], r["cash_roic_final_year_pct"] / 100, r["roe_final_year_pct"] / 100, r["net_value_created"]] for r in sens["offer_price"]],
          ['0%', NUM2, PCT, CR, CR, CR, PCT2, PCT, CR])
    table(f"Holdco refinancing rate — {fy}",
          ["Refi rate", "Holdco interest", "Attributable NI", "ROE", "Dividend / interest"],
          [[r["refi_rate_pct"] / 100, r["holdco_interest_final_year"], r["attributable_ni_final_year"], r["roe_final_year_pct"] / 100,
            r["dividend_interest_cover_final_year"]] for r in sens["refi_rate"]],
          [PCT2, CR, CR, PCT, MULT2])
    table(f"EBITDA margin (both companies, all years) — {fy}",
          ["Change (bp)", "Cash ROIC", "ROE"],
          [[r["margin_change_bp"], r["cash_roic_final_year_pct"] / 100, r["roe_final_year_pct"] / 100] for r in sens["ebitda_margin"]],
          ["0", PCT2, PCT])
    table(f"Holdco interest tax shield — {fy}",
          ["Deductible?", "Attributable NI", "ROE", "Levered Ke"],
          [["Yes" if r["interest_tax_deductible"] else "No", r["attributable_ni_final_year"], r["roe_final_year_pct"] / 100,
            r["levered_cost_of_equity_pct"] / 100] for r in sens["interest_tax_shield"]],
          ["@", CR, PCT, PCT])
    lv = sens["synergy_levels"]
    for title, key, fmt, scale in (("Net value created for Adani (₹ Cr): offer price × run-rate synergies", "matrix_net_value_created", CR, 1),
                                   (f"Cash ROIC {fy}: offer price × run-rate synergies", "matrix_cash_roic_final_year", PCT2, 100)):
        table(title, ["Price \\ Synergies"] + list(lv),
              [[r["price_multiplier"]] + [r[str(x)] / scale for x in lv] for r in sens[key]],
              ['0%'] + [fmt] * len(lv))


def _checks(b, m):
    s = b.sheet("Checks")
    s.title("Checks", "Integrity checks (formulas) and Python reconciliation. Every row should read OK.")
    ws = s.ws
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 10
    s.section("Integrity checks")
    checks = [
        ("Balance sheet balances", "ABS({bs_ta}-{bs_tle})<1"),
        ("Sources = uses", "ABS({total_sources}-{total_uses})<1"),
        ("Sponsor equity is positive", "{sponsor_eq}>0"),
        ("Look-through consideration = consideration paid", "ABS({c_amb_ex}+{c_acc_lt}-{consideration})<1"),
        ("Ownership ties to Adani release: Ambuja (±0.05pp)", "ABS({own_amb}-{rep_amb_pct})<0.0005"),
        ("Ownership ties to Adani release: ACC (±0.05pp)", "ABS({own_acc_ctrl}-{rep_acc_pct})<0.0005"),
        ("Consideration within 3% of reported US$6.5bn", "ABS({consideration_usd}/{rep_usd}-1)<0.03"),
        ("Goodwill positive for both entities", "AND({gw_amb}>0,{gw_acc}>0)"),
        ("Attributable + NCI = consolidated NI (all years)", "ABS(SUM({att_ni.range})+SUM({nci_ni.range})-SUM({pf_ni.range}))<1"),
    ]
    start = s.row
    for label, f in checks:
        ws.cell(s.row, 2, label)
        ws.cell(s.row, 3, b.resolve(f"IF({f},\"OK\",\"FAIL\")", "Checks", "C"))
        s.row += 1
    integrity_end = s.row - 1
    s.blank()

    s.section("Python reconciliation (formula value vs Python model)")
    for i, h in enumerate(["Item", "Year", "Excel formula", "Python", "Status"]):
        c = ws.cell(s.row, 2 + i, h)
        c.font, c.fill = F_BOLD, FILL_HEAD
    s.row += 1
    recon_start = s.row
    for key, label, py, fmt in b.recon:
        r = b.refs[key]
        vals = py if isinstance(py, list) else [py]
        for i, v in enumerate(vals):
            if v is None:
                continue
            if r["kind"] == "scalar":
                ref, yr = f"'{r['sheet']}'!$C${r['row']}", ""
            else:
                ref, yr = f"'{r['sheet']}'!${YEAR_COLS[i]}${r['row']}", m.years[i]
            ws.cell(s.row, 2, label)
            ws.cell(s.row, 3, yr)
            c = ws.cell(s.row, 4, f"={ref}")
            c.number_format = fmt
            c = ws.cell(s.row, 5, float(v))
            c.number_format = fmt
            tol = "0.000001" if fmt in (PCT, PCT2, NUM4, MULT, MULT2, NUM2) else "0.5"
            ws.cell(s.row, 6, f"=IF(ABS(D{s.row}-E{s.row})<{tol},\"OK\",\"DIFF\")")
            s.row += 1
    recon_end = s.row - 1
    for col, w in zip("BCDEF", [58, 10, 16, 16, 10]):
        ws.column_dimensions[col].width = w

    ws.cell(3, 2, "OVERALL STATUS").font = F_BOLD
    ws.cell(3, 3, f'=IF(AND(COUNTIF(C{start}:C{integrity_end},"OK")={integrity_end - start + 1},'
                  f'COUNTIF(F{recon_start}:F{recon_end},"OK")={recon_end - recon_start + 1}),"ALL CHECKS OK","CHECK FAILURES")').font = F_BOLD
