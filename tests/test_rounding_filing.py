import pandas as pd
import pytest
import yaml
from io import StringIO
import os

# Test data
data = """Year,Person1_Age,Person2_Age,Filing,Lifestyle,Total_Spend,Taxes_Due,Cash_Events,Target_Spend,Social_Security,IRA_Draw,Brokerage_Draw,Roth_Draw,Roth_Conversion,RMD,MAGI,Std_Deduction,IRA_Balance,Brokerage_Balance,Roth_Balance,Total_Assets,Shortfall
2025,58,56,MFJ,GoGo,100000,7756,0,92244,0,100000,0,0,0,0,100000,31500,321000,535000,107000,963000,0
2026,59,57,MFJ,GoGo,102500,7962,0,94539,0,102500,0,0,0,0,102500,32288,233795,572450,114490,920735,0
2027,60,58,MFJ,GoGo,105062,8172,0,96890,0,105063,0,0,0,0,105063,33095,137744,612522,122504,872770,0
2028,61,59,MFJ,GoGo,107689,8388,0,99301,0,107689,0,0,0,0,107689,33922,32159,655398,131080,818636,0
2029,62,60,MFJ,GoGo,110381,0,0,110381,0,32159,78223,0,0,0,32159,34770,0,617578,140255,757833,0
2030,63,61,MFJ,GoGo,113141,0,0,113141,0,0,113141,0,0,0,0,35639,0,539747,150073,689820,0
2031,64,62,MFJ,GoGo,115969,0,0,115969,0,0,115969,0,0,0,0,36530,0,453442,160578,614021,0
2032,65,63,MFJ,GoGo,118869,0,0,118869,0,0,118869,0,0,0,0,37444,0,357994,171819,529813,0
2033,66,64,MFJ,GoGo,121840,0,0,121840,0,0,121840,0,0,0,0,38380,0,252684,183846,436530,0
2034,67,65,MFJ,GoGo,124886,0,0,124886,0,0,124886,0,0,0,0,39339,0,136744,196715,333459,0
2035,68,66,MFJ,Slow,102407,0,0,102407,0,0,102407,0,0,0,0,40323,0,36741,210485,247226,0
2036,69,67,MFJ,Slow,104967,0,0,104967,20000,0,36741,48226,0,0,0,41331,0,0,173617,173617,0
2037,70,68,MFJ,Slow,107591,0,0,107591,60500,0,0,47091,0,0,0,42364,0,0,135383,135383,0
2038,71,69,MFJ,Slow,110281,0,0,110281,62013,0,0,48268,0,0,0,43423,0,0,93213,93213,0
2039,72,70,MFJ,Slow,113038,0,0,113038,63563,0,0,49475,0,0,0,44509,0,0,46799,46799,0
2040,73,71,MFJ,Slow,115864,0,0,115864,65152,0,0,46799,0,0,576,45621,0,0,0,0,3913
2041,74,72,MFJ,Slow,118760,0,0,118760,66781,0,0,0,0,0,1390,46762,0,0,0,0,51980
2042,75,73,MFJ,Slow,121729,0,0,121729,68450,0,0,0,0,0,2225,47931,0,0,0,0,53279
2043,76,74,Single,Slow,87341,0,0,87341,46388,0,0,0,0,0,0,49129,0,0,0,0,40953
2044,77,75,Single,Slow,89524,0,0,89524,47547,0,0,0,0,0,0,50357,0,0,0,0,41977
2045,78,76,Single,NoGo,68822,0,0,68822,48736,0,0,0,0,0,0,51616,0,0,0,0,20086
2046,79,77,Single,NoGo,70542,0,0,70542,49955,0,0,0,0,0,0,52907,0,0,0,0,20588
2047,80,78,Single,NoGo,72306,0,0,72306,51203,0,0,0,0,0,602,54229,0,0,0,0,21103
2048,81,79,Single,NoGo,74114,0,0,74114,52483,0,0,0,0,0,1242,55585,0,0,0,0,21630
2049,82,80,Single,NoGo,75966,0,0,75966,53796,0,0,0,0,0,1898,56975,0,0,0,0,22171
2050,83,81,Single,NoGo,77866,0,0,77866,55140,0,0,0,0,0,2570,58399,0,0,0,0,22725
2051,84,82,Single,NoGo,79812,0,0,79812,56519,0,0,0,0,0,3259,59859,0,0,0,0,23293
2052,85,83,Single,NoGo,81808,0,0,81808,57932,0,0,0,0,0,3966,61356,0,极 0,0,0,23876
2053,86,84,Single,NoGo,83853,0,0,83853,59380,0,0,0,0,0,4690,62890,0,0,0,0,24473
2054,87,85,Single,NoGo,85949,0,0,85949,60865,0,0,0,0,0,5432,64462,0,0,0,0,25084"""

