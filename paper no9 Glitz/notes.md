# Industrial Espionage and Productivity - Table 2 Replication

## Paper Information
- **Authors**: Albrecht Glitz and Erik Meyersson (2019)
- **Title**: Industrial Espionage and Productivity
- **Journal**: American Economic Review
- **Replication Target**: Table 2, Columns 3 and 6

## Replication Objective
Replicate the main specifications from Table 2 focusing on:
- **Column 3**: log TFP with patents gap and lagged gap
- **Column 6**: log output per worker with patents gap and lagged gap

## Expected Results (from Table 2)

### Column 3: log TFP
- **Espionage**: -0.052 (0.012)
- **Patents gap**: 0.071 (0.028)
- **log TFP gap**: -0.564 (0.090)
- **R²**: 0.56
- **Observations**: 240
- **P-value WB**: 0.011

### Column 6: log output per worker
- **Espionage**: -0.039 (0.017)
- **Patents gap**: 0.012 (0.028)
- **log output/worker gap**: -0.514 (0.100)
- **R²**: 0.51
- **Observations**: 240
- **P-value WB**: 0.125

## Econometric Specification

### Main Variables
- **Dependent Variables**:
  - `c3difflnTFP`: log TFP difference (Column 3)
  - `c3diffln_gvapc`: log output per worker difference (Column 6)

- **Independent Variables**:
  - `inf_gva`: Espionage measure (main treatment variable)
  - `diff_patents_gva`: Patents gap between GDR and FRG
  - `difflnTFP`: Lagged TFP gap (Column 3)
  - `diffln_gvapc`: Lagged output per worker gap (Column 6)

### Fixed Effects and Controls
- **Year fixed effects**: `yd_*` dummies
- **Branch fixed effects**: `br_*` dummies
- **Weights**: `weight_workers` (analytical weights)

### Clustering
- **Standard errors**: Clustered at branch level
- **Bootstrap**: 999 replications for wild bootstrap tests

## Technical Implementation

### Data Requirements
- **Main dataset**: `regdata_3_yes_0.33_0.06.dta`
- **Sample**: 240 observations
- **Period**: 1980-1989 (German reunification context)

### Regression Specification
```python
# Column 3: log TFP
c3difflnTFP ~ inf_gva + diff_patents_gva + difflnTFP + year_dummies + branch_dummies

# Column 6: log output per worker  
c3diffln_gvapc ~ inf_gva + diff_patents_gva + diffln_gvapc + year_dummies + branch_dummies
```

### Key Features
1. **Weighted Least Squares**: Using `weight_workers` as analytical weights
2. **Clustered Standard Errors**: At branch level
3. **Fixed Effects**: Year and branch dummies
4. **Bootstrap Testing**: Wild bootstrap for inference

## Economic Interpretation

### Column 3 (log TFP)
- **Espionage effect**: -0.052 indicates that industrial espionage reduces TFP by 5.2%
- **Patents gap**: 0.071 suggests positive effect of patent differences on TFP
- **Lagged TFP gap**: -0.564 shows strong mean reversion in TFP

### Column 6 (log output per worker)
- **Espionage effect**: -0.039 indicates that industrial espionage reduces output per worker by 3.9%
- **Patents gap**: 0.012 shows small positive effect of patent differences
- **Lagged output gap**: -0.514 shows strong mean reversion in output per worker

## Replication Status
- **✅ Code Structure**: Complete Python implementation
- **✅ Specification**: Matches Stata code structure
- **⚠️ Data**: Requires original dataset for exact replication
- **✅ Methods**: OLS with clustering and weights implemented

## Files
- `table2_replication.py`: Main replication script
- `notes.md`: This documentation file

## Dependencies
- pandas
- numpy
- statsmodels
- linearmodels

## Usage
```bash
python table2_replication.py
```

## Notes
- The script creates sample data for demonstration if the original dataset is not available
- For exact replication, ensure the original Stata dataset is in the same directory
- The bootstrap implementation is simplified; for exact results, use the original Stata code 