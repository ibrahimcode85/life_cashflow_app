import pandas as pd
import numpy as np
import data_read as read


def append_dataframes(df_list):
    """
    Take a list of pandas dataframes and combined them along the columns.

    Parameters
    ----------
    df_list : List
        A list of pandas dataframe.

    Returns
    -------
    DataFrame
        Combined dataframe along the columns, based on the order listed in the list.

    Notes
    -----
    This function is typically used to get the final cashflows output dataframe to be exported.

    """
    proj_df = pd.concat(df_list, axis=1)

    return proj_df


# ================================
#  REFERENCE COLUMNS
# ================================
# - time index projection for 1200 months (i.e. maximum projection is 100 years).
# - bool to check if the year is within policy coverage period (1= cover, 0 = not-cover).
# - projection of policy month and policy year.
# - projection of attained age.


def generate_t_index_table():
    """
    Create a single column dataframe with index number starting from 1 to 1200.

    Parameters
    ----------
    None

    Returns
    -------
    DataFrame
        A single column dataframe with index number of 1 to 1200.

    Notes
    -----
    The index represent the projection month and for now is capped at 1200 (i.e 100 months).
    This will be the first column in our cashflows output dataframe and is a time reference for the occurence of the cashflows.
    """

    # Create a sequence of numbers from 1 to 1200
    t_index_values = list(range(1, 1201))

    # Create a pandas DataFrame with the specified column name
    t_index_df = pd.DataFrame(t_index_values, columns=["T_Index"])

    return t_index_df


def generate_is_cover_table(t_index_df, POL_YEAR):
    """
    Generate a single column dataframe which contain bool values indicating whether a policy is still inforce that month.

    Parameters
    ----------
    t_index_df : DataFrame
        A DataFrame containing a time index.

    POL_YEAR : int
        The number of years the policy is covered.

    Returns
    -------
    DataFrame
        A DataFrame indicating whether a policy is still inforce that month (1= inforce, 0= not inforce).
    """

    # Create a table of the same dimension as t_index_df
    is_cover_values = [
        1 if value <= POL_YEAR * 12 else 0 for value in t_index_df["T_Index"]
    ]

    # Create a pandas DataFrame with the specified column name
    is_cover_df = pd.DataFrame(is_cover_values, columns=["is_Cover"])

    return is_cover_df


def generate_pol_month_table(t_index_df, is_cover_df):
    """
    Generate a single column dataframe containing policy month table based on the time index.

    Parameters
    ----------
    t_index_df : DataFrame
        A DataFrame containing a time index.
    is_cover_df : DataFrame
        A DataFrame indicating coverage status for each time period.

    Returns
    -------
    DataFrame
        A DataFrame containing policy months. 0 if policy is not inforce.
    """

    # Calculate the product of t_index_df and is_cover_df
    pol_month_values = t_index_df["T_Index"] * is_cover_df["is_Cover"]

    # Create a pandas DataFrame with the specified column name
    pol_month_df = pd.DataFrame(pol_month_values, columns=["Pol_Month"])

    return pol_month_df


def generate_pol_year_table(pol_month_df, is_cover_df):
    """
    Generate a single column dataframe containing the policy year value based on the policy month.

    Parameters
    ----------
    pol_month_df : DataFrame
        A DataFrame containing policy months.
    is_cover_df : DataFrame
        A DataFrame indicating coverage status for each period.

    Returns
    -------
    DataFrame
        A DataFrame containing policy years. 0 if policy is not inforce.
    """

    # Calculate Pol_Year as ROUNDUP(pol_month_df / 12, 0) * is_cover_df
    pol_year_values = (
        np.ceil(pol_month_df["Pol_Month"] / 12).astype(int) * is_cover_df["is_Cover"]
    )

    # Create a pandas DataFrame with the specified column name
    pol_year_df = pd.DataFrame(pol_year_values, columns=["Pol_Year"])

    return pol_year_df


def generate_age_table(pol_year_df, is_cover_df, AGE):
    """
    Generate a single column dataframe containing the projected attained age.

    Parameters
    ----------
    pol_year_df : DataFrame
        A DataFrame containing policy years.
    is_cover_df : DataFrame
        A DataFrame indicating coverage status for each period.
    AGE : int
        The starting age of the policyholder.

    Returns
    -------
    DataFrame
        A DataFrame containing attained age for each period. 0 if policy is not inforce.
    """

    # Calculate Age as (Constant_Age + pol_year_df) * is_cover_df
    age_values = (AGE + pol_year_df["Pol_Year"] - 1) * is_cover_df["is_Cover"]

    # Create a pandas DataFrame with the specified column name
    age_df = pd.DataFrame(age_values, columns=["Age"])

    return age_df


