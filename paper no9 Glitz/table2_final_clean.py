"""
Industrial Espionage and Productivity - Table 2 Final Clean Replication
Authors: Albrecht Glitz and Erik Meyersson (2019)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data():
    """Load and prepare the regression data"""
    try:
        df = pd.read_stata('regdata_3_yes_.33_.06.dta')
        return df
    except FileNotFoundError:
        print("Data file not found")
        return None

def run_ols_regression(df, dependent_var, independent_vars, weights=None, cluster_var=None):
    """Run OLS regression with clustering and weights"""
    y = df[dependent_var].astype(float)
    X = df[independent_vars].astype(float)
    X = sm.add_constant(X)
    
    if weights is not None:
        w = df[weights].astype(float)
        model = sm.WLS(y, X, weights=w)
    else:
        model = sm.OLS(y, X)
    
    results = model.fit(cov_type='cluster', cov_kwds={'groups': df[cluster_var]})
    return results

def main():
    """Main replication function"""
    
    # Load data
    df = load_and_prepare_data()
    if df is None:
        return
    
    # Filter data
    df_filtered = df.dropna(subset=['c3difflnTFP', 'c3diffln_gvapc'])
    
    # Set up variables
    espionage_var = 'inf_gva'
    patents_var = 'diff_patents_gva'
    
    # Create fixed effects
    year_dummies = pd.get_dummies(df_filtered['year'], prefix='yd', drop_first=True)
    branch_dummies = pd.get_dummies(df_filtered['branch'], prefix='br', drop_first=True)
    df_filtered = pd.concat([df_filtered, year_dummies, branch_dummies], axis=1)
    fe_vars = [col for col in df_filtered.columns if col.startswith(('yd_', 'br_'))]
    
    # Loop over outcomes
    outcomes = ['difflnTFP', 'diffln_gvapc']
    results_summary = {}
    
    for y in outcomes:
        if y == "difflnTFP":
            ylabel = "TFP"
            dependent_var = 'c3difflnTFP'
        else:
            ylabel = "GVAPC"
            dependent_var = 'c3diffln_gvapc'
        
        results_summary[y] = {}
        
        # Column 1: Unconditional
        X_vars_1 = [espionage_var] + fe_vars
        results_1 = run_ols_regression(df_filtered, dependent_var, X_vars_1, 
                                     weights='weight_workers', cluster_var='branch')
        
        results_summary[y]['col1'] = {
            'espionage_coef': results_1.params[espionage_var],
            'espionage_se': results_1.bse[espionage_var],
            'r2': results_1.rsquared,
            'nobs': results_1.nobs
        }
        
        # Column 2: With Patent Gap
        X_vars_2 = [espionage_var, patents_var] + fe_vars
        results_2 = run_ols_regression(df_filtered, dependent_var, X_vars_2, 
                                     weights='weight_workers', cluster_var='branch')
        
        results_summary[y]['col2'] = {
            'espionage_coef': results_2.params[espionage_var],
            'espionage_se': results_2.bse[espionage_var],
            'patents_coef': results_2.params[patents_var],
            'patents_se': results_2.bse[patents_var],
            'r2': results_2.rsquared,
            'nobs': results_2.nobs
        }
        
        # Column 3: With Patent Gap and Lagged Gap
        X_vars_3 = [espionage_var, patents_var, y] + fe_vars
        results_3 = run_ols_regression(df_filtered, dependent_var, X_vars_3, 
                                     weights='weight_workers', cluster_var='branch')
        
        results_summary[y]['col3'] = {
            'espionage_coef': results_3.params[espionage_var],
            'espionage_se': results_3.bse[espionage_var],
            'patents_coef': results_3.params[patents_var],
            'patents_se': results_3.bse[patents_var],
            'lagged_coef': results_3.params[y],
            'lagged_se': results_3.bse[y],
            'r2': results_3.rsquared,
            'nobs': results_3.nobs
        }
    
    # Results table
    print("=" * 80)
    print("TABLE 2 REPLICATION RESULTS - GLITZ & MEYERSSON (2019)")
    print("=" * 80)
    print("Outcome | Column | Espionage | Patents Gap | Lagged Gap | R²    | N")
    print("-" * 80)
    
    for y in outcomes:
        ylabel = "TFP" if y == "difflnTFP" else "GVAPC"
        for col in ['col1', 'col2', 'col3']:
            result = results_summary[y][col]
            espionage_str = f"{result['espionage_coef']:.3f} ({result['espionage_se']:.3f})"
            patents_str = f"{result['patents_coef']:.3f} ({result['patents_se']:.3f})" if 'patents_coef' in result else "N/A"
            lagged_str = f"{result['lagged_coef']:.3f} ({result['lagged_se']:.3f})" if 'lagged_coef' in result else "N/A"
            
            print(f"{ylabel:7} | {col[-1]:6} | {espionage_str:10} | {patents_str:11} | {lagged_str:10} | {result['r2']:.2f} | {result['nobs']:.0f}")
    
    print("=" * 80)

if __name__ == "__main__":
    main() 