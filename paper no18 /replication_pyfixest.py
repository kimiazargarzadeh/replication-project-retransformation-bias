"""
Paper No. 18 Replication using pyfixest
PAC and Charity Contributions Analysis
"""

import pandas as pd
import numpy as np
import pyfixest as pf
import warnings
warnings.filterwarnings('ignore')

def main():
    """Main replication function using pyfixest"""
    
    # Load data
    df = pd.read_stata('PAC_charity.dta')
    
    # Run PAC regression (Table 3 Column 7)
    print("=" * 60)
    print("TABLE 3 COLUMN 7: PAC CONTRIBUTIONS")
    print("=" * 60)
    
    pac_fit = pf.feols(
        "lnPACamount ~ lnrep_issue_state_cd | EIN_state_cd_id + state_cd_congress_id + EIN_congress_id",
        data=df,
        vcov="HC1"
    )
    
    pac_coeff = pac_fit.coef().iloc[0]
    pac_se = pac_fit.se().iloc[0]
    
    print(f"PAC Elasticity: {pac_coeff:.3f} (SE: {pac_se:.3f})")
    
    # Run Charity regression (Table 4 Column 7)
    print("\n" + "=" * 60)
    print("TABLE 4 COLUMN 7: CHARITY CONTRIBUTIONS")
    print("=" * 60)
    
    charity_fit = pf.feols(
        "lncharamount ~ lnrep_issue_state_cd | EIN_state_cd_id + state_cd_congress_id + EIN_congress_id",
        data=df,
        vcov="HC1"
    )
    
    charity_coeff = charity_fit.coef().iloc[0]
    charity_se = charity_fit.se().iloc[0]
    
    print(f"Charity Elasticity: {charity_coeff:.3f} (SE: {charity_se:.3f})")
    
    # Calculate political motivation
    ratio = charity_coeff / pac_coeff
    political_share = ratio * 100
    
    # Results summary
    print("\n" + "=" * 60)
    print("POLITICAL MOTIVATION ANALYSIS")
    print("=" * 60)
    print(f"Ratio of CSR/PAC elasticities: {ratio:.3f}")
    print(f"Implied politically motivated CSR: {political_share:.1f}%")
    
    # Compare with expected results
    print(f"\nExpected results from paper:")
    print(f"Table 3 Column 7 (PAC): ~0.637")
    print(f"Table 4 Column 7 (CSR): ~0.040")
    print(f"Political CSR share: ~6.3%")
    
    print("\n" + "=" * 60)
    print("REPLICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main() 