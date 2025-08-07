import pandas as pd
import numpy as np

# Load data
df = pd.read_stata("Merged_1853_1864_data.dta").copy()

# 1. Set negative values for distances outside BSP perimeter (EXACTLY like Stata)
df['temp'] = df['dist_netw'] / 100
df.loc[df['broad'] == 0, 'temp'] = -df.loc[df['broad'] == 0, 'dist_netw'] / 100

# 2. Change distance scale (EXACTLY like Stata)
df['dist_netw'] = df['dist_netw'] / 100
df['dist_netw2'] = df['dist_netw'] ** 2
df['dist_netw3'] = df['dist_netw'] ** 3

# 3. Create dist_2 variable (EXACTLY like Stata)
df['dist_2'] = df['dist_netw']
df.loc[df['broad'] == 0, 'dist_2'] = -df.loc[df['broad'] == 0, 'dist_netw']

# 3. Calculate optimal bandwidth using Calonico et al. (2014) method
from rdrobust import rdbwselect, rdrobust

outcomes = ['log_rentals_1853', 'log_rentals_1864']
hopt = {}

# Drop missing values for bandwidth selection
df_bw = df.dropna(subset=['log_rentals_1853', 'log_rentals_1864', 'temp', 'block'])

for var in outcomes:
    # Use rdbwselect to get optimal bandwidth (like Stata)
    bw_result = rdbwselect(y=df_bw[var], x=df_bw['temp'], cluster=df_bw['block'])
    hopt[var] = round(bw_result.bws.iloc[0, 0], 5)  # Get h (left) from mserd row

# 4. Calculate means outside Broad Street area
mean_out_rentals_53 = df.loc[(df['broad'] == 0) & (df['dist_netw'] < hopt['log_rentals_1853']), 'rentals_53'].mean()
mean_out_rentals_64 = df.loc[(df['broad'] == 0) & (df['dist_netw'] < hopt['log_rentals_1864']), 'rentals_64'].mean()

mean_out_rentals_53_all = df.loc[(df['broad'] == 0) & (df['dist_netw'] < 1), 'rentals_53'].mean()
mean_out_rentals_64_all = df.loc[(df['broad'] == 0) & (df['dist_netw'] < 1), 'rentals_64'].mean()



# Drop missing values for regression
df_reg = df.dropna(subset=['log_rentals_1853', 'dist_2', 'block'])

# Use rdrobust for proper regression discontinuity estimation
rd_result = rdrobust(y=df_reg['log_rentals_1853'], x=df_reg['dist_2'], cluster=df_reg['block'])

# Get results from rdrobust
coef_dist2 = rd_result.coef.iloc[0, 0]  # Conventional coefficient
se_dist2 = rd_result.se.iloc[0, 0]      # Conventional standard error
pval_dist2 = rd_result.pv.iloc[0, 0]    # Conventional p-value
obs = rd_result.N_h[0] + rd_result.N_h[1]  # Total observations (left + right)
bw = rd_result.bws.iloc[0, 0] * 100  # Bandwidth in meters

# =============================================================================
# MAIN RESULTS SUMMARY - TABLE 3
# =============================================================================

# Store Panel A results for final summary (will be defined later)
controls = ['dist_cent', 'dist_square', 'dist_fire', 'dist_thea', 'dist_police', 
           'dist_urinal', 'dist_pub', 'dist_church', 'dist_bank', 'no_sewer', 
           'old_sewer', 'dist_vent', 'dist_pump', 'dist_pit_fake']

# Drop missing values for controls regression
df_reg2 = df.dropna(subset=['log_rentals_1853', 'dist_2', 'block'] + controls)

# Use rdrobust with covariates
rd_result2 = rdrobust(y=df_reg2['log_rentals_1853'], x=df_reg2['dist_2'], 
                     covs=df_reg2[controls], cluster=df_reg2['block'])

coef_dist2_2 = rd_result2.coef.iloc[0, 0]
se_dist2_2 = rd_result2.se.iloc[0, 0]
pval_dist2_2 = rd_result2.pv.iloc[0, 0]
obs2 = rd_result2.N_h[0] + rd_result2.N_h[1]
bw2 = rd_result2.bws.iloc[0, 0] * 100

