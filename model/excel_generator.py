"""
Professional Excel Workbook Generator
======================================
Generates a multi-tab, IB-formatted Excel model with:
- Color-coded inputs (blue) vs. calculations (black)
- Proper number formatting, borders, and headers
- Professional IB-style layout conventions
"""

import os
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter

from model.assumptions import (
    TRANSACTION, AMBUJA_SHARES, ACC_SHARES,
    AMBUJA_INCOME_STATEMENT, ACC_INCOME_STATEMENT,
    AMBUJA_BALANCE_SHEET, ACC_BALANCE_SHEET,
    FINANCING, SYNERGY_ASSUMPTIONS, VALUATION_METRICS,
    PRECEDENT_TRANSACTIONS, PREMIUM_ANALYSIS,
)


# ==============================================================================
# STYLE DEFINITIONS (IB Convention)
# ==============================================================================

# Fonts
FONT_TITLE = Font(name="Calibri", size=14, bold=True, color="1F3864")
FONT_SECTION = Font(name="Calibri", size=11, bold=True, color="1F3864")
FONT_HEADER = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
FONT_SUBHEADER = Font(name="Calibri", size=10, bold=True, color="1F3864")
FONT_INPUT = Font(name="Calibri", size=10, color="0000FF")       # Blue = input
FONT_CALC = Font(name="Calibri", size=10, color="000000")        # Black = formula
FONT_LABEL = Font(name="Calibri", size=10, color="333333")
FONT_TOTAL = Font(name="Calibri", size=10, bold=True, color="000000")
FONT_POSITIVE = Font(name="Calibri", size=10, bold=True, color="006100")
FONT_NEGATIVE = Font(name="Calibri", size=10, bold=True, color="9C0006")
FONT_SMALL = Font(name="Calibri", size=9, italic=True, color="666666")

# Fills
FILL_HEADER = PatternFill(start_color="1F3864", end_color="1F3864", fill_type="solid")
FILL_SUBHEADER = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
FILL_INPUT = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
FILL_TOTAL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
FILL_HIGHLIGHT = PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid")
FILL_ACCRETIVE = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
FILL_DILUTIVE = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
FILL_LIGHT_GRAY = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")
FILL_WHITE = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

# Borders
THIN_BORDER = Border(
    left=Side(style="thin", color="B0B0B0"),
    right=Side(style="thin", color="B0B0B0"),
    top=Side(style="thin", color="B0B0B0"),
    bottom=Side(style="thin", color="B0B0B0"),
)
BOTTOM_BORDER = Border(bottom=Side(style="medium", color="1F3864"))
DOUBLE_BOTTOM = Border(bottom=Side(style="double", color="1F3864"))

# Alignment
ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")

# Number formats
FMT_NUMBER = '#,##0'
FMT_DECIMAL = '#,##0.0'
FMT_PCT = '0.0%'
FMT_EPS = '#,##0.00'
FMT_CURRENCY = '₹#,##0'


def _set_col_widths(ws, widths):
    """Set column widths from a dict {col_letter: width}."""
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def _write_row(ws, row, data, fonts=None, fills=None, borders=None,
               alignments=None, number_formats=None):
    """Write a row of data with optional formatting."""
    for col_idx, value in enumerate(data, 1):
        cell = ws.cell(row=row, column=col_idx, value=value)
        if fonts and col_idx <= len(fonts) and fonts[col_idx - 1]:
            cell.font = fonts[col_idx - 1]
        if fills and col_idx <= len(fills) and fills[col_idx - 1]:
            cell.fill = fills[col_idx - 1]
        if borders and col_idx <= len(borders) and borders[col_idx - 1]:
            cell.border = borders[col_idx - 1]
        if alignments and col_idx <= len(alignments) and alignments[col_idx - 1]:
            cell.alignment = alignments[col_idx - 1]
        if number_formats and col_idx <= len(number_formats) and number_formats[col_idx - 1]:
            cell.number_format = number_formats[col_idx - 1]


def _write_header_row(ws, row, headers, start_col=1):
    """Write a formatted header row."""
    for col_idx, header in enumerate(headers, start_col):
        cell = ws.cell(row=row, column=col_idx, value=header)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = THIN_BORDER


def _write_section_header(ws, row, title, num_cols=8):
    """Write a section header spanning multiple columns."""
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=num_cols)
    cell = ws.cell(row=row, column=1, value=title)
    cell.font = FONT_SECTION
    cell.fill = FILL_SUBHEADER
    cell.alignment = ALIGN_LEFT
    cell.border = BOTTOM_BORDER


def _write_data_row(ws, row, label, values, is_input=False, is_total=False,
                    is_pct=False, is_eps=False, label_indent=0):
    """Write a formatted data row with label and values."""
    indent = "  " * label_indent
    cell = ws.cell(row=row, column=1, value=f"{indent}{label}")
    cell.font = FONT_TOTAL if is_total else FONT_LABEL
    cell.alignment = ALIGN_LEFT
    if is_total:
        cell.fill = FILL_TOTAL
        cell.border = BOTTOM_BORDER

    for col_idx, val in enumerate(values, 2):
        cell = ws.cell(row=row, column=col_idx, value=val)
        cell.alignment = ALIGN_RIGHT

        if is_total:
            cell.font = FONT_TOTAL
            cell.fill = FILL_TOTAL
            cell.border = DOUBLE_BOTTOM
        elif is_input:
            cell.font = FONT_INPUT
            cell.fill = FILL_INPUT
        else:
            cell.font = FONT_CALC

        if is_pct:
            cell.number_format = '0.0%' if isinstance(val, float) and abs(val) < 1 else '0.0\\%'
        elif is_eps:
            cell.number_format = FMT_EPS
        elif isinstance(val, (int, float)):
            cell.number_format = FMT_NUMBER
        cell.border = THIN_BORDER


# ==============================================================================
# WORKBOOK GENERATION
# ==============================================================================

def generate_excel_model(model, output_path):
    """Generate the complete Excel workbook from the merger model."""
    wb = Workbook()

    # Remove default sheet
    wb.remove(wb.active)

    # Create all tabs
    _create_transaction_summary(wb, model)
    _create_acquirer_financials(wb)
    _create_target_financials(wb)
    _create_ppa_tab(wb, model)
    _create_pro_forma_tab(wb, model)
    _create_synergy_tab(wb, model)
    _create_accretion_dilution_tab(wb, model)
    _create_sensitivity_tab(wb, model)
    _create_precedents_tab(wb)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"\n✅ Excel model saved: {output_path}")
    return output_path


