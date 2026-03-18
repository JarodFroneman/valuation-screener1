import streamlit as st
import requests
import pandas as pd
from io import StringIO
import json

st.title("OECD structure inspector")

if st.button("Inspect OECD response"):
    try:
        url = ("https://stats.oecd.org/sdmx-json/data/KEI/"
               "IRLTLT01.GBR.ST.M/all?startTime=2020-01&endTime=2025-12")
        r = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
        st.write(f"HTTP {r.status_code} — {len(r.text)} chars")
        data = r.json()
        st.write("**Top-level keys:**", list(data.keys()))
        # Show first 500 chars of raw JSON
        st.code(r.text[:1000])
    except Exception as e:
        st.error(f"Error: {e}")

    st.divider()

    # Try alternative OECD endpoint formats
    st.subheader("Alternative OECD URL formats")
    urls = {
        "OECD iLibrary REST": "https://sdmx.oecd.org/public/rest/data/OECD,DF_DP_LIVE,/.LTINT.../all?startPeriod=2020-01&format=csvfilewithlabels&dimensionAtObservation=AllDimensions",
        "OECD Data Explorer GB": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,/.GBR.M.IRLTLT01.ST....?startPeriod=2020-01&format=csvfilewithlabels",
        "OECD Data Explorer JP": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,/.JPN.M.IRLTLT01.ST....?startPeriod=2020-01&format=csvfilewithlabels",
        "OECD Data Explorer DE": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,/.DEU.M.IRLTLT01.ST....?startPeriod=2020-01&format=csvfilewithlabels",
        "OECD Data Explorer FR": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,/.FRA.M.IRLTLT01.ST....?startPeriod=2020-01&format=csvfilewithlabels",
    }
    for label, url in urls.items():
        try:
            r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
            st.write(f"**{label}**  HTTP {r.status_code} — {len(r.text)} chars")
            st.code(r.text[:200])
        except Exception as e:
            st.error(f"❌ {label}: {e}")
