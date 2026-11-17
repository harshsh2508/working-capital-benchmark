import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Working Capital Benchmark", page_icon="📊", layout="wide")
OUT = Path(__file__).parent 

@st.cache_data(ttl=3600)
def load():
    prize = pd.read_csv(OUT / "latest_prize.csv", parse_dates=["fy_end"])
    hist = pd.read_csv(OUT / "all_years.csv", parse_dates=["fy_end"])
    dq = pd.read_csv(OUT / "data_quality.csv")
    val = pd.read_csv(OUT / "validation.csv") if (OUT / "validation.csv").exists() else pd.DataFrame()
    meta = json.loads((OUT / "meta.json").read_text()) if (OUT / "meta.json").exists() else {}
    return prize, hist, dq, val, meta

try:
    prize, hist, dq, val, meta = load()
except FileNotFoundError as e:
    st.error(f"Output file missing: {e.filename}. Run `python src/run.py` first.")
    st.stop()

st.title("Working Capital Benchmark: Indian Capital Goods")
st.caption(f"Data refreshed: {meta.get('refreshed_utc', 'unknown')} | Source: Yahoo Finance annual statements | "
           "Prize = cash released if a company matched its peer median (upper bound, not a forecast)")

# ---- sidebar filters
groups = sorted(prize["group"].unique())
sel_groups = st.sidebar.multiselect("Peer group", groups, default=groups)
case = st.sidebar.radio("Prize case", ["Conservative (25% of gap)", "Full gap to peer median"])
col = "prize_conservative" if case.startswith("Conservative") else "prize_gap_to_median"
view = prize[prize["group"].isin(sel_groups)].copy()
if view.empty:
    st.warning("No companies match the selected peer groups."); st.stop()

# ---- KPI row
c1, c2, c3 = st.columns(3)
c1.metric("Companies shown", len(view))
c2.metric("Total prize (Rs Cr)", f"{view[col].sum():,.0f}")
top = view.sort_values(col, ascending=False).iloc[0]
c3.metric("Largest opportunity", top["company"], f"Rs {top[col]:,.0f} Cr")

tab1, tab2, tab3, tab4 = st.tabs(["Cash opportunity", "Metrics vs peers", "Trends", "Data quality & validation"])

with tab1:
    long = view.melt(id_vars="company", value_vars=["prize_DSO", "prize_DIO", "prize_DPO"],
                     var_name="lever", value_name="Rs Cr")
    st.plotly_chart(px.bar(long, x="company", y="Rs Cr", color="lever",
                           title="Gap to peer median by lever (Rs Cr, upper bound)"), width="stretch")
    flagged = view[view["outlier_flag"].fillna("") != ""]
    if not flagged.empty:
        st.info("Interpret with care (more than 2x peer median, often a business-model effect): "
                + ", ".join(flagged["company"]))

with tab2:
    st.dataframe(view[["company", "group", "fy_end", "peer_n", "DSO", "DIO", "DPO", "CCC", col]]
                 .sort_values(col, ascending=False), width="stretch", hide_index=True)
    metric = st.selectbox("Metric", ["DSO", "DIO", "DPO", "CCC"])
    st.plotly_chart(px.bar(view.sort_values(metric), x="company", y=metric, color="group",
                           title=f"{metric} (days), latest period"), width="stretch")

with tab3:
    comps = st.multiselect("Companies", sorted(hist["company"].unique()),
                           default=sorted(hist["company"].unique())[:3])
    m2 = st.selectbox("Metric over time", ["CCC", "DSO", "DIO", "DPO"], key="trend")
    h = hist[hist["company"].isin(comps)]
    if h.empty:
        st.write("Select at least one company.")
    else:
        st.plotly_chart(px.line(h.sort_values("fy_end"), x="fy_end", y=m2, color="company", markers=True),
                        width="stretch")

with tab4:
    st.subheader("Data quality")
    st.dataframe(dq, width="stretch", hide_index=True)
    st.subheader("Validation against Screener.in")
    if val.empty:
        st.write("No validation file yet.")
    else:
        st.dataframe(val, width="stretch", hide_index=True)
    st.markdown("**Limitations:** small peer groups; Yahoo and Screener define cost differently; contract assets and "
                "advances distort EPC and defence ratios; fiscal year-ends differ across companies.")
