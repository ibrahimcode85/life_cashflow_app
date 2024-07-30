import projection as prj
import data_read as read
import pandas as pd
import sys
import os


if __name__ == "__main__":

    # Initalised log list
    log_list = []

    # Check if json path is passed as an argument and set the path if exists
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    else:
        log_list = read.log_message(
            "Path to temporary JSON file not provided.", log_list
        )
        sys.exit(1)

    # Get user input from json file
    user_input, log_list = read.read_json_file(json_file_path, log_list)

    # Read data dictionary
    pricing_model_data, log_list = read.read_pricing_model_data(user_input, log_list)

    # -----------------------------------------------------
    # Get the parameters and tables from the dictionary
    # -----------------------------------------------------
    #  Policyholder's profile
    AGE = pricing_model_data["Age"]
    GENDER = pricing_model_data["Gender"]

    # Insurance Contract features
    POL_YEAR = pricing_model_data["Pol_Year"]
    SUM_ASSD = pricing_model_data["SumAssured"]
    CONT_Y = pricing_model_data["Contribution_perYear"]
    SURPLUS_SHARE_SHF = pricing_model_data["SurplusShare_toSHF"]
    SURPLUS_SHARE_PH = pricing_model_data["SurplusShare_toParticipant"]

    # Contract Fees & Charges
    WAKALAH_TABLE = pricing_model_data["Table_WakalahFee"]
    WAKALAH_FMC = pricing_model_data["Wakalah_FMC"]
    COI_LOADING = pricing_model_data["COI_Loading"]

    # Expense Assumptions
    EXP_CONT_Y = pricing_model_data["Expense_perContribution_perYear"]
    EXP_FUND_Y = pricing_model_data["Expense_perFund_perYear"]

    # Decrements Assumptions
    MORT_TABLE = pricing_model_data["Table_Mortality"]
    LAPSE_TABLE = pricing_model_data["Table_Lapse"]

    # Decrements Assumptions
    RFR_TABLE = pricing_model_data["Table_RiskFreeRate"]

    # ----end of procedure----------------------------------------------

    # -----------------------------------------------------
    # Produce projections cashflows
    # -----------------------------------------------------

    # Initiate main columns
    t_index_col = prj.generate_t_index_table()
    is_cover_col = prj.generate_is_cover_table(t_index_col, POL_YEAR)
    pol_month_col = prj.generate_pol_month_table(t_index_col, is_cover_col)
    pol_year_col = prj.generate_pol_year_table(pol_month_col, is_cover_col)
    age_col = prj.generate_age_table(pol_year_col, is_cover_col, AGE)

    # Project risk-free return and discount factor
    rfr_proj_tab = prj.generate_rfr_table(pol_year_col, RFR_TABLE, is_cover_col)
    disc_fact_tab = prj.generate_discount_factor_table(rfr_proj_tab)

    # Project policy decrements
    mort_tab = prj.generate_mortality_rate_table(
        age_col, GENDER, MORT_TABLE, is_cover_col
    )
    lapse_tab = prj.generate_lapse_rate(pol_year_col, LAPSE_TABLE, POL_YEAR)
    pol_count_proj = prj.generate_policy_count_table(pol_month_col, mort_tab, lapse_tab)

    # Project per policy cashflows
    unit_cf_pp_proj = prj.generate_unit_fund_cashflow_table(
        CONT_Y,
        is_cover_col,
        pol_year_col,
        WAKALAH_TABLE,
        SUM_ASSD,
        mort_tab,
        COI_LOADING,
        rfr_proj_tab,
        WAKALAH_FMC,
    )
    risk_cf_pp_proj = prj.generate_risk_fund_cashflows_table(
        unit_cf_pp_proj,
        mort_tab,
        rfr_proj_tab,
        SUM_ASSD,
        SURPLUS_SHARE_SHF,
        SURPLUS_SHARE_PH,
    )
    shf_cf_pp_proj = prj.generate_shf_cashflows(
        unit_cf_pp_proj, rfr_proj_tab, risk_cf_pp_proj, EXP_CONT_Y, EXP_FUND_Y
    )

    # Project inforce cashflows
    unit_cf_if_proj, log_list = prj.generate_cashflow_if_df(
        unit_cf_pp_proj, pol_count_proj, log_list, is_unit_fund=True
    )
    risk_cf_if_proj, log_list = prj.generate_cashflow_if_df(
        risk_cf_pp_proj, pol_count_proj, log_list
    )
    shf_cf_if_proj, log_list = prj.generate_cashflow_if_df(
        shf_cf_pp_proj, pol_count_proj, log_list
    )

    # ----end of procedure----------------------------------------------

    # -----------------------------------------------------
    # Calculate Preset Values of cashflow
    # -----------------------------------------------------

    # Calculate PV of cashflow
    unit_cf_PV = prj.generate_pv_cashflows_df(unit_cf_if_proj, disc_fact_tab)
    risk_cf_PV = prj.generate_pv_cashflows_df(risk_cf_if_proj, disc_fact_tab)
    shf_cf_PV = prj.generate_pv_cashflows_df(shf_cf_if_proj, disc_fact_tab)

    # ----end of procedure----------------------------------------------

    # -----------------------------------------------------
    # Export output file
    # -----------------------------------------------------
    cf_proj_list = [
        t_index_col,
        is_cover_col,
        pol_month_col,
        pol_year_col,
        age_col,
        rfr_proj_tab,
        disc_fact_tab,
        mort_tab,
        lapse_tab,
        pol_count_proj,
        unit_cf_pp_proj,
        risk_cf_pp_proj,
        shf_cf_pp_proj,
        unit_cf_if_proj,
        risk_cf_if_proj,
        shf_cf_if_proj,
    ]

    cf_proj_table = prj.append_dataframes(cf_proj_list)

    # Define Excel output name
    output_path = user_input["outputFilePath"]
    output_name = user_input["outputFileName"]
    output_format = user_input["outputFormat"]
    output_file = output_path + "\\" + output_name + "." + output_format

    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        log_list = read.log_message(
            f"Output directory provided does not exists, '{output_path}' created successfully.",
            log_list,
        )

    # Write output
    if output_format == "xlsx":
        # Write data to Excel
        with pd.ExcelWriter(output_file) as writer:
            # Write cashflow projection table to "cashflow_proj" sheet
            cf_proj_table.to_excel(writer, sheet_name="Cashflow_Proj", index=False)

            # Write PV results to "pv_results" sheet
            pv_results = pd.concat([unit_cf_PV, risk_cf_PV, shf_cf_PV])
            pv_results.to_excel(writer, sheet_name="PV_Results", index=False)

        log_list = read.log_message(
            f"Output file has been created successfully in: {output_file}", log_list
        )

    elif output_format == "csv":
        # Write data to CSV
        cf_proj_table.to_csv(output_file, index=False)
        log_list = read.log_message(
            f"Output file has been created successfully in: {output_file}",
            log_list,
        )

        pv_results = pd.concat([unit_cf_PV, risk_cf_PV, shf_cf_PV])
        pv_results.to_csv(output_file.replace(".csv", "_pv_results.csv"), index=False)

        log_list = read.log_message(
            f"Output file has been created successfully in: {output_file.replace('.csv', '_pv_results.csv')}",
            log_list,
        )

    elif output_format == "pickle":
        # Write data to Pickle
        cf_proj_table.to_pickle(output_file.replace(".pickle", ".pkl"))
        log_list = read.log_message(
            f"Output file has been created successfully in: {output_file.replace(".pickle", ".pkl")}",
            log_list,
        )

        pv_results = pd.concat([unit_cf_PV, risk_cf_PV, shf_cf_PV])
        pv_results.to_pickle(output_file.replace(".pickle", "_pv_results.pkl"))
        log_list = read.log_message(
            f"Output file has been created successfully in: {output_file.replace('.pickle', '_pv_results.pkl')}",
            log_list,
        )

    else:
        log_list = read.log_message(
            f"Unsupported output format: {output_format}", log_list
        )

    # Delete the JSON file after processing
    os.remove(json_file_path)
    log_list = read.log_message(
        f"Temporary JSON file deleted after succesful creation of Output file.",
        log_list,
    )

    # Write log output file
    generate_log_bool = user_input["generateRunLog"]

    if generate_log_bool == True:
        log_file = output_path + "\\" + "log_output.txt"
        with open(log_file, "w") as file:
            for log_entry in log_list:
                file.write(log_entry + "\n")

            # write last entry
            log_list = read.log_message(
                f"Log file has been created successfully in: {log_file}", log_list
            )
            log_entry_last = log_list[-1]
            file.write(log_entry_last)

    # ----end of procedure----------------------------------------------