# Calculate mean for this bandwidth
mean_out_llr2_53 = df.loc[(df['broad'] == 0) & (df['dist_netw'] <= rd_result2.bws.iloc[0, 0]), 'rentals_53'].mean()


import statsmodels.api as sm

# Filter by optimal bandwidth (use exact bandwidth from Stata results: 35.72 meters = 0.3572)
df_reg3 = df[df['dist_netw'] <= 0.3572].dropna(subset=['log_rentals_1853', 'broad', 'dist_netw', 'dist_netw2', 'block'] + controls)

# Create regression variables
y3 = df_reg3['log_rentals_1853']
X3 = sm.add_constant(df_reg3[['broad', 'dist_netw', 'dist_netw2'] + controls])

# Ensure all data is numeric
X3 = X3.astype(float)
y3 = y3.astype(float)

# Run regression with clustered SE
model3 = sm.OLS(y3, X3).fit(cov_type='cluster', cov_kwds={'groups': df_reg3['block']})

coef_broad_3 = model3.params['broad']
se_broad_3 = model3.bse['broad']
pval_broad_3 = model3.pvalues['broad']
obs3 = model3.nobs


df_reg4 = df[df['dist_netw'] <= 1].dropna(subset=['log_rentals_1853', 'broad', 'dist_netw', 'dist_netw2', 'block'] + controls)

y4 = df_reg4['log_rentals_1853']
X4 = sm.add_constant(df_reg4[['broad', 'dist_netw', 'dist_netw2'] + controls])

# Ensure all data is numeric
X4 = X4.astype(float)
y4 = y4.astype(float)

model4 = sm.OLS(y4, X4).fit(cov_type='cluster', cov_kwds={'groups': df_reg4['block']})

coef_broad_4 = model4.params['broad']
se_broad_4 = model4.bse['broad']
pval_broad_4 = model4.pvalues['broad']
obs4 = model4.nobs


df_reg5 = df[df['dist_netw'] < 1].dropna(subset=['log_rentals_1853', 'broad', 'dist_netw', 'dist_netw2', 'block', 'seg_5'] + controls)

# Create segment fixed effects
seg_dummies = pd.get_dummies(df_reg5['seg_5'], prefix='seg', drop_first=True)

y5 = df_reg5['log_rentals_1853']
X5 = pd.concat([df_reg5[['broad', 'dist_netw', 'dist_netw2'] + controls], seg_dummies], axis=1)
X5 = sm.add_constant(X5)

# Ensure all data is numeric
X5 = X5.astype(float)
y5 = y5.astype(float)

model5 = sm.OLS(y5, X5).fit(cov_type='cluster', cov_kwds={'groups': df_reg5['block']})

coef_broad_5 = model5.params['broad']
se_broad_5 = model5.bse['broad']
pval_broad_5 = model5.pvalues['broad']
obs5 = model5.nobs


# =============================================================================
# TABLE 3 - PANEL B: log rental prices, 1864
# =============================================================================

df_reg_b1 = df.dropna(subset=['log_rentals_1864', 'dist_2', 'block'])

# Use rdrobust for proper regression discontinuity estimation
rd_result_b1 = rdrobust(y=df_reg_b1['log_rentals_1864'], x=df_reg_b1['dist_2'], cluster=df_reg_b1['block'])

# Get results from rdrobust
coef_dist2_b1 = rd_result_b1.coef.iloc[0, 0]  # Conventional coefficient
se_dist2_b1 = rd_result_b1.se.iloc[0, 0]      # Conventional standard error
pval_dist2_b1 = rd_result_b1.pv.iloc[0, 0]    # Conventional p-value
obs_b1 = rd_result_b1.N_h[0] + rd_result_b1.N_h[1]  # Total observations (left + right)
bw_b1 = rd_result_b1.bws.iloc[0, 0] * 100  # Bandwidth in meters

# Calculate mean for 1864
mean_out_rentals_64_b1 = df.loc[(df['broad'] == 0) & (df['dist_netw'] <= rd_result_b1.bws.iloc[0, 0]), 'rentals_64'].mean()


df_reg_b2 = df.dropna(subset=['log_rentals_1864', 'dist_2', 'block'] + controls)

