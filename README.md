# 🔨 Auction Bid Tracker

A simple Streamlit app to track live auction bids against your maximum budget. Upload your auction catalog, hit refresh, and instantly see which lots are within budget and which have blown out.

## Features

- Upload a CSV or Excel auction catalog
- Scrapes live current bids from auction listing pages
- Color-coded status per lot (within budget / exceeded / error)
- Summary metrics: items in budget, items exceeded, total max bid exposure

## CSV / Excel Format

Your file must include at least these columns:

| Column | Description |
|---|---|
| `Lot` | Lot number |
| `Description` | Item description |
| `URL` | Link to the auction listing page |
| `Max Bid` | Your maximum bid for that item (e.g. `$250` or `250`) |

Only rows with a `Max Bid` value will be tracked.

## Running Locally

```bash
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo and set the main file to `app.py`
4. Deploy — Streamlit Cloud will install system dependencies from `packages.txt` and Python packages from `requirements.txt` automatically

## How It Works

On refresh, the app spins up a headless Chromium browser (via Playwright) for each tracked lot, waits for the live bid element to load, extracts the current price, and compares it against your max bid.

> **Note:** Each lot requires a separate browser fetch, so refresh time scales with the number of items you're tracking.