# ================================
#  ECONOMIC RATES PROJECTION
# ================================
# - risk free rates lookup
# - risk free rates convertion to monthly rates
# - discount factor calculation


def generate_rfr_table(pol_year_df, rfr_table, is_cover_df):
    """
    Generate a risk-free rates dataframe. Two columns for each annual and monthly basis.

    Parameters
    ----------
    pol_year_df : DataFrame
        A DataFrame containing policy years.
    rfr_table : DataFrame
        A DataFrame containing annual risk-free rates.
    is_cover_df : DataFrame
        A DataFrame indicating coverage status for each period.

    Returns
    -------
    DataFrame
        A DataFrame containing annual and monthly risk-free rates for each period. 0 if policy is not inforce.
    """

    # Create a dictionary from the rfr_table
    rfr_dict = rfr_table.set_index("Year.1")["rfr p.a."].to_dict()

    # Find the last available value in the rfr_dict
    max_year = max(rfr_dict.keys())
    last_value = rfr_dict[max_year]

    # Create the rfr_lookup_values based on pol_year_df
    rfr_lookup_values = [
        rfr_dict.get(year, last_value) if year <= max_year else last_value
        for year in pol_year_df["Pol_Year"]
    ]

    # Create a pandas DataFrame with the specified column name
    rfr_lookup_df = pd.DataFrame(rfr_lookup_values, columns=["RiskFree_perYear"])

    # Calculate the monthly risk-free rate
    rfr_lookup_df["RiskFree_perMonth"] = (1 + rfr_lookup_df["RiskFree_perYear"]) ** (
        1 / 12
    ) - 1

    # Apply limit up to coverage period
    rfr_lookup_df["RiskFree_perYear"] = (
        rfr_lookup_df["RiskFree_perYear"] * is_cover_df["is_Cover"]
    )
    rfr_lookup_df["RiskFree_perMonth"] = (
        rfr_lookup_df["RiskFree_perMonth"] * is_cover_df["is_Cover"]
    )

    return rfr_lookup_df


def generate_discount_factor_table(rfr_lookup_df):
    """
    Generate a discount factor table based on monthly risk-free rates.

    Parameters
    ----------
    rfr_lookup_df : DataFrame
        A DataFrame containing monthly risk-free rates.

    Returns
    -------
    DataFrame
        A DataFrame containing discount factors for the beginning and end of each period.
    """

    # Initialize lists for discount factors
    disc_factor_bop = [1.0]  # Beginning of period discount factor
    disc_factor_eop = [
        1 / (1 + rfr_lookup_df["RiskFree_perMonth"][0])
    ]  # End of period discount factor

    # Calculate the discount factors for each row
    for i in range(1, len(rfr_lookup_df)):
        disc_factor_bop.append(
            disc_factor_bop[i - 1] / (1 + rfr_lookup_df["RiskFree_perMonth"][i - 1])
        )
        disc_factor_eop.append(
            disc_factor_eop[i - 1] / (1 + rfr_lookup_df["RiskFree_perMonth"][i])
        )

    # Create a pandas DataFrame with the calculated columns
    discount_factor_df = pd.DataFrame(
        {"disc_factor_bop": disc_factor_bop, "disc_factor_eop": disc_factor_eop}
    )

    return discount_factor_df


# ================================
#  DECREMENTS PROJECTION
# ================================
# - mortality and lapse rates lookup
# - conversion to monthly decrement rates
# - calculation of policy count as: Number of Policy at End of Period = Num Policy at Start - Num of Death - Num of Lapse


