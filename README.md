# Asset Pricing — Illustrated Knowledge Base

![Python](https://img.shields.io/badge/python-3.13+-3776AB?logo=python&logoColor=white)
![JupyterLab](https://img.shields.io/badge/JupyterLab-4.x-F37626?logo=jupyter&logoColor=white)
![QuantLib](https://img.shields.io/badge/QuantLib-1.42-4B8BBE)
![quant--risk--engine](https://img.shields.io/badge/engine-quant--risk--engine-00897B)
![Status](https://img.shields.io/badge/status-educational-6A1B9A)

A collection of Jupyter notebooks covering foundational and intermediate asset pricing topics: yield curves, fixed income instruments, derivatives, Monte Carlo simulations, and quantitative financial theory.

These notebooks are **illustrative and educational**. They demonstrate concepts with working code, not production systems.

---

## Structure

```
asset-pricing/
├── 01_yield_curves/
│   ├── 01_nss_ecb.ipynb            # Nelson-Siegel-Svensson curve fitting (ECB data)
│   └── 02_bootstrapping_ois.ipynb  # OIS curve bootstrapping
│
├── 02_instruments/
│   ├── 01_bonds.ipynb              # Bond pricing and duration
│   ├── 02_swaps.ipynb              # Interest rate swaps
│   ├── 03_fx_forwards.ipynb        # FX forwards and covered interest parity
│   ├── 04_options_vol.ipynb        # Options and volatility surfaces
│   ├── 05_cds.ipynb                # Credit default swaps
│   ├── 06_carry_trade.ipynb        # FX carry trade mechanics
│   ├── 07_futures.ipynb            # Futures pricing
│   ├── 08_fi_strategy_rv.ipynb     # Fixed income relative value strategies
│   ├── 09_callable_bond.ipynb      # Callable bond pricing
│   └── 10_exotic_equity_derivatives.ipynb  # Exotic equity derivatives
│
├── 03_simulations/
│   ├── 01_mc_rate_paths.ipynb      # Monte Carlo interest rate paths
│   ├── 02_mc_bond_swap_pricing.ipynb
│   ├── 03_mc_callable_bonds.ipynb
│   ├── 04_mc_equity_paths.ipynb    # GBM equity path simulation
│   ├── 05_vasicek_model.ipynb      # Vasicek short-rate model
│   ├── 06_hw_model.ipynb           # Hull-White model
│   ├── 07_cir_model.ipynb          # Cox-Ingersoll-Ross model
│   ├── 08_cva.ipynb                # Credit Valuation Adjustment
│   ├── 09_fva.ipynb                # Funding Valuation Adjustment
│   ├── 10_mva.ipynb                # Margin Valuation Adjustment
│   └── 11_xva_aggregation.ipynb    # XVA aggregation
│
├── 04_financial_theory/
│   ├── basic single period .ipynb  # Single-period model, state prices, arbitrage
│   ├── Vries_derivatives-pricing.ipynb  # Derivatives pricing fundamentals
│   └── timeseries/
│       ├── ts_finance.ipynb            # Financial time series analysis
│       ├── ts_garch_risk_management.ipynb  # GARCH models for risk
│       └── ts_var_xgboost.ipynb        # VaR with XGBoost
│
└── pyproject.toml
```

---

## Dependencies

### External packages
All standard packages (`numpy`, `pandas`, `scipy`, `matplotlib`, `statsmodels`, `QuantLib`, etc.) are declared in [pyproject.toml](pyproject.toml).

### `quant_risk` — internal engine
Many notebooks import `quant_risk`, which comes from the [`quant-risk-engine`](https://github.com/mrspatbile/quant-risk-engine) repository. See the [Runbook](RUNBOOK.md) for how to install it.

---

## Quickstart

See [RUNBOOK.md](RUNBOOK.md) for full setup instructions.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
# To use the local quant-risk-engine instead of GitHub:
# pip install . --no-deps && pip install -e ../quant-risk-engine
jupyter lab
```
