# Runbook — Asset Pricing

Step-by-step guide to set up and run this project from scratch.

---

## Prerequisites

- Python 3.13+
- `git` (optional, for cloning `quant-risk-engine` from GitHub)

---

## 1. Create and activate the virtual environment

```bash
cd asset-pricing
python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows
```

---

## 2. Install dependencies

```bash
pip install .
```

All dependencies are declared in `pyproject.toml`. This includes `quant-risk` pulled from GitHub.  
If you prefer the **local copy** instead (faster, works offline, lets you edit the engine):

```bash
# Install everything except quant-risk, then install the local engine:
pip install --no-deps .
pip install -e ../quant-risk-engine
# Then install the remaining deps manually or edit pyproject.toml to remove the GitHub line
```

Or simply install the local engine after the standard install (it will override the GitHub version):

```bash
pip install .
pip install -e ../quant-risk-engine
```

---

## 3. Register the kernel with JupyterLab

```bash
python3 -m ipykernel install --user --name asset-pricing --display-name "asset-pricing"
```

In JupyterLab, select the **asset-pricing** kernel when opening any notebook.

---

## 4. Launch JupyterLab

```bash
jupyter lab
```

Navigate to any notebook and run it top-to-bottom.

---

## Notebook-specific notes

### Base setup — shared across all notebooks
Every notebook starts with:
```python
from quant_risk.setup import base
np, pd, plt = base()
```
This is provided by the `quant-risk-engine` package (installed in step 2). It configures `numpy`, `pandas`, and `matplotlib` with a consistent display style. No local helper file is needed.

### Notebooks that require `QuantLib`
- `01_yield_curves/02_bootstrapping_ois.ipynb`
- `03_simulations/02_mc_bond_swap_pricing.ipynb`
- `03_simulations/03_mc_callable_bonds.ipynb`

`QuantLib` is declared in `pyproject.toml` and is installed automatically.

### Notebooks that fetch live market data (`yfinance`)
- `02_instruments/04_options_vol.ipynb`
- `02_instruments/10_exotic_equity_derivatives.ipynb`
- `04_financial_theory/timeseries/*.ipynb`

These make outbound HTTP calls to Yahoo Finance. An internet connection is required, and results will differ from any cached outputs in the notebook.

### `quant_risk` — engine dependency
Most notebooks across sections 01–03 import from `quant_risk`. If you see:
```
ModuleNotFoundError: No module named 'quant_risk'
```
re-run step 2 above. The engine source is at:
- Local: `../quant-risk-engine/`
- GitHub: `https://github.com/mrspatbile/quant-risk-engine`

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: quant_risk` | `pip install -e ../quant-risk-engine` |
| `ModuleNotFoundError: QuantLib` | `pip install QuantLib` |
| `from setup import base` fails | Launch Jupyter from the project root |
| Kernel not found | Re-run step 3 to register the kernel |
| Stale outputs after a `quant-risk-engine` change | Restart the kernel (`Kernel > Restart`) |
