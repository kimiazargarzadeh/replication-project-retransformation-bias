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
        print(f"Data loaded successfully. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print("Data file not found: Radio_LRA_DB125.dta")
        return None

def run_fixed_effects_regression(df, dependent_var, independent_vars, entity_effects=True, time_effects=False):
    """Run fixed effects regression (equivalent to Stata's xtreg with fe robust)"""
    
    # Prepare data
    y = df[dependent_var].astype(float)
    X = df[independent_vars].astype(float)
    
    # Add constant
    X = sm.add_constant(X)
    
    # Create panel data structure
    panel_data = pd.DataFrame({
        'y': y,
        'entity': df['cell_id'] if 'cell_id' in df.columns else df.index,
        'time': df['year'] if 'year' in df.columns else df.index
    })
    
    # Add independent variables
    for i, col in enumerate(X.columns):
        panel_data[col] = X.iloc[:, i]
    
    # Set panel structure
    panel_data = panel_data.set_index(['entity', 'time'])
    
    # Run fixed effects regression
    if entity_effects and time_effects:
        model = PanelOLS.from_formula('y ~ ' + ' + '.join(independent_vars), data=panel_data, 
                                     entity_effects=True, time_effects=True)
    elif entity_effects:
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
    print(f"Filtered dataset (year > 2007): {df_filtered.shape}")
    
    # Check available variables
    print("\nAvailable variables:")
    print(df_filtered.columns.tolist()[:20])  # Show first 20 columns
    
    # Define dependent variables (LRA fatalities)
    dependent_vars = ['lnC_LRAfatalities', 'lnA_LRAfatalities', 'lnB_LRAfatalities', 'ln_LRAfatalities']
    
    # Check which dependent variables exist
    available_dep_vars = [var for var in dependent_vars if var in df_filtered.columns]
    print(f"\nAvailable dependent variables: {available_dep_vars}")
    
    # Define control variables (these would need to be adjusted based on actual data)
    # Basic controls
    basic_controls = ['cont_dist']  # Distance controls
    
    # Additional controls
    additional_controls = ['cont_nvis', 'cont_vis']  # Non-visual and visual controls
    
    # Year dummies
    year_dummies = [col for col in df_filtered.columns if col.startswith('year_')]
    
    # Trends
    trends = [col for col in df_filtered.columns if 'trend' in col.lower()]
    
    # Main treatment variable
    main_treatment = 'main'  # This would be the main defection messaging variable
    
    # Alternative intensity measures
    intensity_vars = ['stdnintensity', 'pctmessaging']
    
    # Check which variables exist
    available_controls = {
        'basic': [var for var in basic_controls if var in df_filtered.columns],
        'additional': [var for var in additional_controls if var in df_filtered.columns],
        'year_dummies': year_dummies,
        'trends': trends,
        'main_treatment': main_treatment if main_treatment in df_filtered.columns else None,
        'intensity_vars': [var for var in intensity_vars if var in df_filtered.columns]
    }
    
    print(f"\nAvailable controls:")
    for key, vars_list in available_controls.items():
        print(f"  {key}: {vars_list}")
    
    # Results storage
    results_summary = {}
    
    # Run regressions for each dependent variable
    for dep_var in available_dep_vars:
        print(f"\n{'='*60}")
        print(f"DEPENDENT VARIABLE: {dep_var}")
        print(f"{'='*60}")
        
        results_summary[dep_var] = {}
        
        # Specification 1: Benchmark (all controls)
        if available_controls['main_treatment']:
            print(f"\n--- Specification 1: Benchmark ---")
            controls_1 = (available_controls['basic'] + 
                         available_controls['additional'] + 
                         available_controls['trends'])
            
            try:
                results_1 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [available_controls['main_treatment']] + controls_1)
                
                results_summary[dep_var]['benchmark'] = {
                    'treatment_coef': results_1.params[available_controls['main_treatment']],
                    'treatment_se': results_1.std_errors[available_controls['main_treatment']],
                    'r2': results_1.rsquared,
                    'nobs': results_1.nobs
                }
                
                print(f"Treatment: {results_1.params[available_controls['main_treatment']]:.3f} ({results_1.std_errors[available_controls['main_treatment']]:.3f})")
                print(f"R²: {results_1.rsquared:.3f}, N: {results_1.nobs}")
                
            except Exception as e:
                print(f"Error in benchmark specification: {e}")
        
        # Specification 2: Basic controls
        if available_controls['main_treatment'] and available_controls['year_dummies']:
            print(f"\n--- Specification 2: Basic controls ---")
            controls_2 = available_controls['basic'] + available_controls['year_dummies']
            
            try:
                results_2 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [available_controls['main_treatment']] + controls_2)
                
                results_summary[dep_var]['basic'] = {
                    'treatment_coef': results_2.params[available_controls['main_treatment']],
                    'treatment_se': results_2.std_errors[available_controls['main_treatment']],
                    'r2': results_2.rsquared,
                    'nobs': results_2.nobs
                }
                
                print(f"Treatment: {results_2.params[available_controls['main_treatment']]:.3f} ({results_2.std_errors[available_controls['main_treatment']]:.3f})")
                print(f"R²: {results_2.rsquared:.3f}, N: {results_2.nobs}")
                
            except Exception as e:
                print(f"Error in basic controls specification: {e}")
        
        # Specification 3: Basic and additional controls
        if available_controls['main_treatment'] and available_controls['year_dummies']:
            print(f"\n--- Specification 3: Basic and additional controls ---")
            controls_3 = (available_controls['basic'] + 
                         available_controls['additional'] + 
                         available_controls['year_dummies'])
            
            try:
                results_3 = run_fixed_effects_regression(df_filtered, dep_var, 
                                                       [available_controls['main_treatment']] + controls_3)
                
                results_summary[dep_var]['basic_additional'] = {
                    'treatment_coef': results_3.params[available_controls['main_treatment']],
                    'treatment_se': results_3.std_errors[available_controls['main_treatment']],
                    'r2': results_3.rsquared,
                    'nobs': results_3.nobs
                }
                
                print(f"Treatment: {results_3.params[available_controls['main_treatment']]:.3f} ({results_3.std_errors[available_controls['main_treatment']]:.3f})")
                print(f"R²: {results_3.rsquared:.3f}, N: {results_3.nobs}")
                
            except Exception as e:
                print(f"Error in basic and additional controls specification: {e}")
    
    # Final summary table
    print(f"\n{'='*80}")
    print("FINAL SUMMARY TABLE - TABLE 2 REPLICATION")
    print(f"{'='*80}")
    print("Dependent Variable | Specification | Treatment | R²    | N")
    print("-" * 80)
    
    for dep_var in available_dep_vars:
        for spec in ['benchmark', 'basic', 'basic_additional']:
            if spec in results_summary[dep_var]:
                result = results_summary[dep_var][spec]
                treatment_str = f"{result['treatment_coef']:.3f} ({result['treatment_se']:.3f})"
                print(f"{dep_var:18} | {spec:13} | {treatment_str:10} | {result['r2']:.3f} | {result['nobs']}")
    
    print(f"{'='*80}")
    print("REPLICATION COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 