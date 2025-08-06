import pandas as pd
import numpy as np
import statsmodels.api as sm
from linearmodels import IV2SLS
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# IV REGRESSION REPLICATION - Asher & Novosad (2020) - FIXED VERSION
# =============================================================================

print("Loading PMGSY main sample data...")
df = pd.read_stata("pmgsy_working_aer_mainsample.dta")

print(f"Data loaded: {len(df)} observations, {len(df.columns)} variables")

# Check key variables
key_vars = ['r2012', 't', 'left', 'right', 'mainsample', 'vhg_dist_id', 'kernel_tri_mainband']
available_vars = [var for var in key_vars if var in df.columns]
print(f"Available key variables: {available_vars}")

# Check family indices
family_indices = ['transport', 'occupation', 'firms', 'agriculture', 'consumption']
available_indices = []
for family in family_indices:
    main_var = f'{family}_index_andrsn'
    spillover_var = f'{family}_index_andrsn_5k'
    if main_var in df.columns:
        available_indices.append(main_var)
    if spillover_var in df.columns:
        available_indices.append(spillover_var)

print(f"Available family indices: {available_indices[:10]}...")

# =============================================================================
# DATA PREPARATION
# =============================================================================

print("\n" + "="*60)
print("DATA PREPARATION")
print("="*60)

# Filter for main sample
if 'mainsample' in df.columns:
    df_main = df[df['mainsample'] == 1].copy()
    print(f"Main sample size: {len(df_main)} (from {len(df)})")
else:
    df_main = df.copy()
    print("No mainsample variable found, using full dataset")

# Check for missing values in key variables
if 'r2012' in df_main.columns:
    print(f"r2012 missing: {df_main['r2012'].isna().sum()}")
if 't' in df_main.columns:
    print(f"t missing: {df_main['t'].isna().sum()}")

# =============================================================================
# FIRST STAGE REGRESSION
# =============================================================================

print("\n" + "="*60)
print("FIRST STAGE REGRESSION")
print("="*60)

if 'r2012' in df_main.columns and 't' in df_main.columns:
    print("Running first stage regression...")
    
    # Prepare variables
    y_fs = df_main['r2012'].astype(float)
    X_vars = ['t']
    
    # Add basic controls if available
    if 'left' in df_main.columns and 'right' in df_main.columns:
        X_vars.extend(['left', 'right'])
        print("Added left, right controls")
    
    # Add district fixed effects if available
    if 'vhg_dist_id' in df_main.columns:
        print("Adding district fixed effects...")
        # Convert district ID to string first to avoid issues
        district_dummies = pd.get_dummies(df_main['vhg_dist_id'].astype(str), prefix='dist', drop_first=True)
        X_fs = pd.concat([df_main[X_vars], district_dummies], axis=1)
    else:
        X_fs = df_main[X_vars]
    
    # Add constant
    X_fs = sm.add_constant(X_fs)
    
    # Ensure all data is numeric
    X_fs = X_fs.astype(float)
    
    # Remove missing values
    valid_idx = ~(y_fs.isna() | X_fs.isna().any(axis=1))
    y_fs_clean = y_fs[valid_idx]
    X_fs_clean = X_fs[valid_idx]
    
    print(f"First stage observations: {len(y_fs_clean)}")
    
    # Add weights if available
    if 'kernel_tri_mainband' in df_main.columns:
        weights = df_main.loc[valid_idx, 'kernel_tri_mainband'].astype(float)
        print("Using kernel weights")
        model_fs = sm.WLS(y_fs_clean, X_fs_clean, weights=weights).fit(cov_type='HC1')
    else:
        print("No weights available, using OLS")
        model_fs = sm.OLS(y_fs_clean, X_fs_clean).fit(cov_type='HC1')
    
    print("\nFirst Stage Results:")
    if 't' in model_fs.params.index:
        print(f"Treatment coefficient (t): {model_fs.params['t']:.4f}")
        print(f"Standard Error: {model_fs.bse['t']:.4f}")
        print(f"P-value: {model_fs.pvalues['t']:.4f}")
        print(f"R-squared: {model_fs.rsquared:.4f}")
        print(f"F-statistic: {model_fs.fvalue:.2f}")
    else:
        print("Warning: 't' not found in first stage results")