def generate_mortality_rate_table(age_df, gender, mortality_table, is_cover_df):
    """
    Generate a mortality rate table based on age and gender.

    Parameters
    ----------
    age_df : DataFrame
        A DataFrame containing attained ages for each period.

    gender : str
        The gender of the policyholder ("Male" or "Female").

    mortality_table : DataFrame
        A DataFrame containing annual mortality rates by age and gender.

    is_cover_df : DataFrame
        A DataFrame indicating coverage status for each period.

    Returns
    -------
    DataFrame
        A DataFrame containing annual and monthly mortality rates for each period. 0 if policy is not inforce.
    """

    # Create a dictionary from the mortality_table
    mortality_dict = mortality_table.set_index("Age").to_dict(orient="index")

    # Find the maximum age available in the mortality table
    max_age = max(mortality_dict.keys())

    # Initialize a list to store the lookup results
    rates = []

    # Loop through the ages in age_df
    for age in age_df["Age"]:
        if age in mortality_dict:
            rate = (
                mortality_dict[age]["Male Rates"]
                if gender == "Male"
                else mortality_dict[age]["Female Rates"]
            )
        else:
            rate = (
                mortality_dict[max_age]["Male Rates"]
                if gender == "Male"
                else mortality_dict[max_age]["Female Rates"]
            )
        rates.append(rate)

    # Create a pandas DataFrame with the lookup results
    mort_rates_df = pd.DataFrame(rates, columns=["Mortality_Rate_perYear"])

    # Calculate the monthly decrement rates
    mort_rates_df["Mortality_Rate_perMonth"] = 1 - (
        1 - mort_rates_df["Mortality_Rate_perYear"]
    ) ** (1 / 12)

    # Apply limit up to coverage period
    mort_rates_df["Mortality_Rate_perYear"] = (
        mort_rates_df["Mortality_Rate_perYear"] * is_cover_df["is_Cover"]
    )
    mort_rates_df["Mortality_Rate_perMonth"] = (
        mort_rates_df["Mortality_Rate_perMonth"] * is_cover_df["is_Cover"]
    )

    return mort_rates_df


def generate_lapse_rate(pol_year_df, lapse_table, max_pol_year):
    """
    Generate a lapse rate table based on policy year.

    Parameters
    ----------
    pol_year_df : DataFrame
        A DataFrame containing policy years.

    lapse_table : DataFrame
        A DataFrame containing annual lapse rates by policy year.

    max_pol_year : int
        The maximum policy year considered for lapse rates.

    Returns
    -------
    DataFrame
        A DataFrame containing annual and monthly lapse rates for each period.
        0 if policy is not inforce.
        1 if policy year reach maximum policy year.

    """

    # Create a dictionary from the lapse_table
    lapse_dict = lapse_table.set_index("Year")["%"].to_dict()

    # Find the maximum year available in the lapse table
    max_year = max(lapse_dict.keys())

    # Initialize a list to store the lookup results
    lapse_rates = []

    # Loop through the years in pol_year_df
    for year in pol_year_df["Pol_Year"]:
        if year == 0:
            lapse_rate = 0
        elif year == max_pol_year:
            lapse_rate = 1
        elif year in lapse_dict:
            lapse_rate = lapse_dict[year] / 100
        else:
            lapse_rate = lapse_dict[max_year] / 100

        lapse_rates.append(lapse_rate)

    # Create a pandas DataFrame with the lookup results
    lapse_rates_df = pd.DataFrame(lapse_rates, columns=["Lapse_Rate_perYear"])

    # Calculate the monthly decrement rates
    lapse_rates_df["Lapse_Rate_perMonth"] = 1 - (
        1 - lapse_rates_df["Lapse_Rate_perYear"]
    ) ** (1 / 12)

    return lapse_rates_df


def generate_policy_count_table(pol_month_df, mortality_rates_df, lapse_rates_df):
    """
    Generate a policy count table based on policy month, mortality, and lapse rates.

    Parameters
    ----------
    pol_month_df : DataFrame
        A DataFrame containing policy months.

    mortality_rates_df : DataFrame
        A DataFrame containing monthly mortality rates.

    lapse_rates_df : DataFrame
        A DataFrame containing monthly lapse rates.

    Returns
    -------
    DataFrame
        A DataFrame containing policy counts at the start, end, and decrements for each period.

    Notes
    -------
    The death and lapse count is calculated by applying the decrement rates to the beginning of period policy count.
    Assumption is that death and lapse is independent and not competing - so the incidence count is simply the incidence rate
    applied to opening count without any adjustment for competing incidence rates.

    Number of Death = Num Policy at Start * Death Rate
    Number of Lapse = Num Policy at Start * Lapse Rate
    Number of Policy at End of Period = Num Policy at Start - Num of Death - Num of Lapse

    """

    # Initialize lists for policy counts
    no_pol_start = [1]  # No_Pol_Start starts with 1
    no_death = []  # To be calculated
    no_lapse = []  # To be calculated
    no_pol_end = []  # To be calculated

    # Loop through each year to calculate the policy counts
    for i in range(len(pol_month_df)):
        if i > 0:
            no_pol_start.append(no_pol_end[i - 1])

        # Calculate No_Death
        death = no_pol_start[i] * mortality_rates_df.loc[i, "Mortality_Rate_perMonth"]
        no_death.append(death)

        # Calculate No_Lapse
        lapse = (no_pol_start[i] - death) * lapse_rates_df.loc[i, "Lapse_Rate_perMonth"]
        no_lapse.append(lapse)

        # Calculate No_Pol_End
        end = no_pol_start[i] - death - lapse
        no_pol_end.append(end)

    # Create a pandas DataFrame with the calculated columns
    policy_count_df = pd.DataFrame(
        {
            "No_Pol_Start": no_pol_start,
            "No_Death": no_death,
            "No_Lapse": no_lapse,
            "No_Pol_End": no_pol_end,
        }
    )

    return policy_count_df


