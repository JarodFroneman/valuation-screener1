"""
test_zar.py — Verify CME ZAR futures (6Z=F) data from Yahoo Finance
Run: python test_zar.py
"""
import yfinance as yf
import pandas as pd
import numpy as np

print("=" * 60)
print("Testing CME ZAR futures: 6Z=F  (TradingView: 6Z1!)")
print("=" * 60)

def test_ticker(ticker):
    print(f"\n── {ticker} ──")
    try:
        # Method 1: Ticker.history
        tk = yf.Ticker(ticker)
        df = tk.history(period="max", auto_adjust=True)
        if df is not None and not df.empty and "Close" in df.columns:
            s = df["Close"].dropna()
            print(f"  Ticker.history:  {len(s)} bars  |  "
                  f"first={s.index[0].date()}  latest={s.index[-1].date()}  "
                  f"last_close={s.iloc[-1]:.6f}")
            print(f"  Index tz: {s.index.tz}")
            return s
        else:
            print("  Ticker.history:  EMPTY")
    except Exception as e:
        print(f"  Ticker.history:  ERROR — {e}")

    try:
        # Method 2: yf.download
        df2 = yf.download(ticker, period="max", interval="1d",
                          auto_adjust=True, progress=False)
        if df2 is not None and not df2.empty:
            c = df2["Close"].iloc[:, 0] if isinstance(df2.columns, pd.MultiIndex) else df2["Close"]
            s = c.dropna()
            print(f"  yf.download:     {len(s)} bars  |  "
                  f"first={s.index[0].date()}  latest={s.index[-1].date()}  "
                  f"last_close={s.iloc[-1]:.6f}")
            return s
        else:
            print("  yf.download:     EMPTY")
    except Exception as e:
        print(f"  yf.download:     ERROR — {e}")

    return None

# Test the ZAR futures ticker
zar = test_ticker("6Z=F")

# Also test the old wrong ticker for comparison
print("\n── USDZAR=X (old — spot rate, NOT futures) ──")
old = test_ticker("USDZAR=X")

# Test DX=F too to confirm valuation calc will work
print("\n── DX=F (USD Index futures — front leg) ──")
dx = test_ticker("DX=F")

# Now test the actual valuation calculation
print("\n" + "=" * 60)
print("Valuation calculation test: DX=F vs 6Z=F")
print("=" * 60)

if zar is not None and dx is not None:
    # Strip tz from both
    def clean(s):
        if s.index.tz is not None:
            s = s.tz_convert("UTC").tz_localize(None)
        s.index = s.index.normalize()
        s = s[~s.index.duplicated(keep="last")]
        return s.sort_index().dropna()

    zar_c = clean(zar)
    dx_c  = clean(dx)

    df = pd.DataFrame({"dx": dx_c, "zar": zar_c}).dropna()
    print(f"\nAligned rows (DX ∩ ZAR): {len(df)}")
    print(f"Date range: {df.index[0].date()} → {df.index[-1].date()}")

    if len(df) >= 115:
        length = 10
        rsc    = 100
        diff     = df["dx"].pct_change(length) * 100 - df["zar"].pct_change(length) * 100
        roll_max = diff.rolling(rsc).max()
        roll_min = diff.rolling(rsc).min()
        rng      = (roll_max - roll_min).replace(0, np.nan)
        val      = (diff - roll_min) / rng * 200 - 100
        val      = val.dropna()

        latest = val.iloc[-1]
        sig = "OVERVALUED" if latest >= 75 else "UNDERVALUED" if latest <= -75 else "NEUTRAL"
        print(f"\nValuation score (daily, period={length}, rescale={rsc}): {latest:+.1f}")
        print(f"Signal: {sig}")
        print(f"Last 5 scores:\n{val.tail()}")
        print("\n✓  ZAR futures valuation is working correctly.")
    else:
        print(f"\n✗  Not enough aligned rows ({len(df)}) for valuation calc.")
        print("   Need at least 115 (length=10 + rescale=100 + 5 buffer).")
        print("   ZAR futures may have limited history — this is expected for CME ZAR.")
        print("   Try reducing Rescale Length in the screener (e.g. to 50 or 60).")
else:
    print("\n✗  Could not fetch one or both tickers.")
    if zar is None:
        print("   6Z=F returned no data — Yahoo Finance may not carry CME ZAR futures.")
        print("   Alternative tickers to try: 'USDZAR=X', 'ZAR=X'")
