"""
Table 2 Replication: Effect of defection messaging on fatalities
Simple version using statsmodels
Authors: Armand et al.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data():
    """Load and prepare the regression data"""
    try:
        df = pd.read_stata('Radio_LRA_DB125.dta')
        return df
    except FileNotFoundError:
        print("Data file not found: Radio_LRA_DB125.dta")
        return None

def run_fixed_effects_regression(df, dependent_var, independent_vars):
    """Run fixed effects regression using statsmodels"""
    
    # Prepare data
    y = df[dependent_var].astype(float)
    X = df[independent_vars].astype(float)
    
    # Add constant
    X = sm.add_constant(X)
    
    # Add entity fixed effects (cell_id)
    entity_dummies = pd.get_dummies(df['cell_id'], prefix='cell', drop_first=True)
    X = pd.concat([X, entity_dummies], axis=1)
    
    # Run regression
    model = sm.OLS(y, X)
    results = model.fit(cov_type='cluster', cov_kwds={'groups': df['cell_id']})
    
    return results

def main():
    """Main replication function"""
    
    # Load data
    df = load_and_prepare_data()
    if df is None:
        return
    
    # Filter data for year > 2007
    df_filtered = df[df['year'] > 2007].copy()
    
    # Define dependent variables (LRA fatalities)
    dependent_vars = ['lnC_LRAfatalities', 'lnA_LRAfatalities', 'lnB_LRAfatalities', 'ln_LRAfatalities']
    available_dep_vars = [var for var in dependent_vars if var in df_filtered.columns]
    
    # Define control variables
    dist_controls = ['bdist3', 'mean_dist', 'med_dist', 'min_dist']
    available_dist_controls = [var for var in dist_controls if var in df_filtered.columns]
    
    year_dummies = [col for col in df_filtered.columns if col.startswith('year_')]
    
    trend_controls = ['ruggedyear', 'nlightsyear', 'popyear', 'urban_gcyear', 'forest_gcyear', 
                     'CARyear', 'DRCyear', 'UGAyear', 'SSDyear']
    available_trend_controls = [var for var in trend_controls if var in df_filtered.columns]
    
    # Main treatment variable
    main_treatment = 'messaging'
    
    # Alternative intensity measures
    intensity_vars = ['stdnintensity', 'pctmessaging']
    available_intensity_vars = [var for var in intensity_vars if var in df_filtered.columns]
    
    # Results storage
    results_summary = {}
    
    # Run regressions for each dependent variable
    for dep_var in available_dep_vars:
        results_summary[dep_var] = {}
        
        # Specification 1: Benchmark
        if main_treatment in df_filtered.columns:
            controls_1 = available_dist_controls + available_trend_controls
            
            try:
                results_1 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [main_treatment] + controls_1)
                
                results_summary[dep_var]['benchmark'] = {
                    'treatment_coef': results_1.params[main_treatment],
                    'treatment_se': results_1.bse[main_treatment],
                    'r2': results_1.rsquared,
                    'nobs': results_1.nobs
                }
            except Exception as e:
                print(f"Error in {dep_var} benchmark: {e}")
        
        # Specification 2: Basic controls
        if main_treatment in df_filtered.columns and year_dummies:
            controls_2 = available_dist_controls + year_dummies
            
            try:
                results_2 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [main_treatment] + controls_2)
                
                results_summary[dep_var]['basic'] = {
                    'treatment_coef': results_2.params[main_treatment],
                    'treatment_se': results_2.bse[main_treatment],
                    'r2': results_2.rsquared,
                    'nobs': results_2.nobs
                }
            except Exception as e:
                print(f"Error in {dep_var} basic: {e}")
        
        # Specification 3: Basic and additional controls
        if main_treatment in df_filtered.columns and year_dummies:
            controls_3 = available_dist_controls + year_dummies + available_trend_controls
            
            try:
                results_3 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [main_treatment] + controls_3)
                
                results_summary[dep_var]['basic_additional'] = {
                    'treatment_coef': results_3.params[main_treatment],
                    'treatment_se': results_3.bse[main_treatment],
                    'r2': results_3.rsquared,
                    'nobs': results_3.nobs
                }
            except Exception as e:
                print(f"Error in {dep_var} basic_additional: {e}")
        
        # Alternative intensity measures
        for intensity_var in available_intensity_vars:
            controls_intensity = available_dist_controls + available_trend_controls
            
            try:
                results_intensity = run_fixed_effects_regression(df_filtered, dep_var, 
                                                               [intensity_var] + controls_intensity)
                
                results_summary[dep_var][f'intensity_{intensity_var}'] = {
                    'treatment_coef': results_intensity.params[intensity_var],
                    'treatment_se': results_intensity.bse[intensity_var],
                    'r2': results_intensity.rsquared,
                    'nobs': results_intensity.nobs
                }
            except Exception as e:
                print(f"Error in {dep_var} {intensity_var}: {e}")
    
    # Results table
    print("=" * 80)
    print("TABLE 2 REPLICATION RESULTS - ARMAND ET AL.")
    print("=" * 80)
    print("Dependent Variable | Specification | Treatment | R²    | N")
    print("-" * 80)
    
    for dep_var in available_dep_vars:
        for spec in ['benchmark', 'basic', 'basic_additional']:
            if spec in results_summary[dep_var]:
                result = results_summary[dep_var][spec]
                treatment_str = f"{result['treatment_coef']:.3f} ({result['treatment_se']:.3f})"
                print(f"{dep_var:18} | {spec:13} | {treatment_str:10} | {result['r2']:.3f} | {result['nobs']}")
        
        # Alternative intensity measures
        for intensity_var in available_intensity_vars:
            spec = f'intensity_{intensity_var}'
            if spec in results_summary[dep_var]:
                result = results_summary[dep_var][spec]
                treatment_str = f"{result['treatment_coef']:.3f} ({result['treatment_se']:.3f})"
                print(f"{dep_var:18} | {spec:13} | {treatment_str:10} | {result['r2']:.3f} | {result['nobs']}")
    
    print("=" * 80)

if __name__ == "__main__":
    main() 