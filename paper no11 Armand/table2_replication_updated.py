"""
Table 2 Replication: Effect of defection messaging on fatalities
Python equivalent of the Stata code for Table 2
Authors: Armand et al.

This script replicates the complete Table 2 specification including:
- Different sets of controls
- Alternative intensity of messaging measures
- Fixed effects regression with robust standard errors
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from linearmodels import PanelOLS
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

def run_fixed_effects_regression(df, dependent_var, independent_vars, entity_effects=True):
    """Run fixed effects regression (equivalent to Stata's xtreg with fe robust)"""
    
    # Prepare data
    y = df[dependent_var].astype(float)
    X = df[independent_vars].astype(float)
    
    # Create panel data structure
    panel_data = pd.DataFrame({
        'y': y,
        'entity': df['cell_id'],
        'time': df['year']
    })
    
    # Add independent variables
    for col in X.columns:
        panel_data[col] = X[col]
    
    # Set panel structure
    panel_data = panel_data.set_index(['entity', 'time'])
    
    # Run fixed effects regression
    if entity_effects:
        model = PanelOLS.from_formula('y ~ ' + ' + '.join(independent_vars), data=panel_data, 
                                     entity_effects=True)
    else:
        model = PanelOLS.from_formula('y ~ ' + ' + '.join(independent_vars), data=panel_data)
    
    results = model.fit(cov_type='robust')
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
    
    # Check which dependent variables exist
    available_dep_vars = [var for var in dependent_vars if var in df_filtered.columns]
    
    # Define control variables based on data exploration
    # Distance controls
    dist_controls = ['bdist3', 'mean_dist', 'med_dist', 'min_dist']
    available_dist_controls = [var for var in dist_controls if var in df_filtered.columns]
    
    # Year dummies
    year_dummies = [col for col in df_filtered.columns if col.startswith('year_')]
    
    # Variable-specific trends
    trend_controls = ['ruggedyear', 'nlightsyear', 'popyear', 'urban_gcyear', 'forest_gcyear', 
                     'CARyear', 'DRCyear', 'UGAyear', 'SSDyear']
    available_trend_controls = [var for var in trend_controls if var in df_filtered.columns]
    
    # Main treatment variable (messaging)
    main_treatment = 'messaging'  # Main messaging variable
    
    # Alternative intensity measures
    intensity_vars = ['stdnintensity', 'pctmessaging']
    available_intensity_vars = [var for var in intensity_vars if var in df_filtered.columns]
    
    # Circular coverage
    circ_controls = ['circcovered']
    available_circ_controls = [var for var in circ_controls if var in df_filtered.columns]
    
    # Results storage
    results_summary = {}
    
    # Run regressions for each dependent variable
    for dep_var in available_dep_vars:
        print(f"\n{'='*60}")
        print(f"DEPENDENT VARIABLE: {dep_var}")
        print(f"{'='*60}")
        
        results_summary[dep_var] = {}
        
        # Specification 1: Benchmark (all controls)
        if main_treatment in df_filtered.columns:
            print(f"\n--- Specification 1: Benchmark ---")
            controls_1 = available_dist_controls + available_trend_controls
            
            try:
                results_1 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [main_treatment] + controls_1)
                
                results_summary[dep_var]['benchmark'] = {
                    'treatment_coef': results_1.params[main_treatment],
                    'treatment_se': results_1.std_errors[main_treatment],
                    'r2': results_1.rsquared,
                    'nobs': results_1.nobs
                }
                
                print(f"Treatment: {results_1.params[main_treatment]:.3f} ({results_1.std_errors[main_treatment]:.3f})")
                print(f"R²: {results_1.rsquared:.3f}, N: {results_1.nobs}")
                
            except Exception as e:
                print(f"Error in benchmark specification: {e}")
        
        # Specification 2: Basic controls
        if main_treatment in df_filtered.columns and year_dummies:
            print(f"\n--- Specification 2: Basic controls ---")
            controls_2 = available_dist_controls + year_dummies
            
            try:
                results_2 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [main_treatment] + controls_2)
                
                results_summary[dep_var]['basic'] = {
                    'treatment_coef': results_2.params[main_treatment],
                    'treatment_se': results_2.std_errors[main_treatment],
                    'r2': results_2.rsquared,
                    'nobs': results_2.nobs
                }
                
                print(f"Treatment: {results_2.params[main_treatment]:.3f} ({results_2.std_errors[main_treatment]:.3f})")
                print(f"R²: {results_2.rsquared:.3f}, N: {results_2.nobs}")
                
            except Exception as e:
                print(f"Error in basic controls specification: {e}")
        
        # Specification 3: Basic and additional controls
        if main_treatment in df_filtered.columns and year_dummies:
            print(f"\n--- Specification 3: Basic and additional controls ---")
            controls_3 = available_dist_controls + year_dummies + available_trend_controls
            
            try:
                results_3 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [main_treatment] + controls_3)
                
                results_summary[dep_var]['basic_additional'] = {
                    'treatment_coef': results_3.params[main_treatment],
                    'treatment_se': results_3.std_errors[main_treatment],
                    'r2': results_3.rsquared,
                    'nobs': results_3.nobs
                }
                
                print(f"Treatment: {results_3.params[main_treatment]:.3f} ({results_3.std_errors[main_treatment]:.3f})")
                print(f"R²: {results_3.rsquared:.3f}, N: {results_3.nobs}")
                
            except Exception as e:
                print(f"Error in basic and additional controls specification: {e}")
        
        # Specification 4: Benchmark + circular coverage
        if main_treatment in df_filtered.columns and available_circ_controls:
            print(f"\n--- Specification 4: Benchmark + circular coverage ---")
            controls_4 = available_dist_controls + available_trend_controls + available_circ_controls
            
            try:
                results_4 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [main_treatment] + controls_4)
                
                results_summary[dep_var]['circular_coverage'] = {
                    'treatment_coef': results_4.params[main_treatment],
                    'treatment_se': results_4.std_errors[main_treatment],
                    'r2': results_4.rsquared,
                    'nobs': results_4.nobs
                }
                
                print(f"Treatment: {results_4.params[main_treatment]:.3f} ({results_4.std_errors[main_treatment]:.3f})")
                print(f"R²: {results_4.rsquared:.3f}, N: {results_4.nobs}")
                
            except Exception as e:
                print(f"Error in circular coverage specification: {e}")
        
        # Alternative intensity measures
        for intensity_var in available_intensity_vars:
            print(f"\n--- Alternative intensity: {intensity_var} ---")
            controls_intensity = available_dist_controls + available_trend_controls
            
            try:
                results_intensity = run_fixed_effects_regression(df_filtered, dep_var, 
                                                               [intensity_var] + controls_intensity)
                
                results_summary[dep_var][f'intensity_{intensity_var}'] = {
                    'treatment_coef': results_intensity.params[intensity_var],
                    'treatment_se': results_intensity.std_errors[intensity_var],
                    'r2': results_intensity.rsquared,
                    'nobs': results_intensity.nobs
                }
                
                print(f"Treatment: {results_intensity.params[intensity_var]:.3f} ({results_intensity.std_errors[intensity_var]:.3f})")
                print(f"R²: {results_intensity.rsquared:.3f}, N: {results_intensity.nobs}")
                
            except Exception as e:
                print(f"Error in {intensity_var} specification: {e}")
    
    # Final summary table
    print(f"\n{'='*80}")
    print("FINAL SUMMARY TABLE - TABLE 2 REPLICATION")
    print(f"{'='*80}")
    print("Dependent Variable | Specification | Treatment | R²    | N")
    print("-" * 80)
    
    for dep_var in available_dep_vars:
        for spec in ['benchmark', 'basic', 'basic_additional', 'circular_coverage']:
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
    
    print(f"{'='*80}")
    print("REPLICATION COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 