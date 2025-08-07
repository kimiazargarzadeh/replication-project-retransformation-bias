# === IMPORTS ===
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm

# === LOAD DATA ===
df = pd.read_stata("AG_Corp_Prod_Database.dta")  # make sure it's in your project folder

# === TABLE 3 CHECK: Pooled OLS ===
df_check = df.dropna(subset=["logRevperWorker", "Form", "Industry", "Province", "YEAR"])
model_check = smf.ols(
    formula="logRevperWorker ~ Form + C(Industry) + C(Province) + C(YEAR)",
    data=df_check
).fit(cov_type="HC1")

print("\n=== Table 3 Coefficient on Form (pooled OLS) ===")
print(model_check.params["Form"], model_check.bse["Form"])


# === STEP 1: Construct TFP as residuals ===
df_tfp = df.dropna(subset=["logRev", "logWorkers", "logPower", "Industry", "Province", "YEAR", "id"]).copy()

# Convert numeric columns to float and handle any non-numeric values
df_tfp["logRev"] = pd.to_numeric(df_tfp["logRev"], errors='coerce')
df_tfp["logWorkers"] = pd.to_numeric(df_tfp["logWorkers"], errors='coerce')
df_tfp["logPower"] = pd.to_numeric(df_tfp["logPower"], errors='coerce')

# Drop rows with NaN in numeric columns
df_tfp = df_tfp.dropna(subset=["logRev", "logWorkers", "logPower"])

industry_dummies = pd.get_dummies(df_tfp["Industry"], prefix="ind", drop_first=True)
province_dummies = pd.get_dummies(df_tfp["Province"], prefix="prov", drop_first=True)
year_dummies = pd.get_dummies(df_tfp["YEAR"], prefix="year", drop_first=True)

X = pd.concat([df_tfp[["logWorkers", "logPower"]], industry_dummies, province_dummies, year_dummies], axis=1)
X = sm.add_constant(X)
y = df_tfp["logRev"]

# Ensure all data is numeric
X = X.astype(float)
y = y.astype(float)

model = sm.OLS(y, X).fit()
df_tfp["TFP"] = model.resid

df = df.merge(df_tfp[["id", "TFP"]], on="id", how="left")


# === STEP 2: FIXED EFFECTS REGRESSIONS (Table 5) ===
outcomes = ["logRevperWorker", "logPowerperWorker", "TFP"]
df_fe = df.dropna(subset=outcomes + ["Form", "YEAR", "factory_id"]).copy()

# Convert outcome variables to numeric
for outcome in outcomes:
    if outcome in df_fe.columns:
        df_fe[outcome] = pd.to_numeric(df_fe[outcome], errors='coerce')

# Drop rows with NaN in outcome variables
df_fe = df_fe.dropna(subset=outcomes)

print("\n=== Table 5 Fixed Effects Results ===")
for outcome in outcomes:
    if outcome in df_fe.columns:
        model = smf.ols(
            formula=f"{outcome} ~ Form + C(YEAR)",
            data=df_fe
        ).fit(cov_type="cluster", cov_kwds={"groups": df_fe["factory_id"]})

        coef = model.params["Form"]
        se = model.bse["Form"]
        pval = model.pvalues["Form"]
        ci = model.conf_int().loc["Form"].tolist()

        print(f"\nOutcome: {outcome}")
        print(f"  Coefficient: {coef:.3f}")
        print(f"  Std. Error:  {se:.3f}")
        print(f"  P-value:     {pval:.4f}")
        print(f"  95% CI:      [{ci[0]:.3f}, {ci[1]:.3f}]")
    else:
        print(f"\nOutcome: {outcome} - Column not found in dataset") 