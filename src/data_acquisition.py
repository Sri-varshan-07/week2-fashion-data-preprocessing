"""
data_acquisition.py
-------------------
Utilities for fetching fashion & apparel data from multiple public sources.

Sources covered:
    - Kaggle API
    - Google Trends (via pytrends)
    - FRED API (US retail clothing sales)
    - Web scraping helpers (BeautifulSoup)
    - Local CSV/Excel file loader
"""

import os
import time
import logging
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Kaggle Dataset Downloader
# ══════════════════════════════════════════════════════════════════════════════

def download_kaggle_dataset(dataset: str, dest: Path = RAW_DIR) -> Path:
    """
    Download a Kaggle dataset using the Kaggle CLI.

    Parameters
    ----------
    dataset : str
        Kaggle dataset slug, e.g. "rmisra/clothing-fit-dataset-for-size-recommendation"
    dest : Path
        Destination folder for the downloaded files.

    Returns
    -------
    Path
        The destination folder.

    Prerequisites
    -------------
    Set KAGGLE_USERNAME and KAGGLE_KEY environment variables,
    or place kaggle.json in ~/.kaggle/.

    Example
    -------
    >>> download_kaggle_dataset("rmisra/clothing-fit-dataset-for-size-recommendation")
    """
    logger.info(f"Downloading Kaggle dataset: {dataset}")
    os.system(f'kaggle datasets download -d "{dataset}" -p "{dest}" --unzip')
    logger.info(f"Dataset saved to {dest}")
    return dest


# ══════════════════════════════════════════════════════════════════════════════
# 2. Google Trends Fetcher
# ══════════════════════════════════════════════════════════════════════════════

def fetch_google_trends(
    keywords: list[str],
    timeframe: str = "today 12-m",
    geo: str = "",
    save: bool = True,
) -> pd.DataFrame:
    """
    Fetch Google Trends interest-over-time data for fashion keywords.

    Parameters
    ----------
    keywords : list[str]
        Fashion-related search terms, e.g. ["streetwear", "sustainable fashion"].
    timeframe : str
        Date range string recognised by pytrends (default: last 12 months).
    geo : str
        ISO country code, e.g. "US". Empty string = worldwide.
    save : bool
        If True, saves result to data/raw/google_trends.csv.

    Returns
    -------
    pd.DataFrame
        Interest-over-time data indexed by date.

    Example
    -------
    >>> df = fetch_google_trends(["fast fashion", "sustainable fashion", "luxury fashion"])
    """
    try:
        from pytrends.request import TrendReq
    except ImportError:
        raise ImportError("Install pytrends: pip install pytrends")

    logger.info(f"Fetching Google Trends for: {keywords}")
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()

    if df.empty:
        logger.warning("Google Trends returned empty data.")
        return df

    df.drop(columns=["isPartial"], inplace=True, errors="ignore")
    if save:
        out = RAW_DIR / "google_trends.csv"
        df.to_csv(out)
        logger.info(f"Saved Google Trends data → {out}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 3. FRED API — US Retail Clothing Sales
# ══════════════════════════════════════════════════════════════════════════════

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

FRED_SERIES = {
    "clothing_sales": "RSCCASN",          # Retail: Clothing & Clothing Accessory Stores
    "total_retail_sales": "RSXFS",         # Advance Retail Sales: Retail & Food Services
}


def fetch_fred_data(
    series_id: str = "RSCCASN",
    api_key: str | None = None,
    start_date: str = "2015-01-01",
    save: bool = True,
) -> pd.DataFrame:
    """
    Fetch US retail clothing sales from the FRED API.

    Parameters
    ----------
    series_id : str
        FRED series ID (default: RSCCASN — clothing & accessory retail).
    api_key : str, optional
        FRED API key. Falls back to FRED_API_KEY env variable.
    start_date : str
        Start date in YYYY-MM-DD format.
    save : bool
        If True, saves result to data/raw/fred_{series_id}.csv.

    Returns
    -------
    pd.DataFrame
        Time-series DataFrame with 'date' and 'value' columns.

    Example
    -------
    >>> df = fetch_fred_data(api_key="YOUR_KEY")
    """
    key = api_key or os.getenv("FRED_API_KEY", "")
    if not key:
        logger.warning("No FRED API key provided. Register free at https://fred.stlouisfed.org/")
        return pd.DataFrame()

    params = {
        "series_id": series_id,
        "api_key": key,
        "file_type": "json",
        "observation_start": start_date,
    }
    resp = requests.get(FRED_BASE, params=params, timeout=15)
    resp.raise_for_status()
    observations = resp.json().get("observations", [])
    df = pd.DataFrame(observations)[["date", "value"]].copy()
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df.set_index("date", inplace=True)

    if save:
        out = RAW_DIR / f"fred_{series_id}.csv"
        df.to_csv(out)
        logger.info(f"Saved FRED series {series_id} → {out}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 4. Generic CSV / Excel Loader
# ══════════════════════════════════════════════════════════════════════════════

def load_local_dataset(filepath: str | Path) -> pd.DataFrame:
    """
    Load a local CSV or Excel file into a DataFrame.

    Parameters
    ----------
    filepath : str or Path
        Path to the file.

    Returns
    -------
    pd.DataFrame

    Example
    -------
    >>> df = load_local_dataset("data/raw/fashion_products.csv")
    """
    fp = Path(filepath)
    if not fp.exists():
        raise FileNotFoundError(f"File not found: {fp}")

    ext = fp.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(fp, low_memory=False)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(fp)
    elif ext == ".json":
        df = pd.read_json(fp)
    elif ext == ".parquet":
        df = pd.read_parquet(fp)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    logger.info(f"Loaded {fp.name}: {df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 5. Simple Web Scraper Scaffold
# ══════════════════════════════════════════════════════════════════════════════

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_page(url: str, delay: float = 1.5) -> BeautifulSoup | None:
    """
    Fetch a webpage and return a BeautifulSoup object.

    Parameters
    ----------
    url : str
        Target URL.
    delay : float
        Seconds to wait before the request (polite scraping).

    Returns
    -------
    BeautifulSoup or None

    Notes
    -----
    Always respect a site's robots.txt and Terms of Service.
    Only scrape publicly available, non-restricted content.

    Example
    -------
    >>> soup = scrape_page("https://example.com/fashion-trends")
    """
    time.sleep(delay)
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# CLI entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("Data Acquisition Module — Fashion & Apparel Industry")
    logger.info("Available functions:")
    logger.info("  download_kaggle_dataset(dataset)")
    logger.info("  fetch_google_trends(keywords)")
    logger.info("  fetch_fred_data(series_id, api_key)")
    logger.info("  load_local_dataset(filepath)")
    logger.info("  scrape_page(url)")