# ==========================================
#  UNIT FUND PER POLICY CASH FLOWs PROJECTION
# ==========================================
# - Unit fund cashflow item: Contribution, Wakalah Fee, Insurance Charges, Investment Income and Fund Management Charge.
# - Unit Fund at End of Period = Unit Fund at Beginning of Period + (Contribution - Wakalah Fee) - Insurance Charge + Investment Income - Fund Management Charge.


def generate_wakalah_fee_rate(pol_year_df, wakalah_fee_table):
    """
    Generate a Wakalah fee rate table based on policy year.

    Parameters
    ----------
    pol_year_df : DataFrame
        A DataFrame containing policy years.

    wakalah_fee_table : DataFrame
        A DataFrame containing Wakalah fee rates by policy year.

    Returns
    -------
    DataFrame
        A DataFrame containing Wakalah fee rates for each period. 0 if policy is not inforce.
    """

    # Create a dictionary from the wakalah_fee_table
    wakalah_fee_dict = wakalah_fee_table.set_index("Year")["%"].to_dict()

    # Find the maximum year available in the wakalah fee table
    max_year = max(wakalah_fee_dict.keys())

    # Initialize a list to store the lookup results
    wakalah_fee_rates = []

    # Loop through the years in pol_year_df
    for year in pol_year_df["Pol_Year"]:
        if year in wakalah_fee_dict:
            wakalah_fee_rate = wakalah_fee_dict[year]
        else:
            wakalah_fee_rate = wakalah_fee_dict[max_year]
        wakalah_fee_rates.append(wakalah_fee_rate)

    # Create a pandas DataFrame with the lookup results
    wakalah_fee_rate_df = pd.DataFrame(wakalah_fee_rates, columns=["Wakalah_Fee_Rate"])

    return wakalah_fee_rate_df