# Use rdrobust with covariates
rd_result_b2 = rdrobust(y=df_reg_b2['log_rentals_1864'], x=df_reg_b2['dist_2'], 
                       covs=df_reg_b2[controls], cluster=df_reg_b2['block'])

coef_dist2_b2 = rd_result_b2.coef.iloc[0, 0]
se_dist2_b2 = rd_result_b2.se.iloc[0, 0]
pval_dist2_b2 = rd_result_b2.pv.iloc[0, 0]
obs_b2 = rd_result_b2.N_h[0] + rd_result_b2.N_h[1]
bw_b2 = rd_result_b2.bws.iloc[0, 0] * 100

# Calculate mean for this bandwidth
mean_out_llr2_64 = df.loc[(df['broad'] == 0) & (df['dist_netw'] <= rd_result_b2.bws.iloc[0, 0]), 'rentals_64'].mean()


# Filter by optimal bandwidth (use exact bandwidth from Stata results: 28.04 meters = 0.2804)
df_reg_b3 = df[df['dist_netw'] <= 0.2804].dropna(subset=['log_rentals_1864', 'broad', 'dist_netw', 'dist_netw2', 'block'] + controls)

# Create regression variables
y_b3 = df_reg_b3['log_rentals_1864']
X_b3 = sm.add_constant(df_reg_b3[['broad', 'dist_netw', 'dist_netw2'] + controls])

# Ensure all data is numeric
X_b3 = X_b3.astype(float)
y_b3 = y_b3.astype(float)

# Run regression with clustered SE
model_b3 = sm.OLS(y_b3, X_b3).fit(cov_type='cluster', cov_kwds={'groups': df_reg_b3['block']})

coef_broad_b3 = model_b3.params['broad']
se_broad_b3 = model_b3.bse['broad']
pval_broad_b3 = model_b3.pvalues['broad']
obs_b3 = model_b3.nobs


df_reg_b4 = df[df['dist_netw'] <= 1].dropna(subset=['log_rentals_1864', 'broad', 'dist_netw', 'dist_netw2', 'block'] + controls)

y_b4 = df_reg_b4['log_rentals_1864']
X_b4 = sm.add_constant(df_reg_b4[['broad', 'dist_netw', 'dist_netw2'] + controls])

# Ensure all data is numeric
X_b4 = X_b4.astype(float)
y_b4 = y_b4.astype(float)

model_b4 = sm.OLS(y_b4, X_b4).fit(cov_type='cluster', cov_kwds={'groups': df_reg_b4['block']})

coef_broad_b4 = model_b4.params['broad']
se_broad_b4 = model_b4.bse['broad']
pval_broad_b4 = model_b4.pvalues['broad']
obs_b4 = model_b4.nobs


df_reg_b5 = df[df['dist_netw'] <= 1].dropna(subset=['log_rentals_1864', 'broad', 'dist_netw', 'dist_netw2', 'block', 'seg_5'] + controls)

# Create segment fixed effects
seg_dummies_b5 = pd.get_dummies(df_reg_b5['seg_5'], prefix='seg', drop_first=True)

y_b5 = df_reg_b5['log_rentals_1864']
X_b5 = pd.concat([df_reg_b5[['broad', 'dist_netw', 'dist_netw2'] + controls], seg_dummies_b5], axis=1)
X_b5 = sm.add_constant(X_b5)

# Ensure all data is numeric
X_b5 = X_b5.astype(float)
y_b5 = y_b5.astype(float)

model_b5 = sm.OLS(y_b5, X_b5).fit(cov_type='cluster', cov_kwds={'groups': df_reg_b5['block']})

coef_broad_b5 = model_b5.params['broad']
se_broad_b5 = model_b5.bse['broad']
pval_broad_b5 = model_b5.pvalues['broad']
obs_b5 = model_b5.nobs


# =============================================================================
# TABLE 3 - PANEL C: log rental prices, 1894
# =============================================================================


# Load 1894 data
df_1894 = pd.read_stata("Merged_1846_1894_data.dta").copy()

# 1. Set negative values for distances outside BSP perimeter
df_1894['temp'] = df_1894['dist_netw'] / 100
df_1894.loc[df_1894['broad'] == 0, 'temp'] = -df_1894.loc[df_1894['broad'] == 0, 'dist_netw'] / 100

