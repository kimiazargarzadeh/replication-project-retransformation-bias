import pandas as pd
import numpy as np
from linearmodels import PanelOLS
import warnings
warnings.filterwarnings('ignore')

def replicate_table4():
    # Load Nielsen raw data files
    dfs = []
    
    # Read and combine products_extra files
    products_extra = []
    for x in range(4, 10):
        df = pd.read_csv(f'products_extra_0{x}.tsv', sep='\t')
        products_extra.append(df)
    products_extra = pd.concat(products_extra, ignore_index=True)
    products_extra = products_extra[['upc', 'upc_ver_uc', 'flavor_descr', 'container_descr', 
                                   'style_descr', 'type_descr', 'product_descr']].drop_duplicates()
    
    # Read and combine main files
    for file_type in ['panel', 'purchases', 'trips']:
        file_dfs = []
        for x in range(4, 10):
            df = pd.read_csv(f'{file_type}_0{x}.tsv', sep='\t')
            if file_type == 'panel':
                df['year'] = 2000 + x
            file_dfs.append(df)
        globals()[file_type] = pd.concat(file_dfs, ignore_index=True)
    
    # Read products and retailers
    products = pd.read_csv('products_transformed.tsv', sep='\t')
    upc_versions = pd.read_stata('upc_versions.dta')
    products = products.merge(upc_versions, on=['upc', 'upc_ver'], how='inner')
    
    retailers = pd.read_csv('retailers.tsv', sep='\t')
    
    # Convert purchase_date
    trips['purchase_date'] = pd.to_datetime(trips['purchase_date'])
    
    # Build analysis dataset
    df = (panel[panel['fips_state_desc'] == 'TX']
          .merge(trips, on=['panel_year', 'household_id'])
          .merge(purchases, on='trip_id_uc')
          .merge(products, on=['upc', 'upc_ver']))
    
    # Filter to relevant product groups
    df = df[df['product_group_descr'].isin(['VEGETABLES - CANNED', 'BABY FOOD', 'EGGS', 
                                           'FRESH PRODUCE', 'JAMS, JELLIES, SPREADS', 
                                           'SEAFOOD - CANNED', 'VEGETABLES AND GRAINS - DRIED'])]
    
    # Create fiscal year filter
    df['pyear'] = df['purchase_date'].dt.year
    df['pmonth'] = df['purchase_date'].dt.month
    df['purchase_ym'] = df['pyear'] * 100 + df['pmonth']
    df = df[(df['purchase_ym'] >= 200610) & (df['purchase_ym'] <= 200909)]
    
    # Merge products_extra
    df = df.merge(products_extra, on=['upc', 'upc_ver'], how='left')
    
    # Code WIC-eligible products
    df = code_wic_products(df)
    
    # Calculate price outcome
    df['finalprice_perunit'] = (df['total_price_paid'] - df['coupon_value']) / df['quantity']
    df['lfinalprice_perunit'] = np.log(df['finalprice_perunit'])
    df = df.dropna(subset=['lfinalprice_perunit'])
    
    # Store size indicator
    store_info = (trips[['store_id_uc', 'retailer_id']].drop_duplicates()
                  .merge(retailers, on='retailer_id'))
    store_counts = store_info.groupby('retailer_id').size().reset_index(columns=['total_stores'])
    store_info = store_info.merge(store_counts, on='retailer_id')
    df = df.merge(store_info[['store_id_uc', 'retailer_id', 'total_stores']], 
                  on=['store_id_uc', 'retailer_id'])
    
    # Load auxiliary data files
    zip2county = pd.read_stata('../OtherData/zip2county_tx.dta')
    county_names = pd.read_stata('../OtherData/fips2cntyname.dta')
    ebt_dates = pd.read_stata('../OtherData/ebt_dates.dta')
    
    # Merge geographic info
    df['zipcode'] = df['panelist_zip_code']
    df = (df.merge(zip2county, on='zipcode')
          .merge(county_names, on='fipscode')
          .merge(ebt_dates, on='county'))
    
    # Create WIC store proxy (requires TIPS data - simplified here)
    df['sm'] = 1  # Placeholder - needs actual WIC store matching
    
    # Create after EBT indicator
    df['after'] = (df['purchase_date'] > df['ebt_date']).astype(int)
    
    # Create control variables
    df['purchase_ym_fe'] = df['purchase_ym']
    df['fy_year'] = df['purchase_ym'].apply(lambda x: 2007 if 200610 <= x <= 200709 
                                           else (2008 if 200710 <= x <= 200809 else 2009))
    df['ebt_ym'] = df['ebt_date'].dt.year * 100 + df['ebt_date'].dt.month
    df['tt'] = df['fy_year'] - 2003
    
    # Store-EBT group
    df['storeret'] = df['store_id_uc'].fillna(df['retailer_id'])
    df['storeretebt'] = df.groupby(['storeret', 'ebt_ym']).ngroup()
    
    # Sample filters
    small_samp = ((df['total_stores'] == 1) & (df['leb'] == 0) & 
                  (df['sm'] == 1) & (df['pm'] == 1))
    big_samp = ((df['total_stores'] > 1) & (df['leb'] == 0) & 
                (df['sm'] == 1) & (df['pm'] == 1))
    
    results = {}
    
    # Independent stores
    df_small = df[small_samp].copy()
    if len(df_small) > 0:
        df_small = df_small.set_index(['storeretebt', 'purchase_ym_fe'])
        model = PanelOLS.from_formula('lfinalprice_perunit ~ after + EntityEffects + TimeEffects', 
                                      df_small)
        result = model.fit(cov_type='clustered', cluster_entity=True)
        results['independent'] = {
            'coef': result.params['after'],
            'se': result.std_errors['after'],
            'n': result.nobs
        }
    
    # Chain stores  
    df_big = df[big_samp].copy()
    if len(df_big) > 0:
        # Drop singletons
        upc_counts = df_big.groupby('upc').size()
        df_big = df_big[df_big['upc'].isin(upc_counts[upc_counts > 1].index)]
        store_counts = df_big.groupby('storeretebt').size()
        df_big = df_big[df_big['storeretebt'].isin(store_counts[store_counts > 1].index)]
        
        df_big = df_big.set_index(['storeretebt', 'purchase_ym_fe'])
        model = PanelOLS.from_formula('lfinalprice_perunit ~ after + EntityEffects + TimeEffects', 
                                      df_big)
        result = model.fit(cov_type='clustered', cluster_entity=True)
        results['chain'] = {
            'coef': result.params['after'],
            'se': result.std_errors['after'],
            'n': result.nobs
        }
    
    # Print Table 4
    print("TABLE 4: Effect of EBT on Prices of WIC Foods in WIC Stores")
    print("-" * 60)
    print(f"{'':15} {'Independent':>15} {'Chain':>15}")
    print(f"After EBT{results['independent']['coef']:>15.4f} {results['chain']['coef']:>15.4f}")
    print(f"{'':15} ({results['independent']['se']:>13.4f}) ({results['chain']['se']:>13.4f})")
    print(f"N{results['independent']['n']:>15,} {results['chain']['n']:>15,}")
    
    return results

def code_wic_products(df):
    # WIC product coding (simplified version)
    df['eggs_fy2007'] = ((df['product_group_descr'] == 'EGGS') & 
                         (df['size1_amount'] == 12) &
                         (~df['type_descr'].isin(['EXTRA LARGE', 'JUMBO', 'SUPER JUMBO'])) &
                         (df['multi'] <= 1))
    
    df['peanutbutter_fy2007'] = ((df['product_module_descr'] == 'PEANUT BUTTER') &
                                 (df['size1_amount'] == 18) & (df['multi'] <= 1))
    
    # Similar for other products...
    
    df['wic_prods_fy2007'] = (df['eggs_fy2007'] | df['peanutbutter_fy2007'])  # etc.
    
    df['pm'] = df['wic_prods_fy2007'].astype(int)  # Simplified
    df['leb'] = 0  # Simplified
    
    return df

if __name__ == "__main__":
    results = replicate_table4()