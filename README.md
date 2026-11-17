# Working Capital Benchmarking: Indian Capital Goods

**Live dashboard:** [paste your streamlit.app link here]

## Question
How much cash is each listed capital-goods company tying up in working capital compared with its peers?

## What it does
- Pulls annual financials for 11 Indian capital-goods companies (Yahoo Finance via yfinance).
- Computes DSO, DIO, DPO and cash conversion cycle using standard definitions (no scaling or calibration).
- Benchmarks each company against the median of its own peers (company excluded) within two peer groups.
- Sizes the cash-release opportunity in Rs crore: a full-gap upper bound and a conservative 25% case.

## Validation
Compared against Screener.in for [N] companies. Result: [e.g. "within X% for N of M metrics; larger gaps for L&T because of customer advances"]. 

## Key findings
- [finding 1 with a number]
- [finding 2 with a number]

## Limitations
- Small peer groups; medians are unstable.
- Yahoo and Screener define cost differently, so ratios do not match exactly.
- Contract assets and customer advances distort EPC and defence companies.
- Fiscal year-ends differ across companies.
- The prize is an upper bound, not a forecast.

## Files
- `working_capital_analysis.ipynb`: full analysis
- `app.py`: Streamlit dashboard
- CSV/JSON files: data used by the dashboard