def generate_unit_fund_cashflow_table(
    contribution_per_year,
    is_cover_df,
    pol_year_df,
    wakalah_fee_table,
    sum_assured,
    mort_rates_df,
    coi_loading,
    rfr_df,
    fmc,
):
    """
    Generate a unit fund cashflow table based on various inputs and assumptions.

    Parameters
    ----------
    contribution_per_year : float
        The annual contribution amount.

    is_cover_df : DataFrame
        A DataFrame indicating coverage status for each period.

    pol_year_df : DataFrame
        A DataFrame containing policy years.

    wakalah_fee_table : DataFrame
        A DataFrame containing Wakalah fee rates by policy year.

    sum_assured : float
        The sum assured amount.

    mort_rates_df : DataFrame
        A DataFrame containing monthly mortality rates.

    coi_loading : float
        The cost of insurance loading factor.

    rfr_df : DataFrame
        A DataFrame containing monthly risk-free rates.

    fmc : float
        The fund management charge rate.

    Returns
    -------
    DataFrame
        A DataFrame containing unit fund cashflows for each period. 0 if policy is not inforce.

    Notes
    -------
    The table contains each of the unit fund cashflows item:

    Contribution        : cash inflow. A lookup value
    Wakalah Fee         : cash outflow. A portion of contribution transferred to shareholder as service fee
                            = Contribution * Wakalah Fee Rate
    Unit Allocation     : cash inflow. The portion of contribution left in the unit fund.
                            = Contribution - Wakalah Fee.
    Insurance Charge    : cash outflow. The amount transferred to risk fund to pay for insurance coverage.
                            = Sum Assured * Mortality Rates * (1 + Insurance Charge Loading)
    Investment Income   : cash inflow. The investment income earned on the unit fund
                            = (Opening Fund + Unit Allocation - Insurance Charge) * Investment Return
    Investment Charge   : cash outflow. The fund management charge deducted as a service fee to manage the unit fund.
                            = (Opening Fund + Unit Allocation - Insurance Charge + Invesment Income) * Fund Management Charge

    Unit Fund At End of Period =  Unit Fund At Start + Unit Allocation - Insurance Charge + Investment Income - Investment Charge

    """

    # Initialize lists for cashflow calculations
    unit_fund_bop_pp = [0]  # Unit_Fund_BOP_PP starts with 0
    contribution_pp = (contribution_per_year / 12) * is_cover_df["is_Cover"]
    wakalah_fee_rate_df = generate_wakalah_fee_rate(pol_year_df, wakalah_fee_table)
    wakalah_fee_pp = contribution_pp * (wakalah_fee_rate_df["Wakalah_Fee_Rate"] / 100)
    unit_alloc_pp = contribution_pp - wakalah_fee_pp

    insurance_charge_pp = (
        sum_assured * mort_rates_df["Mortality_Rate_perMonth"] * (1 + coi_loading)
    )
    unit_invinc_pp = []
    unit_invcharge_pp = []
    unit_fund_eop_pp = []

    # Loop through each period to calculate the values
    for i in range(len(pol_year_df)):
        if i > 0:
            unit_fund_bop_pp.append(
                unit_fund_eop_pp[i - 1] * is_cover_df["is_Cover"][i]
            )

        inv_inc = (
            unit_fund_bop_pp[i] + unit_alloc_pp[i] - insurance_charge_pp[i]
        ) * rfr_df["RiskFree_perMonth"][i]
        unit_invinc_pp.append(inv_inc)

        inv_charge = (
            unit_fund_bop_pp[i] + unit_alloc_pp[i] - insurance_charge_pp[i] + inv_inc
        ) * (fmc / 12)
        unit_invcharge_pp.append(inv_charge)

        end_val = (
            unit_fund_bop_pp[i]
            + unit_alloc_pp[i]
            - insurance_charge_pp[i]
            + inv_inc
            - inv_charge
        )
        unit_fund_eop_pp.append(end_val)

    # Create pandas DataFrames with the calculated columns
    unit_cashflow_df = pd.DataFrame(
        {
            "Contribution_PP": contribution_pp,
            "Wakalah_Fee_Rate": wakalah_fee_rate_df["Wakalah_Fee_Rate"],
            "Wakalah_Fee_PP": wakalah_fee_pp,
            "Unit_Fund_BOP_PP": unit_fund_bop_pp,
            "Unit_Alloc_PP": unit_alloc_pp,
            "Insurance_Charge_PP": insurance_charge_pp,
            "Unit_InvInc_PP": unit_invinc_pp,
            "Unit_InvCharge_PP": unit_invcharge_pp,
            "Unit_Fund_EOP_PP": unit_fund_eop_pp,
        }
    )

    return unit_cashflow_df


# ==========================================
# RISK FUND PER POLICY CASH FLOWs PROJECTION
# ==========================================
# - Risk fund cashflow item:  Insurance Charges, Claims, Investment Income, Surplus to Shareholder and Surplus to Participant
# - Risk Fund at End of Period = Risk Fund at Beginning of Period + Insurance Charge + Investment Income - Surplus to Shareholder - Surplus to Participant.
# - Assume surplus as cash pay-out to policyholders instead of credited to unit fund.


