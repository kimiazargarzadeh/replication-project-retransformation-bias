# Gregg (2020) – Factory Productivity and Incorporation in Late Imperial Russia

## Data Description

- Panel dataset from Russian manufacturing censuses: **1894, 1900, 1908**
- ~13,000+ factories per census
- Key variables: revenue, workers, machine horsepower, factory age, industry, location
- Matched with the **RUSCORP** database (corporation registry)
- Excludes excise-taxed sectors (e.g. alcohol, sugar)
- Focused on **European Russia**

---

## Main Specification

Let for factory _i_, industry _j_, year _t_:

- `log(R/L)` = log revenue per worker  
- `log(HP/L)` = log horsepower per worker  
- `TFP` = total factor productivity (residual from Cobb-Douglas)  
- `Corp` = dummy: 1 if incorporated  
- `X` = province, industry, and year fixed effects

### Estimating Equations

```text
(1) log(R/L)_ijt = γ₁ * Corp_ijt + φ₁ * X_ijt + ε_ijt  
(2) log(HP/L)_ijt = γ₂ * Corp_ijt + φ₂ * X_ijt + ν_ijt  
(3) TFP_ijt        = γ₃ * Corp_ijt + φ₃ * X_ijt + ζ_ijt


Each γ estimates the association between incorporation and the performance metric.

---

## Results Summary

### OLS Estimates (Table 3)

| Outcome             | Coefficient | Method     |
|---------------------|-------------|------------|
| log(R/L)            | 0.49        | Pooled OLS |
| log(HP/L)           | 0.25        | Pooled OLS |
| TFP                 | 0.10        | Pooled OLS |

→ Corporate factories had higher revenue and machine intensity.  
→ Not causal — includes selection bias.

---

### Fixed Effects (Table 5)

| Outcome             | Coefficient | Method               |
|---------------------|-------------|----------------------|
| log(R/L)            | 0.20        | Factory Fixed Effects |
| log(HP/L)           | 0.30        | Factory Fixed Effects |
| TFP                 | 0.05        | Factory Fixed Effects |

→ Causal interpretation: factories that incorporated became more machine-intensive and labor-productive.  
→ No significant effect on TFP → productivity gains came from capital deepening.

---

### Instrumental Variables (Table 6)

| Outcome             | Coefficient | Method |
|---------------------|-------------|--------|
| log(HP/L)           | 3.08        | 2SLS   |
| TFP                 | –1.31       | 2SLS   |

→ Larger effect on machine power per worker when correcting for selection.  
→ TFP becomes negative — possible governance costs or negative selection.

---

### Corporation Types (Table 7)

- Compared A-corporations (stock market oriented) vs. Share Partnerships (family-run)
- Performance differences were **small**
- → Stock market access **not the main driver** of productivity differences
- → Advantages came from legal structure: **limited liability, locked-in capital, legal personhood**

---

## Conclusion

- More productive firms were more likely to incorporate.
- Incorporation **increased capital intensity** (machine power) and revenue per worker.
- **No significant gains in TFP**: productivity gains came from more capital, not efficiency.
- Russia’s **concession system** (requiring special permission to incorporate) limited growth of mid-sized firms.
- Legal form mattered — especially in a capital-scarce environment — beyond just access to stock markets.