# Load sample inputs directly
with open(os.path.join("examples", "sample_inputs.yaml"), "r") as file:
    inputs = yaml.safe_load(file)

# Create DataFrame
df = pd.read_csv(StringIO(data))


def test_filing_status_consistency():
    """Test that filing status matches the expected based on final ages"""
    final_age_person1 = inputs["final_age_person1"]
    final_age_person2 = inputs["final_age_person2"]

    for _, row in df.iterrows():
        person1_alive = row["Person1_Age"] < final_age_person1
        person2_alive = row["Person2_Age"] < final_age_person2

        if person1_alive and person2_alive:
            expected_filing = "MFJ"
        else:
            expected_filing = "Single"

        assert (
            row["Filing"] == expected_filing
        ), f"Year {row['Year']}: Expected {expected_filing}, got {row['Filing']}"


def test_account_balances_with_growth():
    """Test that account balances properly account for growth rates"""
    ira_growth = inputs["rates"]["ira_growth"]
    brokerage_growth = inputs["rates"]["brokerage_growth"]
    roth_growth = inputs["rates"]["roth_growth"]

    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        # Check IRA balance (accounting for growth and withdrawals)
        expected_ira = (prev["IRA_Balance"] - curr["IRA_Draw"]) * (1 + ira_growth)
        assert (
            abs(curr["IRA_Balance"] - expected_ira) < 100
        ), f"Year {curr['Year']}: IRA balance doesn't match expected growth"

        # Check Brokerage balance
        expected_brokerage = (prev["Brokerage_Balance"] - curr["Brokerage_Draw"]) * (
            1 + brokerage_growth
        )
        assert (
            abs(curr["Brokerage_Balance"] - expected_brokerage) < 100
        ), f"Year {curr['Year']}: Brokerage balance doesn't match expected growth"

        # Check Roth balance
        expected_roth = (
            prev["Roth_Balance"] - curr["Roth_Draw"] + curr["Roth_Conversion"]
        ) * (1 + roth_growth)
        assert (
            abs(curr["Roth_Balance"] - expected_roth) < 100
        ), f"Year {curr['Year']}: Roth balance doesn't match expected growth"


def test_standard_deduction_inflation():
    """Test that standard deduction accounts for inflation"""
    inflation_rate = inputs["rates"]["inflation"]
    base_deduction = inputs["tax_health"]["standard_deduction_base"]

    for _, row in df.iterrows():
        years_since_start = row["Year"] - 2025
        expected_deduction = base_deduction * (1 + inflation_rate) ** years_since_start

        assert (
            abs(row["Std_Deduction"] - expected_deduction) < 100
        ), f"Year {row['Year']}: Standard deduction doesn't match expected inflation adjustment"


def test_magi_calculation():
    """Test that MAGI is calculated correctly"""
    for _, row in df.iterrows():
        # MAGI should include IRA draws, Roth conversions, RMDs, and taxable portion of Social Security
        taxable_ss = row["Social_Security"] * 0.85  # 85% of SS is typically taxable
        expected_magi = (
            row["IRA_Draw"] + row["Roth_Conversion"] + row["RMD"] + taxable_ss
        )

        assert (
            abs(row["MAGI"] - expected_magi) < 100
        ), f"Year {row['Year']}: MAGI doesn't match expected calculation"


def test_rmd_calculations():
    """Test that RMDs are calculated correctly for appropriate ages"""
    rmd_start_age = inputs["tax_health"]["rmd_start_age"]

    for _, row in df.iterrows():
        older_age = max(row["Person1_Age"], row["Person2_Age"])

        if older_age >= rmd_start_age and row["IRA_Balance"] > 0:
            # RMD should be calculated (simplified check)
            assert (
                row["RMD"] > 0
            ), f"Year {row['Year']}: RMD should be calculated for age {older_age} with IRA balance"
        else:
            assert (
                row["RMD"] == 0
            ), f"Year {row['Year']}: RMD should not be calculated for age {older_age}"
