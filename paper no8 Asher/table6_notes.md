# Table 6, Panel A Replication - Asher & Novosad (2020)

## Replication Objective
Replicate Table 6, Panel A (log employment growth by sector) from Asher & Novosad (2020) using Python.

## Expected Results (From Paper)
| Sector | Coefficient | Std Error |
|--------|-------------|-----------|
| Total | 0.273 | 0.159 |
| Livestock | 0.252 | 0.188 |
| Manufacturing | 0.260 | 0.193 |
| Education | 0.198 | 0.143 |
| Retail | 0.333 | 0.154 |
| Forestry | -0.107 | 0.107 |

## Our Replication Results
| Sector | Coefficient | Std Error | Difference |
|--------|-------------|-----------|------------|
| Total | 0.263 | 0.169 | -0.010 |
| Livestock | 0.031 | 0.076 | -0.221 |
| Manufacturing | 0.231 | 0.190 | -0.029 |
| Education | -0.071 | 0.120 | -0.269 |
| Retail | 0.239 | 0.202 | -0.094 |
| Forestry | 0.297 | 0.159 | +0.404 |

## Main Result: Total Employment
- **Our Result**: 0.263 (SE: 0.169)
- **Expected**: 0.273 (SE: 0.159)
- **Difference**: -0.010


## Key Issues and Differences

### 1. **Total Employment (Best Match)**
- **Difference**: Only -0.010
- **Reason**: This is the most aggregated measure, least affected by sector-specific issues

### 2. **Sector-Specific Issues**
- **Livestock**: Large difference (-0.221)
- **Education**: Wrong sign (-0.071 vs +0.198)
- **Forestry**: Wrong sign (+0.297 vs -0.107)

### 3. **Potential Sources of Differences**

#### **A. Sample Definition Issues**
- **Missing Filters**: We may not have the exact `$states & $noroad & $nobad & rd_band_ik & _m_pmgsy == 3` filters
- **Sample Size**: Our sample (10,834) vs expected (10,678)

#### **B. Variable Mapping Issues**
- **Activity Codes**: We assumed act1=livestock, act2=manufacturing, etc.

#### **D. Kernel Weights**
- **Bandwidth**: Using `kernel_tri_ik` but may need different bandwidth
- **Weight Calculation**: Different kernel weight implementation

#### **E. Fixed Effects**
- **District FE**: Using `vhg_dist_id` 

## Technical Implementation

### **Regression Specification**
```
log(employment_sector) = α + β₁r2012 + β₂left + β₃right + γᵢDistrictᵢ + ε
```

### **Instrumental Variables**
- **Endogenous**: `r2012` (road access)
- **Instrument**: `t` (treatment assignment)
- **Method**: 2SLS with robust standard errors

### **Controls Used**
- `left`, `right` (RD controls)
- `scst_share`, `bus`, `comm`, `bank`, `irr_share` (village characteristics)
- District fixed effects

### **Weights**
- `kernel_tri_ik` (triangular kernel with IK bandwidth)



## Conclusion