# ==============================================================================
# TAB 1: TRANSACTION SUMMARY
# ==============================================================================

def _create_transaction_summary(wb, model):
    ws = wb.create_sheet("1. Transaction Summary")
    _set_col_widths(ws, {"A": 35, "B": 20, "C": 20, "D": 20, "E": 20, "F": 18})

    row = 1
    ws.merge_cells("A1:F1")
    cell = ws.cell(row=1, column=1, value="TRANSACTION SUMMARY")
    cell.font = FONT_TITLE
    cell.alignment = ALIGN_LEFT
    row = 2
    ws.cell(row=2, column=1, value="Adani Group Acquisition of Ambuja Cements & ACC Ltd").font = FONT_SMALL

    # Deal Overview
    row = 4
    _write_section_header(ws, row, "DEAL OVERVIEW", 6)

    details = [
        ("Acquirer", TRANSACTION["acquirer"]),
        ("Target Companies", f"{TRANSACTION['target_1']} & {TRANSACTION['target_2']}"),
        ("Seller", TRANSACTION["seller"]),
        ("Announcement Date", TRANSACTION["announcement_date"]),
        ("Completion Date", TRANSACTION["completion_date"]),
        ("Sector", TRANSACTION["sector"]),
        ("Currency", TRANSACTION["currency"]),
    ]
    for i, (label, value) in enumerate(details):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=label).font = FONT_LABEL
        ws.cell(row=r, column=2, value=value).font = FONT_INPUT
        ws.cell(row=r, column=1).border = THIN_BORDER
        ws.cell(row=r, column=2).border = THIN_BORDER

    # Purchase Price Breakdown
    row = row + len(details) + 2
    _write_section_header(ws, row, "PURCHASE PRICE BREAKDOWN (₹ Crores)", 6)
    row += 1
    _write_header_row(ws, row, ["Component", "Shares (Cr)", "Price/Share (₹)", "Value (₹ Cr)", "% of Total"])

    pp = model.purchase_price
    total = pp["total_cash_outlay"]
    pp_rows = [
        ("Holcim Stake — 63.15% of Ambuja", pp["ambuja_holcim_shares_cr"],
         AMBUJA_SHARES["offer_price_per_share"], pp["ambuja_holcim_value"],
         pp["ambuja_holcim_value"] / total * 100),
        ("Ambuja Open Offer (5.63% acceptance)", pp["ambuja_oo_shares_tendered_cr"],
         AMBUJA_SHARES["offer_price_per_share"], pp["ambuja_oo_value"],
         pp["ambuja_oo_value"] / total * 100),
        ("ACC Open Offer (4.89% acceptance)", pp["acc_oo_shares_tendered_cr"],
         ACC_SHARES["offer_price_per_share"], pp["acc_oo_value"],
         pp["acc_oo_value"] / total * 100),
        ("Transaction Costs", "", "", pp["transaction_costs"],
         pp["transaction_costs"] / total * 100),
    ]
    for i, (label, shares, price, value, pct) in enumerate(pp_rows):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=label).font = FONT_LABEL
        ws.cell(row=r, column=1).border = THIN_BORDER
        for c, v in [(2, shares), (3, price), (4, value), (5, f"{pct:.1f}%")]:
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = FONT_INPUT if c in [2, 3] else FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            if isinstance(v, (int, float)):
                cell.number_format = FMT_NUMBER

    r = row + len(pp_rows) + 1
    ws.cell(row=r, column=1, value="Total Cash Outlay").font = FONT_TOTAL
    ws.cell(row=r, column=1).fill = FILL_TOTAL
    ws.cell(row=r, column=1).border = DOUBLE_BOTTOM
    for c in [2, 3]:
        ws.cell(row=r, column=c).fill = FILL_TOTAL
        ws.cell(row=r, column=c).border = DOUBLE_BOTTOM
    cell = ws.cell(row=r, column=4, value=total)
    cell.font = FONT_TOTAL
    cell.fill = FILL_TOTAL
    cell.number_format = FMT_NUMBER
    cell.border = DOUBLE_BOTTOM
    cell = ws.cell(row=r, column=5, value="100.0%")
    cell.font = FONT_TOTAL
    cell.fill = FILL_TOTAL
    cell.border = DOUBLE_BOTTOM

    # Implied Valuation
    row = r + 2
    _write_section_header(ws, row, "IMPLIED VALUATION METRICS", 6)
    row += 1
    _write_header_row(ws, row, ["Metric", "Ambuja Cements", "ACC Ltd"])

    vm = VALUATION_METRICS
    val_rows = [
        ("Implied Equity Value (100%, ₹ Cr)", vm["ambuja"]["implied_equity_value"], vm["acc"]["implied_equity_value"]),
        ("Net Debt (₹ Cr)", vm["ambuja"]["net_debt_FY2022"], vm["acc"]["net_debt_FY2022"]),
        ("Implied Enterprise Value (₹ Cr)", vm["ambuja"]["implied_ev"], vm["acc"]["implied_ev"]),
        ("EV / EBITDA (FY22)", f"{vm['ambuja']['ev_ebitda_fy22']}x", f"{vm['acc']['ev_ebitda_fy22']}x"),
        ("P / E (FY22)", f"{vm['ambuja']['pe_fy22']}x", f"{vm['acc']['pe_fy22']}x"),
        ("Cement Capacity (MTPA)", vm["ambuja"]["cement_capacity_mtpa"], vm["acc"]["cement_capacity_mtpa"]),
        ("EV / Tonne (US$)", f"${vm['ambuja']['ev_per_tonne_usd']}", f"${vm['acc']['ev_per_tonne_usd']}"),
    ]
    for i, (label, amb, acc_v) in enumerate(val_rows):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=label).font = FONT_LABEL
        ws.cell(row=r, column=1).border = THIN_BORDER
        for c, v in [(2, amb), (3, acc_v)]:
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            if isinstance(v, (int, float)):
                cell.number_format = FMT_NUMBER

    # Sources & Uses
    row = r + 2
    _write_section_header(ws, row, "SOURCES & USES (₹ Crores)", 6)
    row += 1
    _write_header_row(ws, row, ["Sources", "Amount", "", "Uses", "Amount"])

    fin = FINANCING
    sources = list(fin["sources"].items())[:-1]  # Exclude total
    uses = list(fin["uses"].items())[:-1]

    max_rows = max(len(sources), len(uses))
    for i in range(max_rows):
        r = row + 1 + i
        if i < len(sources):
            label = sources[i][0].replace("_", " ").title()
            val = sources[i][1]
            ws.cell(row=r, column=1, value=label).font = FONT_LABEL
            ws.cell(row=r, column=1).border = THIN_BORDER
            cell = ws.cell(row=r, column=2, value=val)
            cell.font = FONT_INPUT
            cell.number_format = FMT_NUMBER
            cell.border = THIN_BORDER
            cell.alignment = ALIGN_RIGHT
        if i < len(uses):
            label = uses[i][0].replace("_", " ").title()
            val = uses[i][1]
            ws.cell(row=r, column=4, value=label).font = FONT_LABEL
            ws.cell(row=r, column=4).border = THIN_BORDER
            cell = ws.cell(row=r, column=5, value=val)
            cell.font = FONT_CALC
            cell.number_format = FMT_NUMBER
            cell.border = THIN_BORDER
            cell.alignment = ALIGN_RIGHT

    r = row + max_rows + 1
    ws.cell(row=r, column=1, value="Total Sources").font = FONT_TOTAL
    ws.cell(row=r, column=1).fill = FILL_TOTAL
    ws.cell(row=r, column=1).border = DOUBLE_BOTTOM
    cell = ws.cell(row=r, column=2, value=fin["sources"]["total_sources"])
    cell.font = FONT_TOTAL
    cell.fill = FILL_TOTAL
    cell.number_format = FMT_NUMBER
    cell.border = DOUBLE_BOTTOM
    cell.alignment = ALIGN_RIGHT

    ws.cell(row=r, column=4, value="Total Uses").font = FONT_TOTAL
    ws.cell(row=r, column=4).fill = FILL_TOTAL
    ws.cell(row=r, column=4).border = DOUBLE_BOTTOM
    cell = ws.cell(row=r, column=5, value=fin["uses"]["total_uses"])
    cell.font = FONT_TOTAL
    cell.fill = FILL_TOTAL
    cell.number_format = FMT_NUMBER
    cell.border = DOUBLE_BOTTOM
    cell.alignment = ALIGN_RIGHT

    # Premium Analysis
    row = r + 2
    _write_section_header(ws, row, "PREMIUM ANALYSIS", 6)
    row += 1
    _write_header_row(ws, row, ["Metric", "Ambuja", "ACC"])

    pa = PREMIUM_ANALYSIS
    prem_rows = [
        ("Offer Price (₹/share)", pa["ambuja"]["offer_price"], pa["acc"]["offer_price"]),
        ("Undisturbed 30-Day VWAP (₹)", pa["ambuja"]["undisturbed_30d_vwap"], pa["acc"]["undisturbed_30d_vwap"]),
        ("Premium to VWAP (%)", f"{pa['ambuja']['premium_to_vwap_pct']}%", f"{pa['acc']['premium_to_vwap_pct']}%"),
        ("Pre-Announcement Close (₹)", pa["ambuja"]["pre_announcement_close"], pa["acc"]["pre_announcement_close"]),
        ("Premium to Close (%)", f"{pa['ambuja']['premium_to_close_pct']}%", f"{pa['acc']['premium_to_close_pct']}%"),
        ("52-Week High (₹)", pa["ambuja"]["52w_high"], pa["acc"]["52w_high"]),
        ("52-Week Low (₹)", pa["ambuja"]["52w_low"], pa["acc"]["52w_low"]),
    ]
    for i, (label, amb, acc_v) in enumerate(prem_rows):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=label).font = FONT_LABEL
        ws.cell(row=r, column=1).border = THIN_BORDER
        for c, v in [(2, amb), (3, acc_v)]:
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = FONT_INPUT if "Premium" not in label else FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            if isinstance(v, (int, float)):
                cell.number_format = FMT_NUMBER


