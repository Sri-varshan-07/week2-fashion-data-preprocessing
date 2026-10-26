"""
feature_engineering.py
-----------------------
Domain-specific feature engineering for fashion & apparel datasets.

Features created:
    - Price tier (budget / mid-range / premium / luxury)
    - Discount rate category
    - Season encoding (cyclical)
    - Popularity score
    - Profit margin estimate
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Price Tier Classification
# ══════════════════════════════════════════════════════════════════════════════

def add_price_tier(df: pd.DataFrame, price_col: str = "price") -> pd.DataFrame:
    """
    Add a 'price_tier' column classifying products into market segments.

    Tiers:
        - Budget      : price < 20
        - Mid-Range   : 20 ≤ price < 60
        - Premium     : 60 ≤ price < 150
        - Luxury      : price ≥ 150

    Parameters
    ----------
    df : pd.DataFrame
    price_col : str
        Name of the price column.

    Returns
    -------
    pd.DataFrame
    """
    bins = [0, 20, 60, 150, float("inf")]
    labels = ["Budget", "Mid-Range", "Premium", "Luxury"]
    df["price_tier"] = pd.cut(df[price_col], bins=bins, labels=labels, right=False)
    logger.info("Feature added: price_tier")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Discount Category
# ══════════════════════════════════════════════════════════════════════════════

def add_discount_category(df: pd.DataFrame, discount_col: str = "discount_pct") -> pd.DataFrame:
    """
    Add a 'discount_category' column based on discount percentage.

    Categories:
        - No Discount  : 0%
        - Low          : 1–20%
        - Moderate     : 21–40%
        - High         : 41–60%
        - Deep Discount : >60%

    Parameters
    ----------
    df : pd.DataFrame
    discount_col : str

    Returns
    -------
    pd.DataFrame
    """
    def categorize(pct):
        if pct == 0:
            return "No Discount"
        elif pct <= 20:
            return "Low"
        elif pct <= 40:
            return "Moderate"
        elif pct <= 60:
            return "High"
        return "Deep Discount"

    df["discount_category"] = df[discount_col].apply(categorize)
    logger.info("Feature added: discount_category")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Cyclical Season Encoding
# ══════════════════════════════════════════════════════════════════════════════

SEASON_ORDER = {"Spring": 0, "Summer": 1, "Autumn": 2, "Winter": 3}


def add_cyclical_season(df: pd.DataFrame, season_col: str = "season") -> pd.DataFrame:
    """
    Encode season as cyclical sin/cos features so that Winter and Spring
    are treated as adjacent by the model.

    Parameters
    ----------
    df : pd.DataFrame
    season_col : str

    Returns
    -------
    pd.DataFrame
        With new 'season_sin' and 'season_cos' columns.
    """
    df["season_num"] = df[season_col].map(SEASON_ORDER)
    df["season_sin"] = np.sin(2 * np.pi * df["season_num"] / 4)
    df["season_cos"] = np.cos(2 * np.pi * df["season_num"] / 4)
    df.drop(columns=["season_num"], inplace=True)
    logger.info("Features added: season_sin, season_cos (cyclical encoding)")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Popularity Score
# ══════════════════════════════════════════════════════════════════════════════

def add_popularity_score(
    df: pd.DataFrame,
    rating_col: str = "rating",
    reviews_col: str = "reviews_count",
) -> pd.DataFrame:
    """
    Compute a weighted popularity score: score = rating × log1p(reviews_count).

    This rewards products with both high ratings AND many reviews.

    Parameters
    ----------
    df : pd.DataFrame
    rating_col : str
    reviews_col : str

    Returns
    -------
    pd.DataFrame
    """
    df["popularity_score"] = df[rating_col] * np.log1p(df[reviews_col])
    # Normalize to [0, 1]
    min_val = df["popularity_score"].min()
    max_val = df["popularity_score"].max()
    if max_val > min_val:
        df["popularity_score"] = (df["popularity_score"] - min_val) / (max_val - min_val)
    logger.info("Feature added: popularity_score")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Revenue Estimate
# ══════════════════════════════════════════════════════════════════════════════

def add_revenue_estimate(
    df: pd.DataFrame,
    price_col: str = "price",
    discount_col: str = "discount_pct",
    reviews_col: str = "reviews_count",
) -> pd.DataFrame:
    """
    Estimate revenue using: effective_price × reviews_count as a proxy for units sold.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df["effective_price"] = df[price_col] * (1 - df[discount_col] / 100)
    df["revenue_estimate"] = df["effective_price"] * df[reviews_col]
    logger.info("Features added: effective_price, revenue_estimate")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Run All Engineering
# ══════════════════════════════════════════════════════════════════════════════

def engineer_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering steps in sequence.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame (post-preprocessing).

    Returns
    -------
    pd.DataFrame
        DataFrame enriched with all engineered features.
    """
    if "price" in df.columns:
        df = add_price_tier(df)
    if "discount_pct" in df.columns:
        df = add_discount_category(df)
    if "season" in df.columns:
        df = add_cyclical_season(df)
    if "rating" in df.columns and "reviews_count" in df.columns:
        df = add_popularity_score(df)
    if all(c in df.columns for c in ["price", "discount_pct", "reviews_count"]):
        df = add_revenue_estimate(df)
    return df