def generate_risk_fund_cashflows_table(
    unit_cashflow_df,
    mort_rates_df,
    rfr_df,
    sum_assured,
    surplus_share_to_shf,
    surplus_share_to_participant,
):
    """
    Generate a risk fund cashflow table based on various inputs and assumptions.

    Parameters
    ----------
    unit_cashflow_df : DataFrame
        A DataFrame containing unit fund cashflows for each period.

    mort_rates_df : DataFrame
        A DataFrame containing monthly mortality rates. Used as basis to compute the insurance claims.

    rfr_df : DataFrame
        A DataFrame containing monthly risk-free rates.

    sum_assured : float
        The sum assured amount.

    surplus_share_to_shf : float
        The surplus share to shareholder factor.

    surplus_share_to_participant : float
        The surplus share to participant factor.

    Returns
    -------
    DataFrame
        A DataFrame containing risk fund cashflows for each period.

    Notes
    -------
    The table contains each of the risk fund cashflows item:

    Insurance Charge            : cash inflow. The amount transferred to risk fund to pay for insurance coverage.
                                    = Sum Assured * Mortality Rates * (1 + Insurance Charge Loading)
    Insurance Claims            : cash outflow. The expected claim amount paid from risk fund.
                                    = Sum Assured * No_Death
    Investment Income           : cash inflow. The investment income earned on the unit fund
                                    = (Opening Fund + Insurance Charge - Claims) * Investment Return
    Surplus Transfer to SH      : cash outflow. The amount of surplus transferred to shareholder fund (SH)
                                    = (Insurance Charge - Claims + Investment Income) * SH Transfer Ratio
    Surplus Transfer to Partpnt : cash outflow. The amount of surplus transferred to Participant (RF)
                                    = (Insurance Charge - Claims + Investment Income) * RF Transfer Ratio

    Risk Fund At End of Period =  Risk Fund At Start +  Insurance Charge - Claims + Investment Income
                                    - Surplus Transfer to SH - Surplus Transfer to RF

    """

    # Initialize lists for risk fund calculations
    risk_fund_bop_pp = [0]  # Risk_Fund_BOP_PP starts with 0
    insurance_charge_pp = unit_cashflow_df["Insurance_Charge_PP"]
    insurance_claim_pp = sum_assured * mort_rates_df["Mortality_Rate_perMonth"]
    risk_fund_invinc_pp = []
    surplus_to_shf_pp = []
    surplus_to_participant_pp = []
    risk_fund_eop_pp = []

    # Loop through each period to calculate the values
    for i in range(len(unit_cashflow_df)):
        if i > 0:
            risk_fund_bop_pp.append(risk_fund_eop_pp[i - 1])

        inv_inc = (risk_fund_bop_pp[i] + insurance_charge_pp[i]) * rfr_df[
            "RiskFree_perMonth"
        ][i]
        risk_fund_invinc_pp.append(inv_inc)

        surplus_shf = (
            risk_fund_bop_pp[i]
            + insurance_charge_pp[i]
            - insurance_claim_pp[i]
            + inv_inc
        ) * surplus_share_to_shf
        surplus_to_shf_pp.append(surplus_shf)

        surplus_participant = (
            risk_fund_bop_pp[i]
            + insurance_charge_pp[i]
            - insurance_claim_pp[i]
            + inv_inc
        ) * surplus_share_to_participant
        surplus_to_participant_pp.append(surplus_participant)

        eop = (
            risk_fund_bop_pp[i]
            + insurance_charge_pp[i]
            - insurance_claim_pp[i]
            + inv_inc
            - surplus_shf
            - surplus_participant
        )
        risk_fund_eop_pp.append(eop)

    # Create pandas DataFrames with the calculated columns
    risk_fund_cashflow_df = pd.DataFrame(
        {
            "Risk_Fund_BOP_PP": risk_fund_bop_pp,
            "Insurance_Charge_PP": insurance_charge_pp,
            "Insurance_Claim_PP": insurance_claim_pp,
            "Risk_Fund_InvInc_PP": risk_fund_invinc_pp,
            "Surplus_to_SHF_PP": surplus_to_shf_pp,
            "Surplus_to_Participant_PP": surplus_to_participant_pp,
            "Risk_Fund_EOP_PP": risk_fund_eop_pp,
        }
    )

    return risk_fund_cashflow_df


# ===================================================
# SHAREHOLDERS' FUND PER POLICY CASH FLOWs PROJECTION
# ===================================================
# - SHF fund cashflow item:  Wakalah Fee, Expenses, Fund Management Fee, Fund Expenses, Investment Income and Surplus to Shareholder.
# - Profit = Wakalah Fee - Expenses + Fund Management Fee - Fund Expenses + Investment Income +  Surplus to Shareholder.