# ==============================================================================
# TAB 2: ACQUIRER FINANCIALS
# ==============================================================================

def _create_acquirer_financials(wb):
    ws = wb.create_sheet("2. Ambuja Financials")
    _set_col_widths(ws, {"A": 35, "B": 15, "C": 15, "D": 15, "E": 15, "F": 15, "G": 15})

    ws.merge_cells("A1:G1")
    ws.cell(row=1, column=1, value="AMBUJA CEMENTS LTD — STANDALONE FINANCIALS").font = FONT_TITLE

    periods = ["FY2020", "FY2021", "FY2022", "FY2023E", "FY2024E", "FY2025E"]

    # Income Statement
    row = 3
    _write_section_header(ws, row, "INCOME STATEMENT (₹ Crores)", 7)
    row += 1
    _write_header_row(ws, row, ["", *periods])

    is_items = [
        ("Revenue", "revenue", False, False),
        ("Cost of Materials", "cost_of_materials", False, False),
        ("Employee Costs", "employee_costs", False, False),
        ("Power & Fuel Costs", "power_fuel_costs", False, False),
        ("Freight Expenses", "freight_expenses", False, False),
        ("Other Expenses", "other_expenses", False, False),
        ("EBITDA", "ebitda", True, False),
        ("  EBITDA Margin (%)", None, False, True),  # Calculated
        ("Depreciation", "depreciation", False, False),
        ("EBIT", "ebit", True, False),
        ("Interest Income", "interest_income", False, False),
        ("Interest Expense", "interest_expense", False, False),
        ("Other Income", "other_income", False, False),
        ("PBT", "pbt", True, False),
        ("Tax", "tax", False, False),
        ("Net Income", "net_income", True, False),
        ("EPS (₹)", "eps", True, False),
    ]

    for i, (label, key, is_total, is_margin) in enumerate(is_items):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=label).font = FONT_TOTAL if is_total else FONT_LABEL
        ws.cell(row=r, column=1).border = THIN_BORDER
        if is_total:
            ws.cell(row=r, column=1).fill = FILL_TOTAL
            ws.cell(row=r, column=1).border = BOTTOM_BORDER

        for j, period in enumerate(periods):
            c = j + 2
            if is_margin:
                ebitda = AMBUJA_INCOME_STATEMENT["ebitda"][period]
                rev = AMBUJA_INCOME_STATEMENT["revenue"][period]
                val = f"{ebitda / rev * 100:.1f}%"
            else:
                val = AMBUJA_INCOME_STATEMENT[key][period]

            cell = ws.cell(row=r, column=c, value=val)
            is_proj = "E" in period
            cell.font = FONT_TOTAL if is_total else (FONT_INPUT if is_proj else FONT_CALC)
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER if not is_total else BOTTOM_BORDER
            if is_total:
                cell.fill = FILL_TOTAL
            if isinstance(val, (int, float)):
                cell.number_format = FMT_EPS if key == "eps" else FMT_NUMBER

    # Key Ratios
    r = row + len(is_items) + 2
    _write_section_header(ws, r, "KEY RATIOS", 7)
    r += 1
    _write_header_row(ws, r, ["", *periods])

    ratios = [
        ("Revenue Growth (%)", None),
        ("EBITDA Margin (%)", None),
        ("Net Margin (%)", None),
        ("EBIT Margin (%)", None),
    ]
    for i, (label, _) in enumerate(ratios):
        rr = r + 1 + i
        ws.cell(row=rr, column=1, value=label).font = FONT_LABEL
        ws.cell(row=rr, column=1).border = THIN_BORDER
        for j, period in enumerate(periods):
            c = j + 2
            rev = AMBUJA_INCOME_STATEMENT["revenue"][period]
            if "Growth" in label:
                if j == 0:
                    val = "—"
                else:
                    prev_rev = AMBUJA_INCOME_STATEMENT["revenue"][periods[j - 1]]
                    val = f"{(rev / prev_rev - 1) * 100:.1f}%"
            elif "EBITDA" in label:
                val = f"{AMBUJA_INCOME_STATEMENT['ebitda'][period] / rev * 100:.1f}%"
            elif "Net" in label:
                val = f"{AMBUJA_INCOME_STATEMENT['net_income'][period] / rev * 100:.1f}%"
            elif "EBIT" in label:
                val = f"{AMBUJA_INCOME_STATEMENT['ebit'][period] / rev * 100:.1f}%"
            cell = ws.cell(row=rr, column=c, value=val)
            cell.font = FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER


# ==============================================================================
# TAB 3: TARGET FINANCIALS (ACC)
# ==============================================================================

def _create_target_financials(wb):
    ws = wb.create_sheet("3. ACC Financials")
    _set_col_widths(ws, {"A": 35, "B": 15, "C": 15, "D": 15, "E": 15, "F": 15, "G": 15})

    ws.merge_cells("A1:G1")
    ws.cell(row=1, column=1, value="ACC LIMITED — STANDALONE FINANCIALS").font = FONT_TITLE

    periods = ["FY2020", "FY2021", "FY2022", "FY2023E", "FY2024E", "FY2025E"]

    row = 3
    _write_section_header(ws, row, "INCOME STATEMENT (₹ Crores)", 7)
    row += 1
    _write_header_row(ws, row, ["", *periods])

    is_items = [
        ("Revenue", "revenue", False),
        ("Cost of Materials", "cost_of_materials", False),
        ("Employee Costs", "employee_costs", False),
        ("Power & Fuel Costs", "power_fuel_costs", False),
        ("Freight Expenses", "freight_expenses", False),
        ("Other Expenses", "other_expenses", False),
        ("EBITDA", "ebitda", True),
        ("Depreciation", "depreciation", False),
        ("EBIT", "ebit", True),
        ("Interest Income", "interest_income", False),
        ("Interest Expense", "interest_expense", False),
        ("Other Income", "other_income", False),
        ("PBT", "pbt", True),
        ("Tax", "tax", False),
        ("Net Income", "net_income", True),
        ("EPS (₹)", "eps", True),
    ]

    for i, (label, key, is_total) in enumerate(is_items):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=label).font = FONT_TOTAL if is_total else FONT_LABEL
        ws.cell(row=r, column=1).border = THIN_BORDER
        if is_total:
            ws.cell(row=r, column=1).fill = FILL_TOTAL

        for j, period in enumerate(periods):
            c = j + 2
            val = ACC_INCOME_STATEMENT[key][period]
            cell = ws.cell(row=r, column=c, value=val)
            is_proj = "E" in period
            cell.font = FONT_TOTAL if is_total else (FONT_INPUT if is_proj else FONT_CALC)
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            if is_total:
                cell.fill = FILL_TOTAL
            if isinstance(val, (int, float)):
                cell.number_format = FMT_EPS if key == "eps" else FMT_NUMBER


# ==============================================================================
# TAB 4: PURCHASE PRICE ALLOCATION
# ==============================================================================