else:
    print("Missing required variables for first stage (r2012 or t)")

# =============================================================================
# IV REGRESSION (2SLS) - FAMILY INDICES (LOG LEVELS)
# =============================================================================

print("\n" + "="*60)
print("IV REGRESSION (2SLS) - FAMILY INDICES (LOG LEVELS)")
print("="*60)

# Store results
results = {}

# Prepare exogenous variables (same as first stage)
if 'left' in df_main.columns and 'right' in df_main.columns:
    exog_vars = ['left', 'right']
else:
    exog_vars = []

if 'vhg_dist_id' in df_main.columns:
    district_dummies = pd.get_dummies(df_main['vhg_dist_id'].astype(str), prefix='dist', drop_first=True)
    X_exog = pd.concat([df_main[exog_vars], district_dummies], axis=1)
else:
    X_exog = df_main[exog_vars]

X_exog = sm.add_constant(X_exog)
X_exog = X_exog.astype(float)

# Run 2SLS for each family index
for family in family_indices:
    print(f"\n--- {family.upper()} INDEX ---")
    
    # Main effect
    main_var = f'{family}_index_andrsn'
    if main_var in df_main.columns:
        print(f"Running 2SLS for log({main_var})...")
        
        # Create log variable (add small constant to avoid log(0))
        y_raw = df_main[main_var].astype(float)
        y = np.log(y_raw + 1)  # log transformation
        
        # Remove missing values
        valid_idx = ~(y.isna() | X_exog.isna().any(axis=1) | df_main['t'].isna())
        
        if valid_idx.sum() > 0:
            y_clean = y[valid_idx]
            X_clean = X_exog[valid_idx]
            
            # Add weights if available
            if 'kernel_tri_mainband' in df_main.columns:
                weights = df_main.loc[valid_idx, 'kernel_tri_mainband'].astype(float)
            else:
                weights = None
            
            try:
                # Run 2SLS with proper syntax
                # Endogenous: r2012, Instruments: t, Exogenous: X_clean
                model_2sls = IV2SLS(
                    dependent=y_clean,
                    exog=X_clean,
                    endog=df_main.loc[valid_idx, 'r2012'].astype(float),
                    instruments=df_main.loc[valid_idx, 't'].astype(float),
                    weights=weights
                ).fit(cov_type='robust')
                
                # Get coefficient for r2012 (endogenous variable)
                if 'r2012' in model_2sls.params.index:
                    coef = model_2sls.params['r2012']
                    se = model_2sls.std_errors['r2012']
                    pval = model_2sls.pvalues['r2012']
                    
                    results[f'log_{main_var}'] = {
                        'coefficient': coef,
                        'std_error': se,
                        'p_value': pval,
                        'observations': len(y_clean)
                    }
                    
                    print(f"Log({main_var}) on r2012:")
                    print(f"Coefficient: {coef:.4f}")
                    print(f"Standard Error: {se:.4f}")
                    print(f"P-value: {pval:.4f}")
                    print(f"Observations: {len(y_clean)}")
                else:
                    print(f"Warning: r2012 not found in results for {main_var}")
                    
            except Exception as e:
                print(f"Error running 2SLS for {main_var}: {e}")
        else:
            print(f"No valid observations for {main_var}")
    else:
        print(f"Variable {main_var} not found in dataset")
    
    # Spillover effect (5k)
    spillover_var = f'{family}_index_andrsn_5k'
    if spillover_var in df_main.columns:
        print(f"Running 2SLS for log({spillover_var})...")
        
        # Create log variable
        y_raw = df_main[spillover_var].astype(float)
        y = np.log(y_raw + 1)  # log transformation
        
        valid_idx = ~(y.isna() | X_exog.isna().any(axis=1) | df_main['t'].isna())
        
        if valid_idx.sum() > 0:
            y_clean = y[valid_idx]
            X_clean = X_exog[valid_idx]
            
            if 'kernel_tri_mainband' in df_main.columns:
                weights = df_main.loc[valid_idx, 'kernel_tri_mainband'].astype(float)
            else:
                weights = None
            
            try:
                model_2sls = IV2SLS(
                    dependent=y_clean,
                    exog=X_clean,
                    endog=df_main.loc[valid_idx, 'r2012'].astype(float),
                    instruments=df_main.loc[valid_idx, 't'].astype(float),
                    weights=weights
                ).fit(cov_type='robust')
                
                if 'r2012' in model_2sls.params.index:
                    coef = model_2sls.params['r2012']
                    se = model_2sls.std_errors['r2012']
                    pval = model_2sls.pvalues['r2012']
                    
                    results[f'log_{spillover_var}'] = {
                        'coefficient': coef,
                        'std_error': se,
                        'p_value': pval,
                        'observations': len(y_clean)
                    }
                    
                    print(f"Log({spillover_var}) on r2012:")
                    print(f"Coefficient: {coef:.4f}")
                    print(f"Standard Error: {se:.4f}")
                    print(f"P-value: {pval:.4f}")
                    print(f"Observations: {len(y_clean)}")
                else:
                    print(f"Warning: r2012 not found in results for {spillover_var}")
                    
            except Exception as e:
                print(f"Error running 2SLS for {spillover_var}: {e}")
        else:
            print(f"No valid observations for {spillover_var}")
    else:
        print(f"Variable {spillover_var} not found in dataset")