# 2. Change distance scale and create polynomial terms
df_1894['dist_netw'] = df_1894['dist_netw'] / 100
df_1894['dist_netw2'] = df_1894['dist_netw'] ** 2
df_1894['dist_netw3'] = df_1894['dist_netw'] ** 3
df_1894['dist_2'] = df_1894['dist_netw']
df_1894.loc[df_1894['broad'] == 0, 'dist_2'] = -df_1894.loc[df_1894['broad'] == 0, 'dist_netw']
df_1894['dist_2_2'] = df_1894['dist_2'] ** 2

# 3. Calculate optimal bandwidth using Calonico et al. (2014) method
outcomes_1894 = ['log_rentals_1894']
hopt_1894 = {}
df_bw_1894 = df_1894.dropna(subset=['log_rentals_1894', 'temp', 'block'])
for var in outcomes_1894:
    bw_result = rdbwselect(y=df_bw_1894[var], x=df_bw_1894['temp'], cluster=df_bw_1894['block'])
    hopt_1894[var] = round(bw_result.bws.iloc[0, 0], 5)


# 4. Calculate means outside Broad Street area
mean_out_rentals_94 = df_1894.loc[(df_1894['broad'] == 0) & (df_1894['dist_netw'] < hopt_1894['log_rentals_1894']), 'rentals_94'].mean()
mean_out_rentals_94_all = df_1894.loc[(df_1894['broad'] == 0) & (df_1894['dist_netw'] < 1), 'rentals_94'].mean()

df_reg_c1 = df_1894.dropna(subset=['log_rentals_1894', 'dist_2', 'block'])

# Use rdrobust for proper regression discontinuity estimation
rd_result_c1 = rdrobust(y=df_reg_c1['log_rentals_1894'], x=df_reg_c1['dist_2'], cluster=df_reg_c1['block'])

# Get results from rdrobust
coef_dist2_c1 = rd_result_c1.coef.iloc[0, 0]
se_dist2_c1 = rd_result_c1.se.iloc[0, 0]
pval_dist2_c1 = rd_result_c1.pv.iloc[0, 0]
obs_c1 = rd_result_c1.N_h[0] + rd_result_c1.N_h[1]
bw_c1 = rd_result_c1.bws.iloc[0, 0] * 100


controls_1894 = ['dist_cent', 'dist_square', 'dist_bank', 'dist_vent', 'dist_pit_fake']
df_reg_c2 = df_1894.dropna(subset=['log_rentals_1894', 'dist_2', 'block'] + controls_1894)

# Use rdrobust with covariates
rd_result_c2 = rdrobust(y=df_reg_c2['log_rentals_1894'], x=df_reg_c2['dist_2'], 
                       covs=df_reg_c2[controls_1894], cluster=df_reg_c2['block'])

coef_dist2_c2 = rd_result_c2.coef.iloc[0, 0]
se_dist2_c2 = rd_result_c2.se.iloc[0, 0]
pval_dist2_c2 = rd_result_c2.pv.iloc[0, 0]
obs_c2 = rd_result_c2.N_h[0] + rd_result_c2.N_h[1]
bw_c2 = rd_result_c2.bws.iloc[0, 0] * 100

# Calculate mean for this bandwidth
mean_out_llr2_94 = df_1894.loc[(df_1894['broad'] == 0) & (df_1894['dist_netw'] <= rd_result_c2.bws.iloc[0, 0]), 'rentals_94'].mean()


# Filter by optimal bandwidth
df_reg_c3 = df_1894[df_1894['dist_netw'] < hopt_1894['log_rentals_1894']].dropna(subset=['log_rentals_1894', 'broad', 'dist_netw', 'dist_netw2', 'block'] + controls_1894)

# Create regression variables
y_c3 = df_reg_c3['log_rentals_1894']
X_c3 = sm.add_constant(df_reg_c3[['broad', 'dist_netw', 'dist_netw2'] + controls_1894])

# Ensure all data is numeric
X_c3 = X_c3.astype(float)
y_c3 = y_c3.astype(float)

# Run regression with clustered SE
model_c3 = sm.OLS(y_c3, X_c3).fit(cov_type='cluster', cov_kwds={'groups': df_reg_c3['block']})