def _create_ppa_tab(wb, model):
    ws = wb.create_sheet("4. PPA & Goodwill")
    _set_col_widths(ws, {"A": 40, "B": 18, "C": 18, "D": 18, "E": 18})

    ws.merge_cells("A1:E1")
    ws.cell(row=1, column=1, value="PURCHASE PRICE ALLOCATION & GOODWILL").font = FONT_TITLE

    for entity_idx, entity in enumerate(["ambuja", "acc"]):
        entity_name = "AMBUJA CEMENTS" if entity == "ambuja" else "ACC LIMITED"

        base_row = 3 + entity_idx * 22
        _write_section_header(ws, base_row, f"{entity_name} — PPA (₹ Crores)", 5)
        base_row += 1
        _write_header_row(ws, base_row, ["Item", "Book Value", "FV Adjustment", "Fair Value"])

        ppa = model.ppa[entity]
        fv_adj = ppa["fv_adjustments"]

        r = base_row + 1
        for key, adj in fv_adj.items():
            ws.cell(row=r, column=1, value=adj["description"]).font = FONT_LABEL
            ws.cell(row=r, column=1).border = THIN_BORDER

            for c, v in [(2, adj["book_value"]), (3, adj["fair_value_adjustment"]), (4, adj["fair_value"])]:
                cell = ws.cell(row=r, column=c, value=v)
                cell.font = FONT_INPUT if c == 3 else FONT_CALC
                cell.alignment = ALIGN_RIGHT
                cell.border = THIN_BORDER
                cell.number_format = FMT_NUMBER
                if v < 0:
                    cell.font = FONT_NEGATIVE
            r += 1

        # Totals
        ws.cell(row=r, column=1, value="Book Value of Equity").font = FONT_TOTAL
        ws.cell(row=r, column=1).fill = FILL_TOTAL
        ws.cell(row=r, column=1).border = BOTTOM_BORDER
        cell = ws.cell(row=r, column=2, value=ppa["book_equity"])
        cell.font = FONT_TOTAL
        cell.fill = FILL_TOTAL
        cell.number_format = FMT_NUMBER
        cell.border = BOTTOM_BORDER
        cell.alignment = ALIGN_RIGHT

        r += 1
        ws.cell(row=r, column=1, value="Total Fair Value Adjustments").font = FONT_TOTAL
        cell = ws.cell(row=r, column=3, value=ppa["total_fv_adjustment"])
        cell.font = FONT_TOTAL
        cell.number_format = FMT_NUMBER
        cell.alignment = ALIGN_RIGHT

        r += 1
        ws.cell(row=r, column=1, value="Fair Value of Net Identifiable Assets").font = FONT_TOTAL
        ws.cell(row=r, column=1).fill = FILL_TOTAL
        ws.cell(row=r, column=1).border = DOUBLE_BOTTOM
        cell = ws.cell(row=r, column=4, value=ppa["fv_net_assets"])
        cell.font = FONT_TOTAL
        cell.fill = FILL_TOTAL
        cell.number_format = FMT_NUMBER
        cell.border = DOUBLE_BOTTOM
        cell.alignment = ALIGN_RIGHT

        r += 1
        ws.cell(row=r, column=1, value="Implied Equity Value (100%)").font = FONT_LABEL
        cell = ws.cell(row=r, column=4, value=ppa["implied_equity_value_100pct"])
        cell.font = FONT_INPUT
        cell.number_format = FMT_NUMBER
        cell.alignment = ALIGN_RIGHT

        r += 1
        gw_key = f"{entity}_goodwill"
        ws.cell(row=r, column=1, value="GOODWILL").font = Font(
            name="Calibri", size=11, bold=True, color="9C0006"
        )
        ws.cell(row=r, column=1).fill = FILL_HIGHLIGHT
        ws.cell(row=r, column=1).border = DOUBLE_BOTTOM
        cell = ws.cell(row=r, column=4, value=model.goodwill[gw_key])
        cell.font = Font(name="Calibri", size=11, bold=True, color="9C0006")
        cell.fill = FILL_HIGHLIGHT
        cell.number_format = FMT_NUMBER
        cell.border = DOUBLE_BOTTOM
        cell.alignment = ALIGN_RIGHT

    # Total Goodwill Summary
    r += 3
    _write_section_header(ws, r, "GOODWILL SUMMARY", 5)
    r += 1
    gw = model.goodwill
    for label, val in [
        ("Ambuja Goodwill", gw["ambuja_goodwill"]),
        ("ACC Goodwill", gw["acc_goodwill"]),
        ("Total Goodwill", gw["total_goodwill"]),
        ("Goodwill as % of Purchase Price", f"{gw['goodwill_as_pct_of_pp']}%"),
    ]:
        ws.cell(row=r, column=1, value=label).font = FONT_LABEL if "Total" not in label else FONT_TOTAL
        ws.cell(row=r, column=1).border = THIN_BORDER
        if "Total" in label:
            ws.cell(row=r, column=1).fill = FILL_TOTAL
            ws.cell(row=r, column=1).border = DOUBLE_BOTTOM
        cell = ws.cell(row=r, column=2, value=val)
        cell.font = FONT_TOTAL if "Total" in label else FONT_CALC
        cell.alignment = ALIGN_RIGHT
        cell.border = THIN_BORDER
        if isinstance(val, (int, float)):
            cell.number_format = FMT_NUMBER
        if "Total" in label:
            cell.fill = FILL_TOTAL
            cell.border = DOUBLE_BOTTOM
        r += 1


# ==============================================================================
# TAB 5: PRO FORMA FINANCIALS
# ==============================================================================

def _create_pro_forma_tab(wb, model):
    ws = wb.create_sheet("5. Pro Forma")
    _set_col_widths(ws, {"A": 38, "B": 16, "C": 16, "D": 16, "E": 16})

    ws.merge_cells("A1:E1")
    ws.cell(row=1, column=1, value="PRO FORMA COMBINED FINANCIALS").font = FONT_TITLE

    periods = ["FY2023E", "FY2024E", "FY2025E"]

    # Pro Forma Income Statement
    row = 3
    _write_section_header(ws, row, "PRO FORMA INCOME STATEMENT (₹ Crores)", 5)
    row += 1
    _write_header_row(ws, row, ["", *periods], start_col=1)

    pf_is = model.pro_forma["income_statement"]

    is_rows = [
        ("Ambuja Revenue", "ambuja_revenue", False),
        ("ACC Revenue", "acc_revenue", False),
        ("Combined Revenue", "combined_revenue", True),
        ("", None, False),
        ("Ambuja EBITDA", "ambuja_ebitda", False),
        ("ACC EBITDA", "acc_ebitda", False),
        ("Synergy Contribution", "synergy_ebitda_impact", False),
        ("Combined EBITDA", "combined_ebitda", True),
        ("  EBITDA Margin (%)", "combined_ebitda_margin_pct", False),
        ("", None, False),
        ("Combined D&A", "combined_da", False),
        ("  of which PPA Amortization", "ppa_amortization", False),
        ("Combined EBIT", "combined_ebit", True),
        ("", None, False),
        ("Interest Income", "combined_interest_income", False),
        ("Interest Expense", "combined_interest_expense", False),
        ("  of which Incremental (Acq. Debt)", "incremental_interest", False),
        ("Other Income", "combined_other_income", False),
        ("", None, False),
        ("Combined PBT", "combined_pbt", True),
        ("Tax (25.17%)", "combined_tax", False),
        ("Combined Net Income", "combined_net_income", True),
        ("", None, False),
        ("Pro Forma EPS (₹)", "combined_eps", True),
    ]

    for i, (label, key, is_total) in enumerate(is_rows):
        r = row + 1 + i
        if not label:
            continue
        ws.cell(row=r, column=1, value=label).font = FONT_TOTAL if is_total else FONT_LABEL
        ws.cell(row=r, column=1).border = THIN_BORDER
        if is_total:
            ws.cell(row=r, column=1).fill = FILL_TOTAL

        for j, period in enumerate(periods):
            c = j + 2
            val = pf_is[period].get(key, "")
            cell = ws.cell(row=r, column=c, value=val)
            cell.font = FONT_TOTAL if is_total else FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            if is_total:
                cell.fill = FILL_TOTAL
            if isinstance(val, (int, float)):
                if "eps" in key.lower():
                    cell.number_format = FMT_EPS
                elif "margin" in key or "pct" in key:
                    cell.number_format = '0.0'
                else:
                    cell.number_format = FMT_NUMBER

    # Pro Forma Balance Sheet
    r = row + len(is_rows) + 3
    _write_section_header(ws, r, "PRO FORMA BALANCE SHEET AT CLOSE (₹ Crores)", 5)
    r += 1
    _write_header_row(ws, r, ["", "Amount"])

    bs = model.pro_forma["balance_sheet"]
    bs_rows = [
        ("ASSETS", None, True),
        ("  Property, Plant & Equipment", bs["assets"]["ppe"], False),
        ("  Intangible Assets (incl. PPA)", bs["assets"]["intangible_assets"], False),
        ("  Goodwill", bs["assets"]["goodwill"], False),
        ("  Cash & Equivalents", bs["assets"]["cash"], False),
        ("  Other Assets", bs["assets"]["other_assets"], False),
        ("Total Assets", bs["assets"]["total_assets"], True),
        ("", None, False),
        ("LIABILITIES & EQUITY", None, True),
        ("  Total Equity", bs["liabilities_equity"]["total_equity"], False),
        ("  Total Debt", bs["liabilities_equity"]["total_debt"], False),
        ("  Other Liabilities", bs["liabilities_equity"]["other_liabilities"], False),
        ("Total Liabilities & Equity", bs["liabilities_equity"]["total_le"], True),
    ]

    for i, (label, val, is_total) in enumerate(bs_rows):
        rr = r + 1 + i
        if not label:
            continue
        ws.cell(row=rr, column=1, value=label).font = FONT_TOTAL if is_total else FONT_LABEL
        ws.cell(row=rr, column=1).border = THIN_BORDER
        if is_total:
            ws.cell(row=rr, column=1).fill = FILL_TOTAL
        if val is not None:
            cell = ws.cell(row=rr, column=2, value=val)
            cell.font = FONT_TOTAL if is_total else FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            cell.number_format = FMT_NUMBER
            if is_total:
                cell.fill = FILL_TOTAL
                cell.border = DOUBLE_BOTTOM

    # Credit Metrics
    rr += 2
    _write_section_header(ws, rr, "PRO FORMA CREDIT METRICS", 5)
    rr += 1
    cm = bs["credit_metrics"]
    for label, val in [
        ("Gross Debt (₹ Cr)", cm["gross_debt"]),
        ("Net Debt (₹ Cr)", cm["net_debt"]),
        ("Combined EBITDA (₹ Cr)", cm["combined_ebitda"]),
        ("Gross Debt / EBITDA", f"{cm['gross_debt_to_ebitda']}x"),
        ("Net Debt / EBITDA", f"{cm['net_debt_to_ebitda']}x"),
        ("Interest Coverage", f"{cm['interest_coverage']}x"),
    ]:
        ws.cell(row=rr, column=1, value=label).font = FONT_LABEL
        ws.cell(row=rr, column=1).border = THIN_BORDER
        cell = ws.cell(row=rr, column=2, value=val)
        cell.font = FONT_CALC
        cell.alignment = ALIGN_RIGHT
        cell.border = THIN_BORDER
        if isinstance(val, (int, float)):
            cell.number_format = FMT_NUMBER
        rr += 1


