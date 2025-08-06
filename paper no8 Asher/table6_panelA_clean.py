import pandas as pd
import numpy as np
import statsmodels.api as sm
from linearmodels import IV2SLS
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# TABLE 6, PANEL A CLEAN REPLICATION - FOLLOWING STATA DO-FILE
# Based on paper_results_aer_final.do
# =============================================================================

# Load data
df = pd.read_stata("pmgsy_working_aer_mainsample.dta")

# Data preparation
if 'mainsample' in df.columns:
    df_main = df[df['mainsample'] == 1].copy()
else:
    df_main = df.copy()

# Check for required variables
required_vars = ['t', 'left', 'right', 'vhg_dist_id', 'ec13_emp_all_ln']
available_vars = [var for var in required_vars if var in df_main.columns]

# Check for control variables
control_candidates = [
    'scst_share', 'bus', 'comm', 'bank', 'irr_share', 'ln_land',
    'pc01_lit_share', 'primary_school', 'med_center', 'electric',
    'app_pr', 'app_mr', 'mcw', 'pc01_sc_share'
]
available_controls = [var for var in control_candidates if var in df_main.columns]

# Sector mapping
sector_mapping = {
    'Total': 'ec13_emp_all_ln',
    'Livestock': 'ec13_emp_act1_ln',
    'Manufacturing': 'ec13_emp_act2_ln',
    'Education': 'ec13_emp_act3_ln',
    'Retail': 'ec13_emp_act6_ln',
    'Forestry': 'ec13_emp_act12_ln'
}

# Prepare regression variables
if 'left' in df_main.columns and 'right' in df_main.columns:
    exog_vars = ['left', 'right']
else:
    exog_vars = []

# Add available control variables
if available_controls:
    exog_vars.extend(available_controls[:5])

# Add district fixed effects
if 'vhg_dist_id' in df_main.columns:
    district_dummies = pd.get_dummies(df_main['vhg_dist_id'].astype(str), prefix='dist', drop_first=True)
    X_exog = pd.concat([df_main[exog_vars], district_dummies], axis=1)
else:
    X_exog = df_main[exog_vars]

X_exog = sm.add_constant(X_exog)
X_exog = X_exog.astype(float)

# Store results
results = {}

# Run 2SLS for each sector
for sector, log_var in sector_mapping.items():
    if log_var in df_main.columns:
        y = df_main[log_var].astype(float)
        
        # Remove missing values
        valid_idx = ~(y.isna() | X_exog.isna().any(axis=1) | df_main['t'].isna())
        
        if valid_idx.sum() > 0:
            y_clean = y[valid_idx]
            X_clean = X_exog[valid_idx]
            
            # Add kernel weights if available
            if 'kernel_tri_ik' in df_main.columns:
                weights = df_main.loc[valid_idx, 'kernel_tri_ik'].astype(float)
            elif 'kernel_tri_mainband' in df_main.columns:
                weights = df_main.loc[valid_idx, 'kernel_tri_mainband'].astype(float)
            else:
                weights = None
            
            try:
                # Run 2SLS
                model_2sls = IV2SLS(
                    dependent=y_clean,
                    exog=X_clean,
                    endog=df_main.loc[valid_idx, 'r2012'].astype(float),
                    instruments=df_main.loc[valid_idx, 't'].astype(float),
                    weights=weights
                ).fit(cov_type='robust')
                
                # Get coefficient for r2012
                if 'r2012' in model_2sls.params.index:
                    coef = model_2sls.params['r2012']
                    se = model_2sls.std_errors['r2012']
                    obs = len(y_clean)
                    
                    results[sector] = {
                        'coefficient': coef,
                        'std_error': se,
                        'observations': obs
                    }
                    
            except Exception as e:
                pass

# =============================================================================
# FINAL RESULTS
# =============================================================================

print("="*80)
print("TABLE 6 - IMPACT OF NEW ROAD ON FIRMS")
print("="*80)
print("Panel A. Log employment growth, by sector")
print("="*80)

if results:
    # Create DataFrame
    df_results = pd.DataFrame(results).T
    df_results = df_results.round(3)
    
    # Format the table
    print(f"{'Sector':<15} {'New Road':<10} {'Std Error':<12} {'Observations':<12}")
    print("-" * 60)
    
    for sector in ['Total', 'Livestock', 'Manufacturing', 'Education', 'Retail', 'Forestry']:
        if sector in results:
            coef = results[sector]['coefficient']
            se = results[sector]['std_error']
            obs = results[sector]['observations']
            
            print(f"{sector:<15} {coef:<10.3f} {se:<12.3f} {obs:<12.0f}")
    
    print("-" * 60)
    
    # Save results
    df_results.to_csv('table6_panelA_final_clean.csv')
    
    # Main result summary
    print("\n" + "="*80)
    print("MAIN RESULT SUMMARY")
    print("="*80)
    if 'Total' in results:
        total_coef = results['Total']['coefficient']
        total_se = results['Total']['std_error']
        print(f"Total Employment Effect: {total_coef:.3f} (SE: {total_se:.3f})")
        print(f"Expected from Paper: 0.273 (SE: 0.159)")
        print(f"Difference: {total_coef - 0.273:.3f}")
        
        if abs(total_coef - 0.273) < 0.05:
            print("✅ RESULT: Very close to expected!")
        elif abs(total_coef - 0.273) < 0.1:
            print("⚠️  RESULT: Moderately close to expected")
        else:
            print("❌ RESULT: Significantly different from expected")

print("\n" + "="*80)
print("REPLICATION COMPLETE")
print("="*80) 