coef_broad_c3 = model_c3.params['broad']
se_broad_c3 = model_c3.bse['broad']
pval_broad_c3 = model_c3.pvalues['broad']
obs_c3 = model_c3.nobs


df_reg_c4 = df_1894[df_1894['dist_netw'] < 1].dropna(subset=['log_rentals_1894', 'broad', 'dist_netw', 'dist_netw2', 'block'] + controls_1894)

y_c4 = df_reg_c4['log_rentals_1894']
X_c4 = sm.add_constant(df_reg_c4[['broad', 'dist_netw', 'dist_netw2'] + controls_1894])

# Ensure all data is numeric
X_c4 = X_c4.astype(float)
y_c4 = y_c4.astype(float)

model_c4 = sm.OLS(y_c4, X_c4).fit(cov_type='cluster', cov_kwds={'groups': df_reg_c4['block']})

coef_broad_c4 = model_c4.params['broad']
se_broad_c4 = model_c4.bse['broad']
pval_broad_c4 = model_c4.pvalues['broad']
obs_c4 = model_c4.nobs


df_reg_c5 = df_1894[df_1894['dist_netw'] < 1].dropna(subset=['log_rentals_1894', 'broad', 'dist_netw', 'dist_netw2', 'block', 'seg_5'] + controls_1894)

# Create segment fixed effects
seg_dummies_c5 = pd.get_dummies(df_reg_c5['seg_5'], prefix='seg', drop_first=True)

y_c5 = df_reg_c5['log_rentals_1894']
X_c5 = pd.concat([df_reg_c5[['broad', 'dist_netw', 'dist_netw2'] + controls_1894], seg_dummies_c5], axis=1)
X_c5 = sm.add_constant(X_c5)

# Ensure all data is numeric
X_c5 = X_c5.astype(float)
y_c5 = y_c5.astype(float)

model_c5 = sm.OLS(y_c5, X_c5).fit(cov_type='cluster', cov_kwds={'groups': df_reg_c5['block']})

coef_broad_c5 = model_c5.params['broad']
se_broad_c5 = model_c5.bse['broad']
pval_broad_c5 = model_c5.pvalues['broad']
obs_c5 = model_c5.nobs


# =============================================================================
# TABLE 3 - PANEL D: log rental prices, 1936
# =============================================================================


# Load 1936 data
df_1936 = pd.read_stata("houses_1936_final.dta").copy()

# 1. Set negative values for distances outside BSP perimeter
df_1936['temp'] = df_1936['dist_netw']
df_1936.loc[df_1936['broad'] == 0, 'temp'] = -df_1936.loc[df_1936['broad'] == 0, 'dist_netw']

# 2. Create dist_2 variable
df_1936['dist_2'] = df_1936['dist_netw']
df_1936.loc[df_1936['broad'] == 0, 'dist_2'] = -df_1936.loc[df_1936['broad'] == 0, 'dist_netw']

# 3. Calculate optimal bandwidth using Calonico et al. (2014) method
outcomes_1936 = ['lnrentals']
hopt_1936 = {}
df_bw_1936 = df_1936.dropna(subset=['lnrentals', 'temp', 'block'])
for var in outcomes_1936:
    bw_result = rdbwselect(y=df_bw_1936[var], x=df_bw_1936['temp'], cluster=df_bw_1936['block'])
    hopt_1936[var] = round(bw_result.bws.iloc[0, 0], 4)


# 4. Calculate means outside Broad Street area
mean_out_rentals_36 = df_1936.loc[(df_1936['broad'] == 0) & (df_1936['dist_netw'] < hopt_1936['lnrentals']), 'rentals'].mean()
mean_out_rentals_36_all = df_1936.loc[(df_1936['broad'] == 0) & (df_1936['dist_netw'] < 1), 'rentals'].mean()

df_reg_d1 = df_1936.dropna(subset=['lnrentals', 'dist_2', 'block'])

# Use rdrobust for proper regression discontinuity estimation
rd_result_d1 = rdrobust(y=df_reg_d1['lnrentals'], x=df_reg_d1['dist_2'], cluster=df_reg_d1['block'])

