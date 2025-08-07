# overview
Python replication of Table 4 from Meckel (2020) AER paper analyzing price effects of Electronic Benefit Transfer (EBT) implementation in Texas WIC program.
## Research Question
Does eliminating price discrimination through EBT technology cause unintended price increases for non-WIC customers?
Methodology
Identification Strategy: Difference-in-differences using staggered county-level EBT rollout in Texas (2005-2009)
Key Regression Specification:
ln(price_ijst) = β·After_EBT_ct + α_i + γ_j + δ_t + θ_c·t + ε_ijst
Where:

i = store, j = product (UPC), s = county, t = time
α_i = store fixed effects
γ_j = UPC fixed effects
δ_t = year-month fixed effects
θ_c·t = county-group specific linear time trends

### Sample Restrictions:

WIC-eligible products in WIC stores only
Independent stores vs. Chain stores (separate regressions)
Texas households, FY 2007-2009

#### Expected Results

Independent stores: ~6.4% price increase after EBT
Chain stores: ~0.1% price increase (not significant)

##### Code Structure
Main Function: replicate_table4()

Data Loading: Combines Nielsen TSV files across years
Product Coding: Identifies WIC-eligible products per program rules
Sample Construction: Merges household, trip, and purchase data
Geographic Matching: Links purchases to counties and EBT dates
Regression Analysis: Panel regression with clustered standard errors

Key Functions:

code_wic_products(): Implements WIC eligibility rules for 7 food categories
create_controls(): Generates fixed effects and time trends
drop_singletons(): Removes fixed effect cells with single observations

##### Next Steps
Need Raw Data
Step 1: Data Preparation
bash# Place Nielsen TSV files in working directory:
products_extra_04.tsv, products_extra_05.tsv, ..., products_extra_09.tsv
panel_04.tsv, panel_05.tsv, ..., panel_09.tsv  
purchases_04.tsv, purchases_05.tsv, ..., purchases_09.tsv
trips_04.tsv, trips_05.tsv, ..., trips_09.tsv
products_transformed.tsv
retailers.tsv
Step 2: Install Dependencies
bashpip install pandas numpy linearmodels statsmodels
Step 3: Run Analysis
pythonpython replicate_table4.py
Step 4: Validate Results
Compare output to original paper Table 4:

Independent stores coefficient ≈ 0.0644
Chain stores coefficient ≈ 0.0010


File Dependencies
Current: upc_versions.dta () Available)
Needed:  nielsen_sample.dta (Missing - this is the processed analysis dataset) including - products_extra_04.tsv through products_extra_09.tsv
- panel_04.tsv through panel_09.tsv  
- purchases_04.tsv through purchases_09.tsv
- trips_04.tsv through trips_09.tsv
- products_transformed.tsv
- retailers.tsv


