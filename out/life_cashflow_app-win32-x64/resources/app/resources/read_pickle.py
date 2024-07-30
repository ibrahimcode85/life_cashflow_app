import pandas as pd

file_path = r"C:\Users\ibrah\OneDrive\Documents\Projects\life_cashflow_app\output\pricing_model_py_output.pkl"
file_path2 = r"C:\Users\ibrah\OneDrive\Documents\Projects\life_cashflow_app\output\pricing_model_py_output_pv_results.pkl"
df = pd.read_pickle(file_path)
df2 = pd.read_pickle(file_path2)
print("done read.")