def generate_shf_cashflows(
    unit_cashflow_df,
    rfr_df,
    risk_fund_df,
    expense_per_contribution_per_year,
    expense_per_fund_per_year,
):
    """
    Generate a shareholder's fund cashflow table based on various inputs and assumptions.

    Parameters
    ----------
    unit_cashflow_df : DataFrame
        A DataFrame containing unit fund cashflows for each period.

    rfr_df : DataFrame
        A DataFrame containing monthly risk-free rates.

    risk_fund_df : DataFrame
        A DataFrame containing risk fund cashflows for each period.

    expense_per_contribution_per_year : float
        The expense rate per contribution per year.

    expense_per_fund_per_year : float
        The expense rate per fund per year.

    Returns
    -------
    DataFrame
        A DataFrame containing shareholder's fund cashflows for each period.

    Notes
    -------
    The table contains each of the shareholders' fund cashflows item:

    Wakalah Fee             : cash inflow. A portion of contribution transferred to shareholder as service fee
                                = Contribution * Wakalah Fee Rate
    Expenses                : cash outflow. The expected expenses.
                                = Fixed expense per year.
    Investment Charge       : cash inflow. The fund management charge deducted as a service fee to manage the unit fund.
                                = Investment Charge deducted from Unit Fund.
    Investment Expense      : cash outflow. The fund management expense to cover the cost of managing the unit fund.
                                = Unit fund at End of Period * Investment Expense %
    Investment Income       : cash inflow. The investment income earned on the shareholders.
                                = (Wakalah Fee - Expenses) * Investment Return
    Surplus Transfer to SH  : cash inflow. The amount of surplus transferred to shareholder fund (SH)
                                = Surplus transferred from Risk Fund.

    Profit =  Wakalah Fee - Expense + Investment Charge - Investment Expense + Investment Income + Surplus from Risk Fund
    """

    # Initialize lists for SHF cashflow calculations
    wakalah_fee_pp = unit_cashflow_df["Wakalah_Fee_PP"]
    expenses_pp = unit_cashflow_df["Contribution_PP"] * (
        expense_per_contribution_per_year / 12
    )
    shf_invinc_pp = []
    unit_invcharge_pp = unit_cashflow_df["Unit_InvCharge_PP"]
    fund_expenses_pp = unit_cashflow_df["Unit_Fund_EOP_PP"] * expense_per_fund_per_year
    surplus_to_shf_pp = risk_fund_df["Surplus_to_SHF_PP"]
    profit = []

    # Loop through each period to calculate the values
    for i in range(len(unit_cashflow_df)):
        inv_inc = (wakalah_fee_pp[i] - expenses_pp[i]) * rfr_df["RiskFree_perMonth"][i]
        shf_invinc_pp.append(inv_inc)

        prof = (
            wakalah_fee_pp[i]
            - expenses_pp[i]
            + inv_inc
            + unit_invcharge_pp[i]
            - fund_expenses_pp[i]
            + surplus_to_shf_pp[i]
        )
        profit.append(prof)

    # Create pandas DataFrame with the calculated columns
    shf_cashflow_df = pd.DataFrame(
        {
            "Wakalah_Fee_PP": wakalah_fee_pp,
            "Expenses_PP": expenses_pp,
            "SHF_InvInc_PP": shf_invinc_pp,
            "Unit_InvCharge_PP": unit_invcharge_pp,
            "Fund_Expenses_PP": fund_expenses_pp,
            "Surplus_to_SHF_PP": surplus_to_shf_pp,
            "Profit_PP": profit,
        }
    )

    return shf_cashflow_df


# ===================================================
# INFORCE CASH FLOWs PROJECTION
# ===================================================
# - multiply the per-policy tables with the probability inforce at start of period.
# - please note the column name in per-policy table must contain the string '_PP' to indicate that they are
#   a per-policy cashflow item that require conversion to inforce '_IF'.
#   This is to differentiate with non-cashflow item such as rates, age, policy year, month etc.


