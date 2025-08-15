#!/bin/bash

# Mutual Fund Tax Analyzer Runner
# This script activates the virtual environment and runs the analysis

echo "====================================================="
echo "    Mutual Fund Tax Analyzer for ITR Filing"
echo "====================================================="
echo

# Check if virtual environment exists
if [ ! -d "mutual_fund_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv mutual_fund_env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source mutual_fund_env/bin/activate

# Install requirements if not already installed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Run the analysis
echo "Running mutual fund tax analysis..."
echo
python mutual_fund_tax_analyzer.py

echo
echo "====================================================="
echo "Analysis completed! Check the generated CSV files."
echo "====================================================="