# ==============================================================================
# TAB 6: SYNERGY ANALYSIS
# ==============================================================================

def _create_synergy_tab(wb, model):
    ws = wb.create_sheet("6. Synergies")
    _set_col_widths(ws, {"A": 45, "B": 16, "C": 16, "D": 16, "E": 16})

    ws.merge_cells("A1:E1")
    ws.cell(row=1, column=1, value="SYNERGY ANALYSIS").font = FONT_TITLE

    syn = model.synergies

    # Cost Synergies
    row = 3
    _write_section_header(ws, row, "COST SYNERGIES (₹ Crores)", 5)
    row += 1
    _write_header_row(ws, row, ["Category", "Run-Rate", "Year 1", "Year 2", "Year 3"])

    for key, details in syn["cost_synergies"].items():
        row += 1
        ws.cell(row=row, column=1, value=details["description"]).font = FONT_LABEL
        ws.cell(row=row, column=1).border = THIN_BORDER
        for c, v in [(2, details["run_rate"]), (3, details["year1"]),
                     (4, details["year2"]), (5, details["year3"])]:
            cell = ws.cell(row=row, column=c, value=v)
            cell.font = FONT_INPUT if c == 2 else FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            cell.number_format = FMT_NUMBER

    row += 1
    ws.cell(row=row, column=1, value="Total Cost Synergies").font = FONT_TOTAL
    ws.cell(row=row, column=1).fill = FILL_TOTAL
    ws.cell(row=row, column=1).border = DOUBLE_BOTTOM
    totals = syn["totals"]
    for c, v in [(2, totals["cost_synergy_runrate"]), (3, None), (4, None), (5, None)]:
        cell = ws.cell(row=row, column=c)
        if v is not None:
            cell.value = v
        cell.font = FONT_TOTAL
        cell.fill = FILL_TOTAL
        cell.border = DOUBLE_BOTTOM
        cell.alignment = ALIGN_RIGHT
        if isinstance(v, (int, float)):
            cell.number_format = FMT_NUMBER

    # Revenue Synergies
    row += 2
    _write_section_header(ws, row, "REVENUE SYNERGIES (₹ Crores)", 5)
    row += 1
    _write_header_row(ws, row, ["Category", "Run-Rate", "Year 1", "Year 2", "Year 3"])

    for key, details in syn["revenue_synergies"].items():
        row += 1
        ws.cell(row=row, column=1, value=details["description"]).font = FONT_LABEL
        ws.cell(row=row, column=1).border = THIN_BORDER
        for c, v in [(2, details["run_rate"]), (3, details["year1"]),
                     (4, details["year2"]), (5, details["year3"])]:
            cell = ws.cell(row=row, column=c, value=v)
            cell.font = FONT_INPUT if c == 2 else FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            cell.number_format = FMT_NUMBER

    # Total Synergies Summary
    row += 2
    _write_section_header(ws, row, "TOTAL SYNERGIES SUMMARY (₹ Crores)", 5)
    row += 1
    _write_header_row(ws, row, ["", "Run-Rate", "Year 1", "Year 2", "Year 3"])

    for label, vals in [
        ("Total Pre-Tax Synergies", [totals["total_runrate"], totals["year1"], totals["year2"], totals["year3"]]),
        ("After-Tax Synergies", [syn["after_tax"]["runrate"], syn["after_tax"]["year1"],
                                 syn["after_tax"]["year2"], syn["after_tax"]["year3"]]),
    ]:
        row += 1
        ws.cell(row=row, column=1, value=label).font = FONT_TOTAL
        ws.cell(row=row, column=1).fill = FILL_TOTAL
        ws.cell(row=row, column=1).border = BOTTOM_BORDER
        for c, v in enumerate(vals, 2):
            cell = ws.cell(row=row, column=c, value=v)
            cell.font = FONT_TOTAL
            cell.fill = FILL_TOTAL
            cell.alignment = ALIGN_RIGHT
            cell.border = BOTTOM_BORDER
            cell.number_format = FMT_NUMBER

    # NPV
    row += 2
    _write_section_header(ws, row, "NPV OF SYNERGIES (₹ Crores)", 5)
    npv = syn["npv"]
    for label, val in [
        ("PV of Year 1 Synergies", npv["pv_year1"]),
        ("PV of Year 2 Synergies", npv["pv_year2"]),
        ("PV of Year 3 Synergies", npv["pv_year3"]),
        ("PV of Terminal Value", npv["pv_terminal"]),
        ("Total NPV of Synergies", npv["total_npv"]),
        ("Less: Costs to Achieve", -npv["costs_to_achieve"]),
        ("NPV Net of Implementation Costs", npv["npv_net_of_costs"]),
    ]:
        row += 1
        is_total = "Total" in label or "Net of" in label
        ws.cell(row=row, column=1, value=label).font = FONT_TOTAL if is_total else FONT_LABEL
        ws.cell(row=row, column=1).border = THIN_BORDER
        if is_total:
            ws.cell(row=row, column=1).fill = FILL_TOTAL
            ws.cell(row=row, column=1).border = DOUBLE_BOTTOM
        cell = ws.cell(row=row, column=2, value=val)
        cell.font = FONT_TOTAL if is_total else FONT_CALC
        cell.alignment = ALIGN_RIGHT
        cell.border = THIN_BORDER
        cell.number_format = FMT_NUMBER
        if is_total:
            cell.fill = FILL_TOTAL
            cell.border = DOUBLE_BOTTOM


