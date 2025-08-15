## Note: Vibe coded, run in isolation

# Mutual Fund Tax Analyzer for ITR Filing

This Python script analyzes mutual fund transactions from Kuvera reports and splits them based on July 23, 2024 - the date when new tax rules became applicable for mutual fund taxation in India.

## Features

- **Transaction Analysis**: Reads mutual fund transaction data from Excel files
- **Tax Period Split**: Automatically separates transactions before and after July 23, 2024
- **Capital Gains Calculation**: Calculates STCG (Short Term Capital Gains) and LTCG (Long Term Capital Gains)
- **ITR-Ready Reports**: Generates detailed reports suitable for Income Tax Return filing
- **Fund-wise Analysis**: Provides fund-wise breakdown of investments and gains
- **Export to CSV**: Exports all reports to CSV format for easy use in tax software

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your Kuvera mutual fund report file in the same directory as the script:
   - Excel format: `2.xlsx`

2. Run the analyzer:
   ```bash
   python mutual_fund_tax_analyzer.py
   ```

3. The script will generate the following CSV reports:
   - `MF_Tax_Summary_[timestamp].csv` - Overall summary by tax periods
   - `MF_Before_July23_2024_[timestamp].csv` - Detailed transactions before July 23, 2024
   - `MF_After_July23_2024_[timestamp].csv` - Detailed transactions after July 23, 2024
   - `MF_FundWise_Before_July23_2024_[timestamp].csv` - Fund-wise summary for old tax rules
   - `MF_FundWise_After_July23_2024_[timestamp].csv` - Fund-wise summary for new tax rules

## Understanding the Tax Change (July 23, 2024)

On July 23, 2024, the Indian government implemented changes to mutual fund taxation:

### Before July 23, 2024 (Old Rules):
- **Equity Funds**: STCG taxed at 15%, LTCG above ₹1 lakh taxed at 10%
- **Debt Funds**: STCG taxed as per income tax slab, LTCG at 20% with indexation

### After July 23, 2024 (New Rules):
- **All Mutual Funds**: STCG and LTCG taxed as per income tax slab rates
- **No Indexation Benefit**: Removed for debt mutual funds

## Report Fields Explanation

- **Fund Name**: Name of the mutual fund scheme
- **Transaction Number**: Sequential transaction identifier
- **Purchase Date**: Date of investment
- **Purchase Value**: Amount invested
- **Redemption Date**: Date of redemption/sale
- **Redemption Value**: Amount received on redemption
- **STCG**: Short Term Capital Gains (holdings ≤ 1 year for equity, ≤ 3 years for debt)
- **LTCG**: Long Term Capital Gains (holdings > 1 year for equity, > 3 years for debt)

## Important Notes for ITR Filing

1. **Verify Calculations**: Always cross-check calculations with your tax advisor
2. **Keep Documents**: Maintain all transaction confirmations and statements
3. **Tax Planning**: Consider the timing of redemptions based on applicable tax rules
4. **Professional Advice**: Consult a chartered accountant for complex scenarios

## Disclaimer

This tool is for informational purposes only. The user is responsible for verifying all calculations and ensuring compliance with current tax laws. Please consult a qualified tax professional for accurate tax advice.

## Support

For issues with the script or questions about the analysis, please review the generated reports and consult with your tax advisor for ITR filing guidance.
