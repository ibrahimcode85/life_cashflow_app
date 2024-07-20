import pandas as pd
import numpy as np
from data_read import *


def append_dataframes(df_list):
    # Concatenate the list of DataFrames along the columns
    proj_df = pd.concat(df_list, axis=1)
    
    return proj_df


'''
POLICY'S TIME VALUE PROJECTION:
    - time index projection for 1200 months (i.e. maximum projection is 100 years).
    - bool to check if the year is within policy coverage period (1= cover, 0 = not-cover).
    - projection of policy month and policy year.
    - projection of attained age.
'''

def generate_t_index_table():
    # Create a sequence of numbers from 1 to 1200
    t_index_values = list(range(1, 1201))
    
    # Create a pandas DataFrame with the specified column name
    t_index_df = pd.DataFrame(t_index_values, columns=['T_Index'])
    
    return t_index_df


def generate_is_cover_table(t_index_df, POL_YEAR):
    # Create a table of the same dimension as t_index_df
    is_cover_values = [1 if value <= POL_YEAR*12 else 0 for value in t_index_df['T_Index']]
    
    # Create a pandas DataFrame with the specified column name
    is_cover_df = pd.DataFrame(is_cover_values, columns=['is_Cover'])
    
    return is_cover_df

def generate_pol_month_table(t_index_df, is_cover_df):
    # Calculate the product of t_index_df and is_cover_df
    pol_month_values = t_index_df['T_Index'] * is_cover_df['is_Cover']
    
    # Create a pandas DataFrame with the specified column name
    pol_month_df = pd.DataFrame(pol_month_values, columns=['Pol_Month'])
    
    return pol_month_df


def generate_pol_year_table(pol_month_df, is_cover_df):
    # Calculate Pol_Year as ROUNDUP(pol_month_df / 12, 0) * is_cover_df
    pol_year_values = np.ceil(pol_month_df['Pol_Month'] / 12).astype(int) * is_cover_df['is_Cover']
    
    # Create a pandas DataFrame with the specified column name
    pol_year_df = pd.DataFrame(pol_year_values, columns=['Pol_Year'])
    
    return pol_year_df


def generate_age_table(pol_year_df, is_cover_df, AGE):
    # Calculate Age as (Constant_Age + pol_year_df) * is_cover_df
    age_values = (AGE + pol_year_df['Pol_Year']  - 1) * is_cover_df['is_Cover']
    
    # Create a pandas DataFrame with the specified column name
    age_df = pd.DataFrame(age_values, columns=['Age'])
    
    return age_df


'''
ECONOMIC RATES PROJECTION:
    - risk free rates lookup
    - risk free rates convertion to monthly rates
    - discount factor calculation
'''

def generate_rfr_table(pol_year_df, rfr_table):
    # Create a dictionary from the rfr_table
    rfr_dict = rfr_table.set_index('Year.1')['rfr p.a.'].to_dict()
    
    # Find the last available value in the rfr_dict
    max_year = max(rfr_dict.keys())
    last_value = rfr_dict[max_year]
    
    # Create the rfr_lookup_values based on pol_year_df
    rfr_lookup_values = [rfr_dict.get(year, last_value) if year <= max_year else last_value for year in pol_year_df['Pol_Year']]
    
    # Create a pandas DataFrame with the specified column name
    rfr_lookup_df = pd.DataFrame(rfr_lookup_values, columns=['RiskFree_perYear'])

    # Calculate the monthly risk-free rate
    rfr_lookup_df['RiskFree_perMonth'] = (1 + rfr_lookup_df['RiskFree_perYear'])**(1/12) - 1
    
    return rfr_lookup_df


def generate_discount_factor_table(rfr_lookup_df):
    # Initialize lists for discount factors
    disc_factor_bop = [1.0]  # Beginning of period discount factor
    disc_factor_eop = [1 / (1 + rfr_lookup_df['RiskFree_perMonth'][0])]  # End of period discount factor

    # Calculate the discount factors for each row
    for i in range(1, len(rfr_lookup_df)):
        disc_factor_bop.append(disc_factor_bop[i-1] / (1 + rfr_lookup_df['RiskFree_perMonth'][i-1]))
        disc_factor_eop.append(disc_factor_eop[i-1] / (1 + rfr_lookup_df['RiskFree_perMonth'][i]))

    # Create a pandas DataFrame with the calculated columns
    discount_factor_df = pd.DataFrame({
        'disc_factor_bop': disc_factor_bop,
        'disc_factor_eop': disc_factor_eop
    })

    return discount_factor_df

'''
POLICY DECREMENT PROJECTION:
    - mortality and lapse rates lookup
    - conversion to monthly decrement rates
    - calculation of policy count as: Number of Policy at End of Period = Num Policy at Start - Num of Death - Num of Lapse
'''

