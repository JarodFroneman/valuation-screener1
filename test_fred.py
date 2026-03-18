import streamlit as st
import requests
import pandas as pd
from io import StringIO
import json

st.title("OECD correct parser + new sources")

if st.button("Run tests"):

    # ── Fix OECD parser — response is [meta, data, errors] array ─────────────
    st.subheader("1. OECD — fixed parser")
    for country_code, label in [("GBR","GB"),("JPN","JP"),("DEU","DE"),("FRA","FR")]:
        try:
            url = (f"https://stats.oecd.org/sdmx-json/data/KEI/"
                   f"IRLTLT01.{country_code}.ST.M/all"
                   f"?startTime=2000-01&endTime=2025-12")
            r = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
            arr = r.json()  # it's a list: [meta, data, errors]
            data_block = arr[1]  # second element is the data
            st.write(f"**{label}** data_block keys: {list(data_block.keys())[:6]}")

            # Try to extract series
            datasets = data_block.get("dataSets", [])
            structure = data_block.get("structure", {})
            st.write(f"  dataSets: {len(datasets)}, structure keys: {list(structure.keys())}")

            if datasets and structure:
                dims = structure.get("dimensions", {}).get("observation", [])
                st.write(f"  observation dims count: {len(dims)}")
                if dims:
                    time_dim = dims[0]
                    periods = [v["id"] for v in time_dim.get("values", [])]
                    st.write(f"  periods: {len(periods)}, first={periods[0] if periods else 'none'}, last={periods[-1] if periods else 'none'}")
                    series = datasets[0].get("series", {})
                    st.write(f"  series keys count: {len(series)}")
                    if series:
                        first_key = list(series.keys())[0]
                        obs = series[first_key].get("observations", {})
                        rows = []
                        for idx_str, vals in obs.items():
                            idx = int(idx_str)
                            if idx < len(periods) and vals[0] is not None:
                                rows.append({"date": periods[idx], "value": float(vals[0])})
                        if rows:
                            df = pd.DataFrame(rows).set_index("date").sort_index()
                            st.success(f"✅ {label}: {len(df)} rows, latest={df['value'].iloc[-1]:.4f}")
                        else:
                            st.error(f"❌ {label}: no rows extracted")
        except Exception as e:
            st.error(f"❌ {label}: {e}")

    st.divider()

    # ── datahub.io CSV ─────────────────────────────────────────────────────────
    st.subheader("2. datahub.io")
    for label, url in {
        "GB long rates": "https://pkgstore.datahub.io/core/bond-yields-uk-10y/monthly_csv/data/monthly_csv.csv",
        "US 10Y (test)": "https://pkgstore.datahub.io/core/bond-yields-us-10y/monthly_csv/data/monthly_csv.csv",
    }.items():
        try:
            r = requests.get(url, timeout=10)
            st.write(f"**{label}** HTTP {r.status_code} — {len(r.text)} chars — `{r.text[:100]}`")
        except Exception as e:
            st.error(f"❌ {label}: {e}")

    st.divider()

    # ── abstractapi / marketdata.app / others ──────────────────────────────────
    st.subheader("3. Other public APIs")
    others = {
        "marketdata.app GB gilt": "https://api.marketdata.app/v1/rates/history/?date_from=2020-01-01&country=GB",
        "investing.com alt": "https://api.investing.com/api/financialdata/23705/historical/chart/",
        "twelve data GB": "https://api.twelvedata.com/time_series?symbol=GB10Y&interval=1month&outputsize=60&apikey=demo",
        "twelve data JP": "https://api.twelvedata.com/time_series?symbol=JP10Y&interval=1month&outputsize=60&apikey=demo",
    }
    for label, url in others.items():
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
            st.write(f"**{label}** HTTP {r.status_code} — {len(r.text)} chars — `{r.text[:120]}`")
        except Exception as e:
            st.error(f"❌ {label}: {e}")