# =============================================================================
# UNEMPLOYMENT REGRESSION (LOG LEVEL)
# =============================================================================

print("\n" + "="*60)
print("UNEMPLOYMENT REGRESSION (LOG LEVEL)")
print("="*60)

if 'unemp_5k' in df_main.columns:
    print("Running 2SLS for log(unemp_5k)...")
    
    # Create log variable
    y_raw = df_main['unemp_5k'].astype(float)
    y = np.log(y_raw + 1)  # log transformation
    
    valid_idx = ~(y.isna() | X_exog.isna().any(axis=1) | df_main['t'].isna())
    
    if valid_idx.sum() > 0:
        y_clean = y[valid_idx]
        X_clean = X_exog[valid_idx]
        
        if 'kernel_tri_mainband' in df_main.columns:
            weights = df_main.loc[valid_idx, 'kernel_tri_mainband'].astype(float)
        else:
            weights = None
        
        try:
            model_2sls = IV2SLS(
                dependent=y_clean,
                exog=X_clean,
                endog=df_main.loc[valid_idx, 'r2012'].astype(float),
                instruments=df_main.loc[valid_idx, 't'].astype(float),
                weights=weights
            ).fit(cov_type='robust')
            
            if 'r2012' in model_2sls.params.index:
                coef = model_2sls.params['r2012']
                se = model_2sls.std_errors['r2012']
                pval = model_2sls.pvalues['r2012']
                
                results['log_unemp_5k'] = {
                    'coefficient': coef,
                    'std_error': se,
                    'p_value': pval,
                    'observations': len(y_clean)
                }
                
                print(f"Log(unemp_5k) on r2012:")
                print(f"Coefficient: {coef:.4f}")
                print(f"Standard Error: {se:.4f}")
                print(f"P-value: {pval:.4f}")
                print(f"Observations: {len(y_clean)}")
            else:
                print("Warning: r2012 not found in unemployment results")
                
        except Exception as e:
            print(f"Error running 2SLS for unemployment: {e}")
    else:
        print("No valid observations for unemployment")
else:
    print("Variable unemp_5k not found in dataset")

# =============================================================================
# RESULTS SUMMARY
# =============================================================================

print("\n" + "="*60)
print("RESULTS SUMMARY")
print("="*60)

if results:
    summary_df = pd.DataFrame(results).T
    summary_df = summary_df.round(4)
    
    print("\nIV Regression Results (Log Levels):")
    print("="*50)
    print(summary_df)
    
    # Save results to CSV
    summary_df.to_csv('iv_regression_results_log.csv')
    print(f"\nResults saved to: iv_regression_results_log.csv")
else:
    print("No results to display")

print("\n" + "="*60)
print("REPLICATION COMPLETE")
print("="*60) 