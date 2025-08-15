#!/usr/bin/env python3
"""
Mutual Fund Tax Analyzer for ITR Filing
=======================================

This script analyzes mutual fund transactions from Kuvera report and splits them
based on July 23, 2024 - the date when new tax rules became applicable.

Requirements:
- pandas
- openpyxl (for Excel file reading)

Install dependencies:
pip install pandas openpyxl

Usage:
python mutual_fund_tax_analyzer.py

The script will:
1. Read the Excel file (2.xlsx) containing mutual fund transactions
2. Split transactions into two periods: Before and After July 23, 2024
3. Generate detailed reports for ITR filing
4. Calculate capital gains for each period
5. Export results to CSV files for easy reference
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
import os
from pathlib import Path

# Tax rule change date
TAX_CHANGE_DATE = datetime(2024, 7, 23)

class MutualFundTaxAnalyzer:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.transactions_df = None
        self.before_july_23 = None
        self.after_july_23 = None
        
    def read_excel_file(self):
        """Read the Excel file and extract transaction data"""
        try:
            # Try reading all sheets to understand structure
            all_sheets = pd.read_excel(self.excel_file_path, sheet_name=None, header=None)
            print(f"Found {len(all_sheets)} sheet(s): {list(all_sheets.keys())}")
            
            # Use the first sheet or look for specific sheet names
            sheet_name = list(all_sheets.keys())[0]
            df = all_sheets[sheet_name]
            
            print(f"Reading sheet: {sheet_name}")
            print(f"Sheet dimensions: {df.shape}")
            
            # Display first few rows to understand structure
            print("\nFirst 10 rows of the Excel file:")
            print(df.head(10).to_string())
            
            # Parse the Excel format similar to CSV
            return self.parse_excel_data(df)
            
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None
    
    def parse_excel_data(self, df):
        """Parse the Excel DataFrame with mutual fund transaction data"""
        try:
            transactions = []
            current_fund = None
            current_folio = None
            
            for idx, row in df.iterrows():
                # Convert row to string representation for parsing
                row_str = ' '.join([str(val) for val in row.values if pd.notna(val)])
                
                # Check if this is a fund name line
                if '[ISIN:' in row_str and '] (' in row_str:
                    current_fund = row_str.split('[ISIN:')[0].strip()
                    continue
                
                # Check if this is a folio line
                if 'Folio No:' in row_str:
                    current_folio = row_str.split('Folio No:')[1].strip()
                    continue
                
                # Try to parse transaction data
                try:
                    # Look for rows with transaction numbers (first cell should be a number)
                    first_cell = row.iloc[0]
                    if pd.notna(first_cell) and str(first_cell).strip().isdigit():
                        transaction_num = int(str(first_cell).strip())
                        
                        # Extract transaction data from the row
                        units = float(str(row.iloc[1]).replace(',', '')) if pd.notna(row.iloc[1]) and str(row.iloc[1]).strip() != '' else 0
                        
                        # Parse purchase date
                        purchase_date_str = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
                        purchase_date = self.parse_date(purchase_date_str) if purchase_date_str and purchase_date_str != 'nan' else None
                        
                        if purchase_date is None:
                            continue
                        
                        # Parse other fields
                        purchase_value = self.parse_currency(str(row.iloc[3])) if len(row) > 3 and pd.notna(row.iloc[3]) else 0
                        purchase_nav = float(str(row.iloc[4])) if len(row) > 4 and pd.notna(row.iloc[4]) and str(row.iloc[4]).strip() != '' else 0
                        
                        # Parse redemption data if available
                        redemption_date = None
                        redemption_value = 0
                        redemption_nav = 0
                        stcg = 0
                        ltcg = 0
                        
                        if len(row) > 8 and pd.notna(row.iloc[8]) and str(row.iloc[8]).strip() != '':
                            redemption_date = self.parse_date(str(row.iloc[8]).strip())
                        if len(row) > 9 and pd.notna(row.iloc[9]):
                            redemption_value = self.parse_currency(str(row.iloc[9]))
                        if len(row) > 10 and pd.notna(row.iloc[10]) and str(row.iloc[10]).strip() != '':
                            redemption_nav = float(str(row.iloc[10]))
                        if len(row) > 11 and pd.notna(row.iloc[11]):
                            stcg = self.parse_currency(str(row.iloc[11]))
                        if len(row) > 12 and pd.notna(row.iloc[12]):
                            ltcg = self.parse_currency(str(row.iloc[12]))
                        
                        transaction = {
                            'fund_name': current_fund,
                            'folio_number': current_folio,
                            'transaction_number': transaction_num,
                            'units': units,
                            'purchase_date': purchase_date,
                            'purchase_value': purchase_value,
                            'purchase_nav': purchase_nav,
                            'redemption_date': redemption_date,
                            'redemption_value': redemption_value,
                            'redemption_nav': redemption_nav,
                            'stcg': stcg,
                            'ltcg': ltcg
                        }
                        
                        transactions.append(transaction)
                        
                except (ValueError, IndexError) as e:
                    # Skip rows that don't contain valid transaction data
                    continue
            
            if len(transactions) == 0:
                print("No valid transactions found in Excel file.")
                return None
            
            print(f"Successfully parsed {len(transactions)} transactions from Excel file.")
            return pd.DataFrame(transactions)
            
        except Exception as e:
            print(f"Error parsing Excel data: {e}")
            return None
    
    def parse_date(self, date_str):
        """Parse date string in various formats"""
        if not date_str or date_str.strip() == '-':
            return None
            
        date_str = date_str.strip().strip('"')
        
        # Common date formats in the data
        formats = [
            "%b %d, %Y",      # "Aug 09, 2023"
            "%B %d, %Y",      # "August 09, 2023"
            "%d/%m/%Y",       # "09/08/2023"
            "%Y-%m-%d",       # "2023-08-09"
            "%d-%m-%Y",       # "09-08-2023"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date '{date_str}'")
        return None
    
    def parse_currency(self, currency_str):
        """Parse currency string and return float value"""
        if not currency_str or currency_str.strip() in ['-', '']:
            return 0.0
        
        # Remove currency symbols and commas
        cleaned = currency_str.replace('₹', '').replace(',', '').replace('"', '').strip()
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def analyze_transactions(self):
        """Analyze transactions and split by July 23, 2024"""
        
        # Read Excel file
        df = self.read_excel_file()
        
        if df is None:
            print("Error: Could not read transaction data from Excel file.")
            return False
        
        self.transactions_df = df
        
        # If we got data from Excel, we might need to process it differently
        if 'purchase_date' not in df.columns:
            print("Warning: Standard transaction columns not found. Attempting to parse Excel structure...")
            # This would need custom parsing based on the Excel structure
            return False
        
        # Filter out transactions without purchase dates
        valid_transactions = df[df['purchase_date'].notna()].copy()
        
        if len(valid_transactions) == 0:
            print("No valid transactions with purchase dates found.")
            return False
        
        # IMPORTANT: Tax rules apply based on REDEMPTION date, not purchase date
        # Filter transactions that have been redeemed (have redemption dates)
        redeemed_transactions = valid_transactions[valid_transactions['redemption_date'].notna()].copy()
        
        if len(redeemed_transactions) == 0:
            print("No redeemed transactions found.")
            return False
        
        print(f"Total transactions with purchase dates: {len(valid_transactions)}")
        print(f"Total redeemed transactions: {len(redeemed_transactions)}")
        
        # Split transactions by July 23, 2024 based on REDEMPTION DATE
        self.before_july_23 = redeemed_transactions[
            redeemed_transactions['redemption_date'] < TAX_CHANGE_DATE
        ].copy()
        
        self.after_july_23 = redeemed_transactions[
            redeemed_transactions['redemption_date'] >= TAX_CHANGE_DATE
        ].copy()
        
        print(f"\nTransaction Analysis (Based on Redemption Dates):")
        print(f"Total transactions with purchase dates: {len(valid_transactions)}")
        print(f"Total redeemed transactions: {len(redeemed_transactions)}")
        print(f"Redeemed before July 23, 2024 (Old Tax Rules): {len(self.before_july_23)}")
        print(f"Redeemed after July 23, 2024 (New Tax Rules): {len(self.after_july_23)}")
        
        return True
    
    def generate_summary_report(self):
        """Generate summary reports for ITR filing"""
        
        summary_report = {
            'period': ['Redeemed Before July 23, 2024 (Old Tax Rules)', 'Redeemed After July 23, 2024 (New Tax Rules)', 'Total'],
            'transactions_count': [
                len(self.before_july_23),
                len(self.after_july_23),
                len(self.before_july_23) + len(self.after_july_23)
            ],
            'total_purchase_value': [
                self.before_july_23['purchase_value'].sum(),
                self.after_july_23['purchase_value'].sum(),
                self.before_july_23['purchase_value'].sum() + self.after_july_23['purchase_value'].sum()
            ],
            'total_redemption_value': [
                self.before_july_23['redemption_value'].sum(),
                self.after_july_23['redemption_value'].sum(),
                self.before_july_23['redemption_value'].sum() + self.after_july_23['redemption_value'].sum()
            ],
            'total_stcg': [
                self.before_july_23['stcg'].sum(),
                self.after_july_23['stcg'].sum(),
                self.before_july_23['stcg'].sum() + self.after_july_23['stcg'].sum()
            ],
            'total_ltcg': [
                self.before_july_23['ltcg'].sum(),
                self.after_july_23['ltcg'].sum(),
                self.before_july_23['ltcg'].sum() + self.after_july_23['ltcg'].sum()
            ]
        }
        
        return pd.DataFrame(summary_report)
    
    def generate_fund_wise_report(self, period_df, period_name):
        """Generate fund-wise report for a specific period"""
        
        if len(period_df) == 0:
            return pd.DataFrame()
        
        fund_summary = period_df.groupby('fund_name').agg({
            'transaction_number': 'count',
            'purchase_value': 'sum',
            'redemption_value': 'sum',
            'stcg': 'sum',
            'ltcg': 'sum'
        }).reset_index()
        
        fund_summary.columns = [
            'Fund Name',
            'Number of Transactions',
            'Total Purchase Value',
            'Total Redemption Value',
            'Total STCG',
            'Total LTCG'
        ]
        
        # Calculate total gains
        fund_summary['Total Gains'] = fund_summary['Total STCG'] + fund_summary['Total LTCG']
        
        return fund_summary
    
    def export_reports(self):
        """Export all reports to CSV files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Summary report
        summary_df = self.generate_summary_report()
        summary_file = f"MF_Tax_Summary_{timestamp}.csv"
        summary_df.to_csv(summary_file, index=False)
        print(f"Summary report exported to: {summary_file}")
        
        # Before July 23, 2024 detailed report
        if len(self.before_july_23) > 0:
            before_file = f"MF_Before_July23_2024_{timestamp}.csv"
            self.before_july_23.to_csv(before_file, index=False)
            print(f"Before July 23, 2024 transactions exported to: {before_file}")
            
            # Fund-wise report for before period
            before_fund_wise = self.generate_fund_wise_report(self.before_july_23, "Before July 23, 2024")
            before_fund_file = f"MF_FundWise_Before_July23_2024_{timestamp}.csv"
            before_fund_wise.to_csv(before_fund_file, index=False)
            print(f"Fund-wise report (Before July 23, 2024) exported to: {before_fund_file}")
        
        # After July 23, 2024 detailed report
        if len(self.after_july_23) > 0:
            after_file = f"MF_After_July23_2024_{timestamp}.csv"
            self.after_july_23.to_csv(after_file, index=False)
            print(f"After July 23, 2024 transactions exported to: {after_file}")
            
            # Fund-wise report for after period
            after_fund_wise = self.generate_fund_wise_report(self.after_july_23, "After July 23, 2024")
            after_fund_file = f"MF_FundWise_After_July23_2024_{timestamp}.csv"
            after_fund_wise.to_csv(after_fund_file, index=False)
            print(f"Fund-wise report (After July 23, 2024) exported to: {after_fund_file}")
        
        return {
            'summary': summary_df,
            'before_july_23': self.before_july_23 if len(self.before_july_23) > 0 else None,
            'after_july_23': self.after_july_23 if len(self.after_july_23) > 0 else None
        }
    
    def print_analysis_summary(self):
        """Print a detailed analysis summary to console"""
        
        print("\n" + "="*80)
        print("MUTUAL FUND TAX ANALYSIS SUMMARY FOR ITR FILING")
        print("="*80)
        
        print(f"\nAnalysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tax Rule Change Date: {TAX_CHANGE_DATE.strftime('%Y-%m-%d')}")
        
        # Overall summary
        summary_df = self.generate_summary_report()
        print(f"\nOVERALL SUMMARY:")
        print(summary_df.to_string(index=False, float_format='%.2f'))
        
        # Before July 23, 2024 analysis
        if len(self.before_july_23) > 0:
            print(f"\nBEFORE JULY 23, 2024 (Old Tax Rules):")
            print(f"Number of transactions: {len(self.before_july_23)}")
            print(f"Total Purchase Value: ₹{self.before_july_23['purchase_value'].sum():,.2f}")
            print(f"Total Redemption Value: ₹{self.before_july_23['redemption_value'].sum():,.2f}")
            print(f"Total STCG: ₹{self.before_july_23['stcg'].sum():,.2f}")
            print(f"Total LTCG: ₹{self.before_july_23['ltcg'].sum():,.2f}")
            
            before_fund_wise = self.generate_fund_wise_report(self.before_july_23, "Before")
            if len(before_fund_wise) > 0:
                print(f"\nTop 5 funds by gains (Before July 23, 2024):")
                top_funds = before_fund_wise.nlargest(5, 'Total Gains')[['Fund Name', 'Total Gains']]
                print(top_funds.to_string(index=False, float_format='%.2f'))
        
        # After July 23, 2024 analysis
        if len(self.after_july_23) > 0:
            print(f"\nAFTER JULY 23, 2024 (New Tax Rules):")
            print(f"Number of transactions: {len(self.after_july_23)}")
            print(f"Total Purchase Value: ₹{self.after_july_23['purchase_value'].sum():,.2f}")
            print(f"Total Redemption Value: ₹{self.after_july_23['redemption_value'].sum():,.2f}")
            print(f"Total STCG: ₹{self.after_july_23['stcg'].sum():,.2f}")
            print(f"Total LTCG: ₹{self.after_july_23['ltcg'].sum():,.2f}")
            
            after_fund_wise = self.generate_fund_wise_report(self.after_july_23, "After")
            if len(after_fund_wise) > 0:
                print(f"\nTop 5 funds by gains (After July 23, 2024):")
                top_funds = after_fund_wise.nlargest(5, 'Total Gains')[['Fund Name', 'Total Gains']]
                print(top_funds.to_string(index=False, float_format='%.2f'))
        
        print("\n" + "="*80)
        print("IMPORTANT NOTES FOR ITR FILING:")
        print("="*80)
        print("1. Transactions before July 23, 2024 follow old tax rules")
        print("2. Transactions after July 23, 2024 follow new tax rules")
        print("3. STCG = Short Term Capital Gains")
        print("4. LTCG = Long Term Capital Gains")
        print("5. Please verify all calculations with your tax advisor")
        print("6. Keep all transaction documents for ITR filing")
        print("="*80)

def main():
    """Main function to run the analysis"""
    
    print("Mutual Fund Tax Analyzer for ITR Filing")
    print("======================================")
    
    # Check if required packages are installed
    try:
        import pandas as pd
        import openpyxl
        print("✓ Required packages are available")
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("\nPlease install required packages:")
        print("pip install pandas openpyxl")
        return False
    
    # Look for Excel file
    excel_file = "2.xlsx"
    
    if os.path.exists(excel_file):
        print(f"✓ Found Excel file: {excel_file}")
        analyzer = MutualFundTaxAnalyzer(excel_file)
    else:
        print(f"✗ Could not find mutual fund data file")
        print(f"Expected file: {excel_file}")
        return False
    
    # Run analysis
    print(f"\nStarting analysis...")
    
    if not analyzer.analyze_transactions():
        print("✗ Analysis failed")
        return False
    
    print("✓ Analysis completed successfully")
    
    # Print summary
    analyzer.print_analysis_summary()
    
    # Export reports
    print(f"\nExporting reports...")
    reports = analyzer.export_reports()
    print("✓ All reports exported successfully")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    print(f"\nAnalysis completed! Check the exported CSV files for detailed reports.")
