"""
Data exploration script to identify variables for Table 2 replication
"""

import pandas as pd
import numpy as np

def explore_data():
    """Explore the dataset to identify variables"""
    
    # Load data
    df = pd.read_stata('Radio_LRA_DB125.dta')
    print(f"Dataset shape: {df.shape}")
    
    # Filter for year > 2007
    df_filtered = df[df['year'] > 2007].copy()
    print(f"Filtered dataset (year > 2007): {df_filtered.shape}")
    
    # Check for treatment variables (defection messaging)
    print("\n" + "="*60)
    print("TREATMENT VARIABLES (defection messaging)")
    print("="*60)
    
    # Look for variables that might be the main treatment
    treatment_candidates = [col for col in df_filtered.columns if any(word in col.lower() for word in ['messag', 'defect', 'radio', 'main', 'treat'])]
    print(f"Potential treatment variables: {treatment_candidates}")
    
    # Check for intensity variables
    print(f"\nIntensity variables found: {[col for col in df_filtered.columns if col in ['stdnintensity', 'pctmessaging']]}")
    
    # Check for control variables
    print("\n" + "="*60)
    print("CONTROL VARIABLES")
    print("="*60)
    
    # Distance controls
    dist_controls = [col for col in df_filtered.columns if 'dist' in col.lower()]
    print(f"Distance controls: {dist_controls}")
    
    # Visual/non-visual controls
    vis_controls = [col for col in df_filtered.columns if any(word in col.lower() for word in ['vis', 'nvis'])]
    print(f"Visual/non-visual controls: {vis_controls}")
    
    # Geographic controls
    geo_controls = [col for col in df_filtered.columns if any(word in col.lower() for word in ['geo', 'sel', 'region', 'country'])]
    print(f"Geographic controls: {geo_controls}")
    
    # Circular coverage
    circ_controls = [col for col in df_filtered.columns if 'circ' in col.lower()]
    print(f"Circular coverage controls: {circ_controls}")
    
    # Variable-specific trends
    trend_controls = [col for col in df_filtered.columns if any(word in col.lower() for word in ['trend', 'year', 'rugged', 'nlights', 'pop', 'urban', 'forest'])]
    print(f"Trend controls: {trend_controls}")
    
    # Check for dependent variables
    print("\n" + "="*60)
    print("DEPENDENT VARIABLES")
    print("="*60)
    
    dep_vars = ['lnC_LRAfatalities', 'lnA_LRAfatalities', 'lnB_LRAfatalities', 'ln_LRAfatalities']
    available_dep_vars = [var for var in dep_vars if var in df_filtered.columns]
    print(f"Available dependent variables: {available_dep_vars}")
    
    # Check sample statistics for dependent variables
    for var in available_dep_vars:
        print(f"\n{var}:")
        print(f"  Mean: {df_filtered[var].mean():.3f}")
        print(f"  Std: {df_filtered[var].std():.3f}")
        print(f"  Min: {df_filtered[var].min():.3f}")
        print(f"  Max: {df_filtered[var].max():.3f}")
        print(f"  Non-missing: {df_filtered[var].count()}")
    
    # Check for panel structure
    print("\n" + "="*60)
    print("PANEL STRUCTURE")
    print("="*60)
    
    if 'cell_id' in df_filtered.columns:
        print(f"Number of unique cells: {df_filtered['cell_id'].nunique()}")
    if 'year' in df_filtered.columns:
        print(f"Year range: {df_filtered['year'].min()} - {df_filtered['year'].max()}")
        print(f"Number of unique years: {df_filtered['year'].nunique()}")
    
    # Show first few rows of key variables
    print("\n" + "="*60)
    print("SAMPLE DATA (first 5 rows)")
    print("="*60)
    
    key_vars = ['cell_id', 'year'] + available_dep_vars + treatment_candidates + ['stdnintensity', 'pctmessaging']
    key_vars = [var for var in key_vars if var in df_filtered.columns]
    
    print(df_filtered[key_vars].head())

if __name__ == "__main__":
    explore_data() 