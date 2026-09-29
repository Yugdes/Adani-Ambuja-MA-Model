"""
M&A Model Runner
=================
Generates the complete Excel model and prints a summary to console.
"""

import os
import sys
import io

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.merger_model import MergerModel
from model.excel_generator import generate_excel_model


def main():
    print("=" * 80)
    print("  M&A MERGER CONSEQUENCES MODEL")
    print("  Adani Group Acquisition of Ambuja Cements & ACC Ltd")
    print("  Deal Value: ~₹81,361 Crores (~US$10.5 Billion)")
    print("=" * 80)
    print("\nInitializing model...")

    # Build the model
    model = MergerModel()
    print("✅ Model calculations complete.")

    # Print summary
    model.print_summary()

    # Generate Excel
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    output_path = os.path.join(output_dir, "Adani_Ambuja_MA_Model.xlsx")

    print(f"\nGenerating Excel workbook...")
    generate_excel_model(model, output_path)

    print(f"\n📊 Workbook tabs:")
    print("   1. Transaction Summary — Deal overview, purchase price, premium, sources & uses")
    print("   2. Ambuja Financials — 3Y historical + 3Y projected income statement")
    print("   3. ACC Financials — 3Y historical + 3Y projected income statement")
    print("   4. PPA & Goodwill — Fair value adjustments, goodwill computation")
    print("   5. Pro Forma — Combined income statement & balance sheet")
    print("   6. Synergies — Cost & revenue synergies with phasing & NPV")
    print("   7. Accretion-Dilution — EPS analysis with/without synergies")
    print("   8. Sensitivity — Premium, cost of debt, 2D matrix")
    print("   9. Precedent Txns — Comparable Indian cement M&A deals")

    print(f"\n✅ All outputs generated successfully.")
    print(f"   Excel: {output_path}")
    print(f"   Dashboard: dashboard/index.html")
    print(f"   Deal Memo: deal_rationale/deal_memo.md")


if __name__ == "__main__":
    main()
