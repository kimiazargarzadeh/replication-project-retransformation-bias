"""
Paper No. 18 Replication - Final Clean Version
PAC and Charity Contributions Analysis
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

def run_regression(df, dependent_var, independent_var, fe_vars):
    """Run regression with multiple fixed effects using within-transformation"""
    
    # Prepare data
    data = df[[dependent_var, independent_var] + fe_vars].dropna()
    
    # Apply within-transformation for all fixed effects sequentially
    y_demeaned = data[dependent_var].copy()
    x_demeaned = data[independent_var].copy()
    
    for fe_var in fe_vars:
        y_demeaned = data.groupby(fe_var)[dependent_var].transform(lambda x: x - x.mean())
        x_demeaned = data.groupby(fe_var)[independent_var].transform(lambda x: x - x.mean())
        # Update the data for next iteration
        data = data.copy()
        data[dependent_var] = y_demeaned
        data[independent_var] = x_demeaned
    
    # Run regression
    X = sm.add_constant(x_demeaned.astype(float))
    y = y_demeaned.astype(float)
    
    model = sm.OLS(y, X)
    results = model.fit(cov_type='cluster', cov_kwds={'groups': data[fe_vars[0]]})
    
    return results

def main():
    """Main replication function"""
    
    # Load data
    df = pd.read_stata('PAC_charity.dta')
    
    # Define fixed effects variables
    fe_vars = ['EIN_state_cd_id', 'state_cd_congress_id', 'EIN_congress_id']
    
    # Run PAC regression (Table 3 Column 7)
    pac_results = run_regression(df, 'lnPACamount', 'lnrep_issue_state_cd', fe_vars)
    pac_coeff = pac_results.params['lnrep_issue_state_cd']
    pac_se = pac_results.bse['lnrep_issue_state_cd']
    
    # Run Charity regression (Table 4 Column 7)
    charity_results = run_regression(df, 'lncharamount', 'lnrep_issue_state_cd', fe_vars)
    charity_coeff = charity_results.params['lnrep_issue_state_cd']
    charity_se = charity_results.bse['lnrep_issue_state_cd']
    
    # Calculate political motivation
    ratio = charity_coeff / pac_coeff
    political_share = ratio * 100
    
    # Results
    print("=" * 60)
    print("TABLE 3 & 4 - column 7 -REPLICATION RESULTS")
    print("=" * 60)
    print(f"PAC Elasticity: {pac_coeff:.3f} (SE: {pac_se:.3f})")
    print(f"Charity Elasticity: {charity_coeff:.3f} (SE: {charity_se:.3f})")
    print(f"Political CSR Share: {political_share:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main() 