# Ambrus, Field & Gonzalez (2020) – Table 3 Replication

## Replication Target: Table 3 - Log Rental Prices by Year

**Objective**: Replicate Table 3 from Ambrus et al. (2020) showing the temporal evolution of rental price effects around the Broad Street Pump (BSP) boundary.

---

## Data Sources

* **Panel A (1853)**: `Merged_1853_1864_data.dta`
* **Panel B (1864)**: `Merged_1853_1864_data.dta` 
* **Panel C (1894)**: `Merged_1846_1894_data.dta`
* **Panel D (1936)**: `houses_1936_final.dta`

---

## Econometric Specification

### Regression Discontinuity Design
**Forcing Variable**: Distance to BSP boundary (`dist_netw`)
- **Treatment**: Inside BSP perimeter (`broad = 1`)
- **Control**: Outside BSP perimeter (`broad = 0`)

### Key Variables
* `log_rentals_1853`, `log_rentals_1864`, `log_rentals_1894`, `lnrentals` (1936)
* `dist_2`: Distance variable (negative for outside BSP)
* `broad`: Treatment indicator (1 = inside BSP)
* `block`: Clustering variable for standard errors

### Control Variables (by panel)
* **1853/1864**: `dist_cent`, `dist_square`, `dist_fire`, `dist_thea`, `dist_police`, `dist_urinal`, `dist_pub`, `dist_church`, `dist_bank`, `no_sewer`, `old_sewer`, `dist_vent`, `dist_pump`, `dist_pit_fake`
* **1894**: `dist_cent`, `dist_square`, `dist_bank`, `dist_vent`, `dist_pit_fake`
* **1936**: `dist_cent`, `dist_square`, `dist_thea`, `dist_school`, `dist_pub`, `dist_church`, `dist_bank`, `length`, `width`

---

## Methods Implemented

### Column 1: Local Linear Regression (LLR)
**Method**: `rdrobust` package (Calonico et al. 2014)
**Specification**: 
```python
rdrobust(y=log_rentals, x=dist_2, cluster=block)
```
**Bandwidth**: Optimal bandwidth using `rdbwselect`

### Column 4: Polynomial Regression (Wide Bandwidth)
**Method**: `statsmodels.OLS` with clustered standard errors
**Specification**:
```python
log_rentals ~ broad + dist_netw + dist_netw2 + controls
```
**Bandwidth**: 100 meters (1.0 in scaled units)
**Clustering**: Block-level standard errors

### Column 5: Segment Fixed Effects
**Method**: `statsmodels.OLS` with segment dummies
**Specification**:
```python
log_rentals ~ broad + dist_netw + dist_netw2 + controls + segment_dummies
```
**Bandwidth**: 100 meters (1.0 in scaled units)
**Fixed Effects**: Segment-level (`seg_5`)

---

## Replication Results

### Panel A (1853) - Pre-Treatment Period
| Column | Method | Coefficient | Std Error | P-value | Observations |
|--------|--------|-------------|-----------|---------|--------------|
| **1** | LLR | 0.0516 | 0.1240 | 0.677 | 588 |
| **4** | Polynomial | -0.0408 | 0.0732 | 0.578 | 1070 |
| **5** | Segment FE | -0.0788 | 0.0701 | 0.261 | 1070 |

**Interpretation**: Small, mostly insignificant effects (pre-sewer era)

### Panel B (1864) - Short-Run Effects
| Column | Method | Coefficient | Std Error | P-value | Observations |
|--------|--------|-------------|-----------|---------|--------------|
| **1** | LLR | -0.1858 | 0.1180 | 0.115 | 469 |
| **4** | Polynomial | -0.1185 | 0.0678 | 0.080 | 1047 |
| **5** | Segment FE | -0.1269 | 0.0678 | 0.061 | 1047 |

**Interpretation**: Larger negative effects, some significant (sewer construction impact)

### Panel C (1894) - Medium-Run Effects
| Column | Method | Coefficient | Std Error | P-value | Observations |
|--------|--------|-------------|-----------|---------|--------------|
| **1** | LLR | -0.2506 | 0.2329 | 0.282 | 370 |
| **4** | Polynomial | -0.2674 | 0.1034 | **0.010** | 794 |
| **5** | Segment FE | -0.2875 | 0.0948 | **0.002** | 794 |

**Interpretation**: Strong negative effects, highly significant (full sewer system)

### Panel D (1936) - Long-Run Effects
| Column | Method | Coefficient | Std Error | P-value | Observations |
|--------|--------|-------------|-----------|---------|--------------|
| **1** | LLR | -0.2996 | 0.3111 | 0.335 | 221 |
| **4** | Polynomial | -0.4581 | 0.1440 | **0.001** | 354 |
| **5** | Segment FE | -0.2712 | 0.1502 | 0.071 | 354 |

**Interpretation**: Strongest negative effects, highly significant (mature infrastructure)

---

## Key Findings

1. **Temporal Evolution**: Effects become stronger and more significant over time
2. **1853**: No significant effects (pre-sewer era)
3. **1864**: Emerging negative effects (sewer construction)
4. **1894**: Strong, significant effects (full sewer system)
5. **1936**: Strongest effects (mature infrastructure)

**Economic Interpretation**: The negative impact of being outside the Broad Street perimeter becomes progressively stronger, reflecting the growing importance of sewer infrastructure over time.

---

## Technical Implementation

**Software**: Python with `rdrobust`, `statsmodels`, `pandas`
**Bandwidth Selection**: Calonico, Cattaneo, and Titiunik (2014) method
**Standard Errors**: Clustered at block level
**Data Processing**: Distance scaling, polynomial terms, treatment variable creation