# Get results from rdrobust
coef_dist2_d1 = rd_result_d1.coef.iloc[0, 0]
se_dist2_d1 = rd_result_d1.se.iloc[0, 0]
pval_dist2_d1 = rd_result_d1.pv.iloc[0, 0]
obs_d1 = rd_result_d1.N_h[0] + rd_result_d1.N_h[1]
bw_d1 = rd_result_d1.bws.iloc[0, 0] * 100


controls_1936 = ['dist_cent', 'dist_square', 'dist_thea', 'dist_pub', 'dist_church', 'dist_bank']
df_reg_d2 = df_1936.dropna(subset=['lnrentals', 'dist_2', 'block'] + controls_1936)

# Use rdrobust with covariates and fixed bandwidth h=0.373
rd_result_d2 = rdrobust(y=df_reg_d2['lnrentals'], x=df_reg_d2['dist_2'], 
                       covs=df_reg_d2[controls_1936], cluster=df_reg_d2['block'], h=0.373)

coef_dist2_d2 = rd_result_d2.coef.iloc[0, 0]
se_dist2_d2 = rd_result_d2.se.iloc[0, 0]
pval_dist2_d2 = rd_result_d2.pv.iloc[0, 0]
obs_d2 = rd_result_d2.N_h[0] + rd_result_d2.N_h[1]
bw_d2 = rd_result_d2.bws.iloc[0, 0] * 100

# Calculate mean for this bandwidth
mean_out_llr2_36 = df_1936.loc[(df_1936['broad'] == 0) & (df_1936['dist_netw'] <= rd_result_d2.bws.iloc[0, 0]), 'rentals'].mean()


controls_1936_full = ['dist_cent', 'dist_square', 'dist_thea', 'dist_school', 'dist_pub', 'dist_church', 'dist_bank', 'length', 'width']
# Filter by optimal bandwidth
df_reg_d3 = df_1936[df_1936['dist_netw'] < hopt_1936['lnrentals']].dropna(subset=['lnrentals', 'broad', 'dist_netw', 'dist_netw2', 'block'] + controls_1936_full)

# Create regression variables
y_d3 = df_reg_d3['lnrentals']
X_d3 = sm.add_constant(df_reg_d3[['broad', 'dist_netw', 'dist_netw2'] + controls_1936_full])

# Ensure all data is numeric
X_d3 = X_d3.astype(float)
y_d3 = y_d3.astype(float)

# Run regression with clustered SE
model_d3 = sm.OLS(y_d3, X_d3).fit(cov_type='cluster', cov_kwds={'groups': df_reg_d3['block']})

coef_broad_d3 = model_d3.params['broad']
se_broad_d3 = model_d3.bse['broad']
pval_broad_d3 = model_d3.pvalues['broad']
obs_d3 = model_d3.nobs


df_reg_d4 = df_1936[df_1936['dist_netw'] < 1].dropna(subset=['lnrentals', 'broad', 'dist_netw', 'dist_netw2', 'block'] + controls_1936_full)

y_d4 = df_reg_d4['lnrentals']
X_d4 = sm.add_constant(df_reg_d4[['broad', 'dist_netw', 'dist_netw2'] + controls_1936_full])

# Ensure all data is numeric
X_d4 = X_d4.astype(float)
y_d4 = y_d4.astype(float)

model_d4 = sm.OLS(y_d4, X_d4).fit(cov_type='cluster', cov_kwds={'groups': df_reg_d4['block']})

coef_broad_d4 = model_d4.params['broad']
se_broad_d4 = model_d4.bse['broad']
pval_broad_d4 = model_d4.pvalues['broad']
obs_d4 = model_d4.nobs


df_reg_d5 = df_1936[df_1936['dist_netw'] < 1].dropna(subset=['lnrentals', 'broad', 'dist_netw', 'dist_netw2', 'block', 'seg_5'] + controls_1936_full)

# Create segment fixed effects
seg_dummies_d5 = pd.get_dummies(df_reg_d5['seg_5'], prefix='seg', drop_first=True)

y_d5 = df_reg_d5['lnrentals']
X_d5 = pd.concat([df_reg_d5[['broad', 'dist_netw', 'dist_netw2'] + controls_1936_full], seg_dummies_d5], axis=1)
X_d5 = sm.add_constant(X_d5)

