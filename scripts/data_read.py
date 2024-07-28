import pandas as pd
from openpyxl import load_workbook
import json
import sys
import os
import datetime


def log_message(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")


def log_dict(dictionary):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_dict = json.dumps(dictionary, indent=4)
    print(f"[{current_time}] {formatted_dict}")


def read_json_file(json_file_path):

    # Check if the JSON file exists
    if os.path.exists(json_file_path):
        log_message(f"Temporary JSON file exists in: {json_file_path}")
    else:
        log_message(f"Couldn't find the temporary JSON file in{json_file_path}")
        sys.exit(1)

    # Extract the value
    with open(json_file_path, "r") as f:
        user_input = json.load(f)

    # Log the name defined for audit
    log_message("The input specified by users in Input and Output Settings:")
    log_dict(user_input)

    return user_input


def get_named_range_value(wb, named_range):
    # Extract the cell reference from the named range (e.g., 'Model_Point!$C$3' -> '$C$3')
    sheet_reference = named_range.split("!")[0]
    cell_reference = named_range.split("!")[1]

    return wb[sheet_reference][cell_reference].value


def extract_table_from_reference(file_path, table_reference):
    # Extract the sheet name and cell range from the cell ranges reference

    sheet_name, cell_range = table_reference.split("!")
    col_start, col_end, row_start, row_end = None, None, None, None

    # Extract column and row information
    col_range, row_range = cell_range.split("$")[1::2], cell_range.split("$")[2::2]
    col_start, col_end = col_range[0], col_range[1]
    row_start, row_end = int(row_range[0].replace(":", "")), int(
        row_range[1].replace(":", "")
    )

    # Read the specified table from the sheet
    table_df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        usecols=f"{col_start}:{col_end}",
        header=0,
        skiprows=row_start - 1,
        nrows=row_end - row_start,
    )

    return table_df


def read_pricing_model_data(user_input):

    # user_input is a dictionary which were read from json file.
    input = user_input

    # get file path
    file_path = input["filePath"]
    log_message(f"Python script will be run based on this Excel model: {file_path}.")

    # Load the workbook
    wb = load_workbook(filename=file_path, data_only=True)

    # ------------------------------------------------------
    # Extract specific named ranges
    # ------------------------------------------------------
    #   Person Covered's Profile
    age = wb.defined_names[input["age"]].value
    gender = wb.defined_names[input["gender"]].value

    #   Contract Features
    pol_year = wb.defined_names[input["polYear"]].value
    sum_assured = wb.defined_names[input["sumAssured"]].value
    contribution_per_year = wb.defined_names[input["contributionPerYear"]].value
    surplus_share_to_shf = wb.defined_names[input["surplusShareToShf"]].value
    surplus_share_to_participant = wb.defined_names[
        input["surplusShareToParticipant"]
    ].value

    #   Contract Fees and Charges
    table_wakalah_fee_range = wb.defined_names[input["tabWakalahFee"]].value
    wakalah_fmc = wb.defined_names[input["wakalahFmc"]].value
    coi_loading = wb.defined_names[input["coiLoading"]].value

    #   Expense Assumptions
    expense_per_contribution_per_year = wb.defined_names[
        input["expensePerContributionPerYear"]
    ].value
    expense_per_fund_per_year = wb.defined_names[input["expensePerFundPerYear"]].value

    #   Decrements Assumptions
    table_mortality_range = wb.defined_names[input["tabMortalityRates"]].value
    table_lapse_range = wb.defined_names[input["tabLapseRate"]].value

    #   Economic Assumptions
    table_risk_free_rate_range = wb.defined_names[input["tabRiskFreeRates"]].value

    # ----------end of name extraction ---------------------------

    # ------------------------------------------------------
    # Extract values from named ranges
    # ------------------------------------------------------
    #   from the 'Model_Point' tab
    age_value = get_named_range_value(wb, age)
    gender_value = get_named_range_value(wb, gender)
    pol_year_value = get_named_range_value(wb, pol_year)
    sum_assured_value = get_named_range_value(wb, sum_assured)
    contribution_per_year_value = get_named_range_value(wb, contribution_per_year)
    surplus_share_to_shf_value = get_named_range_value(wb, surplus_share_to_shf)
    surplus_share_to_participant_value = get_named_range_value(
        wb, surplus_share_to_participant
    )

    #   from the 'Table' tab
    wakalah_fmc_value = get_named_range_value(wb, wakalah_fmc)
    expense_per_contribution_per_year_value = get_named_range_value(
        wb, expense_per_contribution_per_year
    )
    expense_per_fund_per_year_value = get_named_range_value(
        wb, expense_per_fund_per_year
    )
    coi_loading_value = get_named_range_value(wb, coi_loading)

    # Convert table's named ranges to DataFrames
    table_wakalah_fee = extract_table_from_reference(file_path, table_wakalah_fee_range)
    table_mortality = extract_table_from_reference(file_path, table_mortality_range)
    table_risk_free_rate = extract_table_from_reference(
        file_path, table_risk_free_rate_range
    )
    table_lapse = extract_table_from_reference(file_path, table_lapse_range)

    # ----------end of value extraction ---------------------------

    # Create a dictionary to return the data
    data = {
        "Age": age_value,
        "Gender": gender_value,
        "Pol_Year": pol_year_value,
        "SumAssured": sum_assured_value,
        "Contribution_perYear": contribution_per_year_value,
        "SurplusShare_toSHF": surplus_share_to_shf_value,
        "SurplusShare_toParticipant": surplus_share_to_participant_value,
        "Table_WakalahFee": table_wakalah_fee,
        "Table_Mortality": table_mortality,
        "Table_RiskFreeRate": table_risk_free_rate,
        "Table_Lapse": table_lapse,
        "Wakalah_FMC": wakalah_fmc_value,
        "Expense_perContribution_perYear": expense_per_contribution_per_year_value,
        "Expense_perFund_perYear": expense_per_fund_per_year_value,
        "COI_Loading": coi_loading_value,
    }

    return data