# ==============================================================================
# TAB 7: ACCRETION / DILUTION
# ==============================================================================

def _create_accretion_dilution_tab(wb, model):
    ws = wb.create_sheet("7. Accretion-Dilution")
    _set_col_widths(ws, {"A": 42, "B": 16, "C": 16, "D": 16, "E": 16})

    ws.merge_cells("A1:E1")
    ws.cell(row=1, column=1, value="ACCRETION / DILUTION ANALYSIS").font = FONT_TITLE

    periods = ["FY2023E", "FY2024E", "FY2025E"]
    ad = model.accretion_dilution

    row = 3
    _write_section_header(ws, row, "EPS ACCRETION / DILUTION (₹ per share)", 5)
    row += 1
    _write_header_row(ws, row, ["", *periods])

    ad_rows = [
        ("Standalone EPS (Ambuja)", "standalone_eps", False, False),
        ("", None, False, False),
        ("Pro Forma EPS (with Synergies)", "pf_eps_with_synergies", True, False),
        ("  Accretion / (Dilution) %", "accretion_dilution_with_syn_pct", False, True),
        ("", None, False, False),
        ("Pro Forma EPS (without Synergies)", "pf_eps_without_synergies", True, False),
        ("  Accretion / (Dilution) %", "accretion_dilution_without_syn_pct", False, True),
        ("", None, False, False),
        ("Synergy Contribution to EPS (₹)", "synergy_contribution_to_eps", False, False),
    ]

    for i, (label, key, is_total, is_pct) in enumerate(ad_rows):
        r = row + 1 + i
        if not label:
            continue
        ws.cell(row=r, column=1, value=label).font = FONT_TOTAL if is_total else FONT_LABEL
        ws.cell(row=r, column=1).border = THIN_BORDER
        if is_total:
            ws.cell(row=r, column=1).fill = FILL_TOTAL

        for j, period in enumerate(periods):
            c = j + 2
            val = ad["annual"][period][key]

            cell = ws.cell(row=r, column=c)
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER

            if is_pct:
                cell.value = f"{val:+.1f}%"
                cell.fill = FILL_ACCRETIVE if val > 0 else FILL_DILUTIVE
                cell.font = FONT_POSITIVE if val > 0 else FONT_NEGATIVE
            else:
                cell.value = val
                cell.font = FONT_TOTAL if is_total else FONT_CALC
                cell.number_format = FMT_EPS
                if is_total:
                    cell.fill = FILL_TOTAL

    # Breakeven Analysis
    r = row + len(ad_rows) + 2
    _write_section_header(ws, r, "BREAKEVEN SYNERGY ANALYSIS (₹ Crores)", 5)

    for label, val in [
        ("Breakeven Pre-Tax Synergy (Year 1)", ad["breakeven_synergy_pretax_cr"]),
        ("Actual Year 1 Pre-Tax Synergy", ad["actual_year1_synergy_cr"]),
        ("Synergy Cushion", ad["synergy_cushion_cr"]),
    ]:
        r += 1
        is_total = "Cushion" in label
        ws.cell(row=r, column=1, value=label).font = FONT_TOTAL if is_total else FONT_LABEL
        ws.cell(row=r, column=1).border = THIN_BORDER
        if is_total:
            ws.cell(row=r, column=1).fill = FILL_ACCRETIVE
        cell = ws.cell(row=r, column=2, value=val)
        cell.font = FONT_TOTAL if is_total else FONT_CALC
        cell.alignment = ALIGN_RIGHT
        cell.border = THIN_BORDER
        cell.number_format = FMT_NUMBER
        if is_total:
            cell.fill = FILL_ACCRETIVE
            cell.font = FONT_POSITIVE


# ==============================================================================
# TAB 8: SENSITIVITY ANALYSIS
# ==============================================================================