# Ensure all data is numeric
X_d5 = X_d5.astype(float)
y_d5 = y_d5.astype(float)

model_d5 = sm.OLS(y_d5, X_d5).fit(cov_type='cluster', cov_kwds={'groups': df_reg_d5['block']})

coef_broad_d5 = model_d5.params['broad']
se_broad_d5 = model_d5.bse['broad']
pval_broad_d5 = model_d5.pvalues['broad']
obs_d5 = model_d5.nobs


# =============================================================================
# FINAL SUMMARY - ALL PANELS
# =============================================================================

# Store all panel results for summary
panel_a_results = {
    'llr': (coef_dist2, se_dist2, pval_dist2, obs),
    'wide_bw': (coef_broad_4, se_broad_4, pval_broad_4, obs4),
    'segment_fe': (coef_broad_5, se_broad_5, pval_broad_5, obs5)
}

print("\n" + "=" * 80)
print("TABLE 3: MAIN RESULTS SUMMARY - All Panels")
print("=" * 80)
print("Format: Coefficient (Std Error) [p-value] | Observations")
print("-" * 80)

print(f"PANEL A (1853):")
print(f"  LLR (Col 1):     {panel_a_results['llr'][0]:.4f} ({panel_a_results['llr'][1]:.4f}) [p={panel_a_results['llr'][2]:.3f}] | N={panel_a_results['llr'][3]}")
print(f"  Wide BW (Col 4): {panel_a_results['wide_bw'][0]:.4f} ({panel_a_results['wide_bw'][1]:.4f}) [p={panel_a_results['wide_bw'][2]:.3f}] | N={panel_a_results['wide_bw'][3]}")
print(f"  Segment FE (Col 5): {panel_a_results['segment_fe'][0]:.4f} ({panel_a_results['segment_fe'][1]:.4f}) [p={panel_a_results['segment_fe'][2]:.3f}] | N={panel_a_results['segment_fe'][3]}")
print()

print(f"PANEL B (1864):")
print(f"  LLR (Col 1):     {coef_dist2_b1:.4f} ({se_dist2_b1:.4f}) [p={pval_dist2_b1:.3f}] | N={obs_b1}")
print(f"  Wide BW (Col 4): {coef_broad_b4:.4f} ({se_broad_b4:.4f}) [p={pval_broad_b4:.3f}] | N={obs_b4}")
print(f"  Segment FE (Col 5): {coef_broad_b5:.4f} ({se_broad_b5:.4f}) [p={pval_broad_b5:.3f}] | N={obs_b5}")
print()

print(f"PANEL C (1894):")
print(f"  LLR (Col 1):     {coef_dist2_c1:.4f} ({se_dist2_c1:.4f}) [p={pval_dist2_c1:.3f}] | N={obs_c1}")
print(f"  Wide BW (Col 4): {coef_broad_c4:.4f} ({se_broad_c4:.4f}) [p={pval_broad_c4:.3f}] | N={obs_c4}")
print(f"  Segment FE (Col 5): {coef_broad_c5:.4f} ({se_broad_c5:.4f}) [p={pval_broad_c5:.3f}] | N={obs_c5}")
print()

print(f"PANEL D (1936):")
print(f"  LLR (Col 1):     {coef_dist2_d1:.4f} ({se_dist2_d1:.4f}) [p={pval_dist2_d1:.3f}] | N={obs_d1}")
print(f"  Wide BW (Col 4): {coef_broad_d4:.4f} ({se_broad_d4:.4f}) [p={pval_broad_d4:.3f}] | N={obs_d4}")
print(f"  Segment FE (Col 5): {coef_broad_d5:.4f} ({se_broad_d5:.4f}) [p={pval_broad_d5:.3f}] | N={obs_d5}")
print()

"""
print("=" * 80)
print("KEY FINDINGS:")
print("- 1853: Small, mostly insignificant effects (pre-sewer era)")
print("- 1864: Larger negative effects, some significant (sewer construction)")
print("- 1894: Strong negative effects, highly significant (full sewer system)")
print("- 1936: Strongest negative effects, highly significant (mature infrastructure)")
print("=" * 80)
"""