def generate_mortality_rate_table(age_df, gender, mortality_table):
    # Create a dictionary from the mortality_table
    mortality_dict = mortality_table.set_index('Age').to_dict(orient='index')
    
    # Find the maximum age available in the mortality table
    max_age = max(mortality_dict.keys())
    
    # Initialize a list to store the lookup results
    rates = []
    
    # Loop through the ages in age_df
    for age in age_df['Age']:
        if age in mortality_dict:
            rate = mortality_dict[age]['Male Rates'] if gender == 'Male' else mortality_dict[age]['Female Rates']
        else:
            rate = mortality_dict[max_age]['Male Rates'] if gender == 'Male' else mortality_dict[max_age]['Female Rates']
        rates.append(rate)
    
    # Create a pandas DataFrame with the lookup results
    mort_rates_df = pd.DataFrame(rates, columns=['Mortality_Rate_perYear'])

    # Calculate the monthly decrement rates
    mort_rates_df['Mortality_Rate_perMonth'] = 1 - (1 - mort_rates_df['Mortality_Rate_perYear'])**(1/12)
    
    return mort_rates_df

def generate_lapse_rate(pol_year_df, lapse_table):
    # Create a dictionary from the lapse_table
    lapse_dict = lapse_table.set_index('Year')['%'].to_dict()
    
    # Find the maximum year available in the lapse table
    max_year = max(lapse_dict.keys())
    
    # Initialize a list to store the lookup results
    lapse_rates = []
    
    # Loop through the years in pol_year_df
    for year in pol_year_df['Pol_Year']:
        if year in lapse_dict:
            lapse_rate = lapse_dict[year] / 100
        else:
            lapse_rate = lapse_dict[max_year] / 100
        lapse_rates.append(lapse_rate)
    
    # Create a pandas DataFrame with the lookup results
    lapse_rates_df = pd.DataFrame(lapse_rates, columns=['Lapse_Rate_perYear'])

    # Calculate the monthly decrement rates
    lapse_rates_df['Lapse_Rate_perMonth'] = 1 - (1 - lapse_rates_df['Lapse_Rate_perYear'])**(1/12)
    
    return lapse_rates_df

def generate_policy_count_table(pol_month_df, mortality_rates_df, lapse_rates_df):
    # Initialize lists for policy counts
    no_pol_start = [1]  # No_Pol_Start starts with 1
    no_death = []  # To be calculated
    no_lapse = []  # To be calculated
    no_pol_end = []  # To be calculated
    
    # Loop through each year to calculate the policy counts
    for i in range(len(pol_month_df)):
        if i > 0:
            no_pol_start.append(no_pol_end[i-1])
        
        # Calculate No_Death
        death = no_pol_start[i] * mortality_rates_df.loc[i, 'Mortality_Rate_perMonth']
        no_death.append(death)
        
        # Calculate No_Lapse
        lapse = (no_pol_start[i] - death) * lapse_rates_df.loc[i, 'Lapse_Rate_perMonth']
        no_lapse.append(lapse)
        
        # Calculate No_Pol_End
        end = no_pol_start[i] - death - lapse
        no_pol_end.append(end)
    
    # Create a pandas DataFrame with the calculated columns
    policy_count_df = pd.DataFrame({
        'No_Pol_Start': no_pol_start,
        'No_Death': no_death,
        'No_Lapse': no_lapse,
        'No_Pol_End': no_pol_end
    })
    
    return policy_count_df




# test
file_path = './pricing_model.xlsx'
pricing_model_data = read_pricing_model_data(file_path)

POL_YEAR = pricing_model_data['Pol_Year']
AGE = pricing_model_data['Age']
GENDER = pricing_model_data['Gender']
RFR_TABLE = pricing_model_data['Table_RiskFreeRate']
MORT_TABLE = pricing_model_data['Table_Mortality']
LAPSE_TABLE = pricing_model_data['Table_Lapse']


t_index_col = generate_t_index_table()
is_cover_col = generate_is_cover_table(t_index_col, POL_YEAR)
pol_month_col = generate_pol_month_table(t_index_col, is_cover_col)
pol_year_col = generate_pol_year_table(pol_month_col, is_cover_col)
age_col = generate_age_table(pol_year_col, is_cover_col, AGE)

rfr_proj_tab = generate_rfr_table(pol_year_col, RFR_TABLE)
disc_fact_tab = generate_discount_factor_table(rfr_proj_tab)

mort_tab= generate_mortality_rate_table(age_col, GENDER, MORT_TABLE)
lapse_tab = generate_lapse_rate(pol_year_col, LAPSE_TABLE)
pol_count_proj_table =  generate_policy_count_table(pol_month_col, mort_tab, lapse_tab)

print(pol_count_proj_table.head())

# # proj_df = append_dataframes([t_index_col, is_cover_col, pol_month_col, pol_year_col, age_col])