def _create_sensitivity_tab(wb, model):
    ws = wb.create_sheet("8. Sensitivity")
    _set_col_widths(ws, {"A": 22, "B": 15, "C": 15, "D": 15, "E": 15, "F": 15, "G": 15, "H": 15, "I": 15})

    ws.merge_cells("A1:H1")
    ws.cell(row=1, column=1, value="SENSITIVITY ANALYSIS").font = FONT_TITLE

    sens = model.sensitivity

    # 1. Premium Sensitivity
    row = 3
    _write_section_header(ws, row, "EPS SENSITIVITY TO PURCHASE PRICE PREMIUM (FY2024E)", 6)
    row += 1
    _write_header_row(ws, row, ["Premium %", "Offer Price (₹)", "Implied PP (₹ Cr)",
                                "PF EPS (₹)", "Accr./Dil. %"], start_col=1)

    for item in sens["premium_sensitivity"]:
        row += 1
        is_base = abs(item["premium_pct"] - 13.2) < 0.5
        vals = [
            f"{item['premium_pct']}%",
            item["offer_price"],
            item["implied_pp_cr"],
            item["pf_eps"],
            f"{item['accretion_dilution_pct']:+.1f}%",
        ]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            if isinstance(v, (int, float)):
                cell.number_format = FMT_NUMBER if c in [2, 3] else FMT_EPS
            if is_base:
                cell.fill = FILL_SUBHEADER
                cell.font = FONT_SUBHEADER
            elif c == 5:
                ad_val = item["accretion_dilution_pct"]
                cell.fill = FILL_ACCRETIVE if ad_val > 0 else FILL_DILUTIVE
                cell.font = FONT_POSITIVE if ad_val > 0 else FONT_NEGATIVE

    # 2. Cost of Debt Sensitivity
    row += 2
    _write_section_header(ws, row, "EPS SENSITIVITY TO COST OF DEBT (FY2024E)", 6)
    row += 1
    _write_header_row(ws, row, ["Cost of Debt %", "Annual Interest (₹ Cr)",
                                "PF EPS (₹)", "Accr./Dil. %"], start_col=1)

    for item in sens["debt_cost_sensitivity"]:
        row += 1
        is_base = abs(item["cost_of_debt_pct"] - 8.75) < 0.1
        vals = [
            f"{item['cost_of_debt_pct']}%",
            item["annual_interest_cr"],
            item["pf_eps"],
            f"{item['accretion_dilution_pct']:+.1f}%",
        ]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
            if isinstance(v, (int, float)):
                cell.number_format = FMT_NUMBER if c == 2 else FMT_EPS
            if is_base:
                cell.fill = FILL_SUBHEADER
                cell.font = FONT_SUBHEADER
            elif c == 4:
                ad_val = item["accretion_dilution_pct"]
                cell.fill = FILL_ACCRETIVE if ad_val > 0 else FILL_DILUTIVE
                cell.font = FONT_POSITIVE if ad_val > 0 else FONT_NEGATIVE

    # 3. 2D Matrix: Premium vs. Synergies
    row += 2
    _write_section_header(ws, row, "EPS ACCR./DIL. (%) — PREMIUM vs. SYNERGIES (FY2024E)", 9)
    row += 1

    syn_range = sens["synergy_range_for_matrix"]
    headers = ["Premium \\ Synergy (₹ Cr)"] + [str(s) for s in syn_range]
    _write_header_row(ws, row, headers, start_col=1)

    for matrix_row in sens["premium_vs_synergy_matrix"]:
        row += 1
        prem = matrix_row["premium_pct"]
        is_base = abs(prem - 13.2) < 0.5

        cell = ws.cell(row=row, column=1, value=f"{prem}%")
        cell.font = FONT_SUBHEADER if is_base else FONT_LABEL
        cell.alignment = ALIGN_CENTER
        cell.border = THIN_BORDER
        if is_base:
            cell.fill = FILL_SUBHEADER

        for c, syn_val in enumerate(syn_range, 2):
            ad_val = matrix_row[f"syn_{syn_val}"]
            cell = ws.cell(row=row, column=c, value=f"{ad_val:+.1f}%")
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
            cell.fill = FILL_ACCRETIVE if ad_val > 0 else FILL_DILUTIVE
            cell.font = FONT_POSITIVE if ad_val > 0 else FONT_NEGATIVE

    # Add note
    row += 2
    ws.cell(row=row, column=1, value="Notes:").font = FONT_SUBHEADER
    row += 1
    ws.cell(row=row, column=1, value="• Blue-highlighted rows indicate base case assumptions").font = FONT_SMALL
    row += 1
    ws.cell(row=row, column=1, value="• Green = accretive to EPS, Red = dilutive to EPS").font = FONT_SMALL
    row += 1
    ws.cell(row=row, column=1, value="• Synergy column shows run-rate (Year 2 = 65% of run-rate applied)").font = FONT_SMALL


# ==============================================================================
# TAB 9: PRECEDENT TRANSACTIONS
# ==============================================================================

def _create_precedents_tab(wb):
    ws = wb.create_sheet("9. Precedent Txns")
    _set_col_widths(ws, {"A": 14, "B": 20, "C": 28, "D": 14, "E": 16, "F": 14, "G": 16})

    ws.merge_cells("A1:G1")
    ws.cell(row=1, column=1, value="PRECEDENT TRANSACTIONS — INDIAN CEMENT M&A").font = FONT_TITLE

    row = 3
    headers = ["Date", "Acquirer", "Target", "EV/EBITDA", "EV/Tonne ($)", "Premium %", "Deal Value (₹ Cr)"]
    _write_header_row(ws, row, headers)

    for txn in PRECEDENT_TRANSACTIONS:
        row += 1
        vals = [
            txn["date"], txn["acquirer"], txn["target"],
            f"{txn['ev_ebitda']}x", f"${txn['ev_tonne_usd']}",
            f"{txn['premium_pct']}%" if txn["premium_pct"] > 0 else "N/A (Distressed)",
            txn["deal_value_cr"],
        ]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ALIGN_RIGHT if c > 3 else ALIGN_LEFT
            cell.border = THIN_BORDER
            if isinstance(v, (int, float)):
                cell.number_format = FMT_NUMBER

            if txn.get("this_deal"):
                cell.fill = FILL_SUBHEADER
                cell.font = FONT_SUBHEADER
            else:
                cell.font = FONT_CALC

    # Summary statistics
    row += 2
    non_distressed = [t for t in PRECEDENT_TRANSACTIONS if t["premium_pct"] > 0 and not t.get("this_deal")]

    stats = [
        ("Precedent Statistics (excl. distressed)", None, None, None),
        ("Mean EV/EBITDA",
         f"{sum(t['ev_ebitda'] for t in non_distressed) / len(non_distressed):.1f}x", None, None),
        ("Median EV/EBITDA",
         f"{sorted([t['ev_ebitda'] for t in non_distressed])[len(non_distressed) // 2]:.1f}x", None, None),
        ("Mean Premium",
         f"{sum(t['premium_pct'] for t in non_distressed) / len(non_distressed):.1f}%", None, None),
        ("Mean EV/Tonne",
         f"${sum(t['ev_tonne_usd'] for t in non_distressed) / len(non_distressed):.0f}", None, None),
    ]

    for label, val, _, _ in stats:
        ws.cell(row=row, column=1, value=label).font = FONT_SUBHEADER if val is None else FONT_LABEL
        ws.cell(row=row, column=1).border = THIN_BORDER
        if val is None:
            ws.cell(row=row, column=1).fill = FILL_SUBHEADER
        else:
            cell = ws.cell(row=row, column=2, value=val)
            cell.font = FONT_CALC
            cell.alignment = ALIGN_RIGHT
            cell.border = THIN_BORDER
        row += 1
