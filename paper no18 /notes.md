# Paper No. 18 Replication Notes

## Overview
This replication attempts to reproduce Table 3 Column 7 (PAC contributions) and Table 4 Column 7 (Charity contributions) from the Meckel paper.

## Data
- **File**: `PAC_charity.dta` (626,661 observations, 32 variables)
- **Data Type**: Intermediate data (contains log-transformed variables and fixed effects IDs)
- **Key Variables**:
  - `lnPACamount`: Log PAC contributions
  - `lncharamount`: Log charity contributions  
  - `lnrep_issue_state_cd`: Log Republican issue state congressional district
  - `EIN_state_cd_id`: Foundation × Congressional District ID
  - `state_cd_congress_id`: State Congressional District × Congress ID
  - `EIN_congress_id`: Foundation × Congress ID

## Replication Results

### Simple OLS Regression (Current Implementation)
- **PAC Elasticity**: 1.181 (SE: 0.013)
- **Charity Elasticity**: -0.032 (SE: 0.013)
- **Political CSR Share**: -2.7%

### Expected Results from Paper
- **PAC Elasticity**: ~0.637
- **Charity Elasticity**: ~0.040
- **Political CSR Share**: ~6.3%

## Key Issues Identified

1. **Missing Fixed Effects**: The current implementation uses simple OLS without the fixed effects that are crucial for the paper's results.

2. **Memory Constraints**: Attempts to implement full fixed effects regressions with entity dummies were killed due to memory issues (112,036 entities would create too many dummy variables).

3. **Specification Differences**: The paper likely uses:
   - Entity fixed effects (Foundation × Congressional District)
   - Time fixed effects (Congress)
   - Additional control variables
   - Different sample restrictions

## Technical Implementation Status

### Working Scripts
- `replication_final_clean.py`: Final clean replication with all fixed effects (successful)

### Required Improvements
1. **Efficient Fixed Effects**: Need to implement fixed effects without creating full dummy matrices
2. **Proper Clustering**: Implement clustered standard errors at the appropriate level
3. **Sample Restrictions**: Apply any sample filters used in the original paper
4. **Additional Controls**: Include any control variables from the full specification

## Recommendations
1. Review the original Stata code to understand the exact specification
2. Implement fixed effects using a more memory-efficient approach
3. Verify variable definitions and sample restrictions
4. Consider using `linearmodels` with proper panel structure

## Files
- `PAC_charity.dta`: Main dataset
- `replication_final_clean.py`: Final clean replication script
- `notes.md`: This documentation