def generate_cashflow_if_df(cashflow_df, policy_count_df, log_list, is_unit_fund=False):
    """
    Generate a inforce cashflow table based on per policy dataframe.

    Parameters
    ----------
    cashflow_df : DataFrame
        A DataFrame containing per policy cashflows for each period.

    policy_count_df : DataFrame
        A DataFrame containing monthly risk-free rates.

    log_list : List
        A list containing a collection of log messages to be printed.

    is_unit_fund : bool
        Indicator whether the cashflow is a unit fund or not. (True = Unit Fund)

    Returns
    -------
    DataFrame
        A DataFrame containing inforce cashflows for each period.

    Notes
    -------
    The function will loop through each column.
    If the column header contains the string "_PP" (indicating a per-policy cashflows),
    the column will be multiplied by inforce factor for the period.

    Inforce Cashflow = Per Policy Cashflow * No Policy At End of Period

    """
    # Initialize an empty dictionary to store the new columns
    cashflow_if_dict = {}

    # Loop through the columns of per-policy cashflow_df to calculate the new values and rename columns
    for col in cashflow_df.columns:
        if "_PP" in col:
            new_col_name = col.replace("_PP", "_IF")
            if new_col_name == "Unit_Fund_EOP_IF":
                # unit fund EOP is at end of period after claim. so apply to policy count at end of period instead of start.
                cashflow_if_dict[new_col_name] = (
                    cashflow_df[col] * policy_count_df["No_Pol_End"]
                )
            else:
                cashflow_if_dict[new_col_name] = (
                    cashflow_df[col] * policy_count_df["No_Pol_Start"]
                )

    # if this is unit fund, add additional column for fund release on claims
    if is_unit_fund == True:
        unit_after_inv = (
            cashflow_df["Unit_Fund_BOP_PP"]
            + cashflow_df["Unit_Alloc_PP"]
            - cashflow_df["Insurance_Charge_PP"]
            + cashflow_df["Unit_InvInc_PP"]
            - cashflow_df["Unit_InvCharge_PP"]
        )

        cashflow_if_dict["Fund_Rel_Death_IF"] = (
            unit_after_inv * policy_count_df["No_Death"]
        )
        cashflow_if_dict["Fund_Rel_Lapse_IF"] = (
            unit_after_inv * policy_count_df["No_Lapse"]
        )

    # Create a new DataFrame with the calculated columns
    cashflow_if_df = pd.DataFrame(cashflow_if_dict)

    # check if the net IF cashflow = Fund_EOP * no_pols_if (for Unit Fund only)
    if is_unit_fund == True:
        unit_after_claim = (
            unit_after_inv * policy_count_df["No_Pol_Start"]
            - cashflow_if_df["Fund_Rel_Death_IF"]
            - cashflow_if_df["Fund_Rel_Lapse_IF"]
        )
        unit_if_check = round(cashflow_if_df["Unit_Fund_EOP_IF"] - unit_after_claim, 4)

        if unit_if_check.sum() == 0:
            log_list = read.log_message(
                f"Checking passed for: Net IF Unit Cashflow = Unit_PP * No_Pols_IF ",
                log_list,
            )
        else:
            log_list = read.log_message(
                f"WARNING! Checking failed for: Net IF Unit Cashflow = Unit_PP * No_Pols_IF ",
                log_list,
            )

    return cashflow_if_df, log_list


# =====================
# DISCOUNTED CASH FLOW
# =====================


def generate_pv_cashflows_df(cashflow_df, disc_fac_df):
    """
    Generate a discounted value at start of projection for the relevant cashflow item.

    Parameters
    ----------
    cashflow_df : DataFrame
        A DataFrame containing per policy cashflows for each period.

    disc_fac_df : DataFrame
        A DataFrame containing the discount factor for each period.


    Returns
    -------
    DataFrame
        A DataFrame containing discounted value of selected cashflow.

    Notes
    -------
    PV Cashflow = Sum Product of (Array of Projected Cashflow , Array of Discount Factor)
    """

    # initialize timing dictionary and empty list
    cf_timing_dict = {
        # for unit fund
        "Contribution_IF": "BOP",
        "Wakalah_Fee_IF": "BOP",
        "Unit_Alloc_IF": "BOP",
        "Insurance_Charge_IF": "BOP",
        "Unit_InvInc_IF": "EOP",
        "Unit_InvCharge_IF": "EOP",
        "Fund_Rel_Death_IF": "EOP",
        "Fund_Rel_Lapse_IF": "EOP",
        # for risk fund
        "Insurance_Claim_IF": "EOP",
        "Risk_Fund_InvInc_IF": "EOP",
        "Surplus_to_SHF_IF": "EOP",
        "Surplus_to_Participant_IF": "EOP",
        # for shareholder's fund
        "Expenses_IF": "BOP",
        "SHF_InvInc_IF": "EOP",
        "Fund_Expenses_IF": "EOP",
        "Profit_IF": "EOP",
    }
    pv_cashflows = []

    # Loop through each column in cashflow_df
    for col in cashflow_df.columns:

        # Check if the col is defined for PV calculation (i.e. must be specified in pv_timing_dict)
        if col not in cf_timing_dict:
            continue

        # Get the cashflow timing and set the disc_factor_id
        cf_timing = cf_timing_dict[col]
        if cf_timing == "BOP":
            disc_fac_id = "disc_factor_bop"
        else:
            disc_fac_id = "disc_factor_eop"

        # Calculate the sum product of the cashflow_df[col] and discount_factor_df
        sum_product = (cashflow_df[col] * disc_fac_df[disc_fac_id]).sum()

        # Create the key name based on the column name
        key_name = f"PV_{col}"

        # Append the key-value pair to the list
        pv_cashflows.append([key_name, cf_timing, sum_product])

    # Create a DataFrame from the list
    pv_cashflows_df = pd.DataFrame(
        pv_cashflows, columns=["Cashflow", "Timing", "Present_Value"]
    )

    return pv_cashflows_df
