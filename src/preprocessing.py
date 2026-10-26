"""
preprocessing.py
----------------
End-to-end preprocessing pipeline for fashion & apparel datasets.

Pipeline steps:
    1. Schema validation
    2. Missing value handling
    3. Duplicate removal
    4. Outlier detection & treatment
    5. Normalization & scaling
    6. Categorical encoding
    7. Export
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Schema Validation
# ══════════════════════════════════════════════════════════════════════════════

def validate_schema(df: pd.DataFrame, required_columns: list[str]) -> pd.DataFrame:
    """
    Validate that required columns exist and report column data types.

    Parameters
    ----------
    df : pd.DataFrame
    required_columns : list[str]
        Columns that must be present in the DataFrame.

    Returns
    -------
    pd.DataFrame
        The input DataFrame (unchanged).

    Raises
    ------
    ValueError
        If any required column is missing.
    """
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    logger.info(f"Schema validation passed. Shape: {df.shape}")
    logger.info(f"Dtypes:\n{df.dtypes.to_string()}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Missing Value Handling
# ══════════════════════════════════════════════════════════════════════════════

def handle_missing_values(
    df: pd.DataFrame,
    numeric_strategy: str = "median",
    categorical_strategy: str = "mode",
    drop_threshold: float = 0.6,
) -> pd.DataFrame:
    """
    Handle missing values using configurable strategies.

    Parameters
    ----------
    df : pd.DataFrame
    numeric_strategy : str
        'mean', 'median', or 'drop' for numeric columns.
    categorical_strategy : str
        'mode', 'unknown', or 'drop' for categorical columns.
    drop_threshold : float
        Drop columns where the fraction of missing values exceeds this threshold.

    Returns
    -------
    pd.DataFrame
        DataFrame with missing values handled.

    Example
    -------
    >>> df_clean = handle_missing_values(df, numeric_strategy="median")
    """
    # Drop columns with excessive missing values
    before_cols = df.shape[1]
    missing_frac = df.isnull().mean()
    cols_to_drop = missing_frac[missing_frac > drop_threshold].index.tolist()
    if cols_to_drop:
        logger.warning(f"Dropping high-missing columns (>{drop_threshold*100:.0f}%): {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)
    logger.info(f"Columns dropped due to high missingness: {before_cols - df.shape[1]}")

    # Numeric columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        n_missing = df[col].isnull().sum()
        if n_missing == 0:
            continue
        if numeric_strategy == "mean":
            fill_val = df[col].mean()
        elif numeric_strategy == "median":
            fill_val = df[col].median()
        elif numeric_strategy == "drop":
            df = df.dropna(subset=[col])
            continue
        else:
            fill_val = df[col].median()
        df[col] = df[col].fillna(fill_val)
        logger.info(f"  Imputed '{col}': {n_missing} values with {numeric_strategy} ({fill_val:.4f})")

    # Categorical columns
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        n_missing = df[col].isnull().sum()
        if n_missing == 0:
            continue
        if categorical_strategy == "mode":
            fill_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
        elif categorical_strategy == "unknown":
            fill_val = "Unknown"
        elif categorical_strategy == "drop":
            df = df.dropna(subset=[col])
            continue
        else:
            fill_val = "Unknown"
        df[col] = df[col].fillna(fill_val)
        logger.info(f"  Imputed '{col}': {n_missing} values with '{fill_val}'")

    logger.info(f"Missing values after handling: {df.isnull().sum().sum()}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Duplicate Removal
# ══════════════════════════════════════════════════════════════════════════════

def remove_duplicates(
    df: pd.DataFrame,
    subset: list[str] | None = None,
    keep: str = "first",
) -> pd.DataFrame:
    """
    Remove duplicate rows from the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
    subset : list[str], optional
        Columns to consider for identifying duplicates. None = all columns.
    keep : str
        Which duplicate to keep: 'first', 'last', or False (drop all).

    Returns
    -------
    pd.DataFrame

    Example
    -------
    >>> df_clean = remove_duplicates(df, subset=["product_id"])
    """
    before = len(df)
    df = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
    removed = before - len(df)
    logger.info(f"Duplicates removed: {removed:,} rows  ({before:,} → {len(df):,})")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Outlier Detection & Treatment
# ══════════════════════════════════════════════════════════════════════════════

def handle_outliers(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    method: str = "iqr",
    action: str = "clip",
    z_threshold: float = 3.0,
    iqr_factor: float = 1.5,
) -> pd.DataFrame:
    """
    Detect and treat outliers using IQR or Z-score methods.

    Parameters
    ----------
    df : pd.DataFrame
    columns : list[str], optional
        Numeric columns to process. None = all numeric columns.
    method : str
        'iqr' or 'zscore'.
    action : str
        'clip' (winsorize), 'drop', or 'flag' (add boolean column).
    z_threshold : float
        Z-score threshold when method='zscore'.
    iqr_factor : float
        IQR multiplier for fence calculation.

    Returns
    -------
    pd.DataFrame

    Example
    -------
    >>> df_clean = handle_outliers(df, columns=["price", "discount"], method="iqr")
    """
    num_cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()

    for col in num_cols:
        if col not in df.columns:
            continue

        if method == "iqr":
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - iqr_factor * iqr, q3 + iqr_factor * iqr
        else:  # zscore
            mean, std = df[col].mean(), df[col].std()
            lower = mean - z_threshold * std
            upper = mean + z_threshold * std

        n_outliers = ((df[col] < lower) | (df[col] > upper)).sum()

        if action == "clip":
            df[col] = df[col].clip(lower=lower, upper=upper)
        elif action == "drop":
            df = df[(df[col] >= lower) & (df[col] <= upper)]
        elif action == "flag":
            df[f"{col}_outlier"] = ((df[col] < lower) | (df[col] > upper)).astype(int)

        logger.info(f"  Outliers in '{col}': {n_outliers} ({method} | {action})")

    return df.reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Normalization / Scaling
# ══════════════════════════════════════════════════════════════════════════════

def normalize_features(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    method: str = "minmax",
) -> pd.DataFrame:
    """
    Scale numeric features using Min-Max or Standard (Z-score) normalization.

    Parameters
    ----------
    df : pd.DataFrame
    columns : list[str], optional
        Columns to scale. None = all numeric columns.
    method : str
        'minmax' (scales to [0, 1]) or 'standard' (zero mean, unit variance).

    Returns
    -------
    pd.DataFrame

    Example
    -------
    >>> df_scaled = normalize_features(df, columns=["price", "rating"], method="minmax")
    """
    num_cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    scaler = MinMaxScaler() if method == "minmax" else StandardScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])
    logger.info(f"Normalization ({method}) applied to: {num_cols}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Categorical Encoding
# ══════════════════════════════════════════════════════════════════════════════

def encode_categoricals(
    df: pd.DataFrame,
    onehot_cols: list[str] | None = None,
    label_cols: list[str] | None = None,
    max_onehot_cardinality: int = 15,
) -> pd.DataFrame:
    """
    Encode categorical variables using One-Hot or Label encoding.

    Parameters
    ----------
    df : pd.DataFrame
    onehot_cols : list[str], optional
        Columns for One-Hot Encoding. Auto-detected if None.
    label_cols : list[str], optional
        Columns for Label Encoding.
    max_onehot_cardinality : int
        Auto one-hot only columns with cardinality ≤ this value.

    Returns
    -------
    pd.DataFrame

    Example
    -------
    >>> df_encoded = encode_categoricals(df, onehot_cols=["gender", "category"])
    """
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Auto-detect one-hot columns if not specified
    if onehot_cols is None and label_cols is None:
        onehot_cols = [c for c in cat_cols if df[c].nunique() <= max_onehot_cardinality]
        label_cols = [c for c in cat_cols if df[c].nunique() > max_onehot_cardinality]

    # One-Hot Encoding
    if onehot_cols:
        df = pd.get_dummies(df, columns=onehot_cols, drop_first=True)
        logger.info(f"One-Hot Encoded: {onehot_cols}")

    # Label Encoding
    if label_cols:
        le = LabelEncoder()
        for col in label_cols:
            if col in df.columns:
                df[col] = le.fit_transform(df[col].astype(str))
        logger.info(f"Label Encoded: {label_cols}")

    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — Export
# ══════════════════════════════════════════════════════════════════════════════

def export_processed(
    df: pd.DataFrame,
    filename: str = "processed_fashion_data",
    formats: list[str] | None = None,
) -> dict[str, Path]:
    """
    Export processed DataFrame to one or more file formats.

    Parameters
    ----------
    df : pd.DataFrame
    filename : str
        Base filename (without extension).
    formats : list[str]
        List of formats: 'csv', 'parquet', 'excel'. Defaults to ['csv'].

    Returns
    -------
    dict[str, Path]
        Mapping of format → file path.

    Example
    -------
    >>> paths = export_processed(df, formats=["csv", "parquet"])
    """
    formats = formats or ["csv"]
    paths = {}

    for fmt in formats:
        out = PROCESSED_DIR / f"{filename}.{fmt}"
        if fmt == "csv":
            df.to_csv(out, index=False)
        elif fmt == "parquet":
            df.to_parquet(out, index=False)
        elif fmt == "excel":
            df.to_excel(out, index=False)
        paths[fmt] = out
        logger.info(f"Exported processed data → {out}")

    return paths


# ══════════════════════════════════════════════════════════════════════════════
# Full Pipeline Runner
# ══════════════════════════════════════════════════════════════════════════════

def run_pipeline(df: pd.DataFrame, required_columns: list[str] | None = None) -> pd.DataFrame:
    """
    Run the complete preprocessing pipeline on a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw input DataFrame.
    required_columns : list[str], optional
        Columns to validate.

    Returns
    -------
    pd.DataFrame
        Fully preprocessed DataFrame.
    """
    logger.info("═" * 60)
    logger.info("STARTING FASHION DATA PREPROCESSING PIPELINE")
    logger.info("═" * 60)

    if required_columns:
        df = validate_schema(df, required_columns)

    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = handle_outliers(df, method="iqr", action="clip")
    df = encode_categoricals(df)
    # Note: Normalization is done AFTER encoding
    df = normalize_features(df, method="minmax")

    logger.info("═" * 60)
    logger.info(f"PIPELINE COMPLETE — Final shape: {df.shape}")
    logger.info("═" * 60)
    return df


if __name__ == "__main__":
    # Demo with synthetic data
    logger.info("Running pipeline with synthetic fashion dataset demo...")

    np.random.seed(42)
    n = 500
    demo_df = pd.DataFrame({
        "product_id": range(1, n + 1),
        "product_name": [f"Product_{i}" for i in range(1, n + 1)],
        "category": np.random.choice(["Tops", "Bottoms", "Dresses", "Footwear", "Accessories"], n),
        "gender": np.random.choice(["Male", "Female", "Unisex"], n),
        "price": np.random.normal(50, 20, n).clip(5, 300),
        "discount_pct": np.random.uniform(0, 60, n),
        "rating": np.random.uniform(1, 5, n),
        "reviews_count": np.random.randint(0, 5000, n),
        "stock": np.random.randint(0, 1000, n),
        "season": np.random.choice(["Spring", "Summer", "Autumn", "Winter"], n),
    })

    # Introduce missing values
    for col in ["price", "rating", "gender"]:
        idx = np.random.choice(n, size=30, replace=False)
        demo_df.loc[idx, col] = np.nan

    # Introduce duplicates
    demo_df = pd.concat([demo_df, demo_df.iloc[:20]], ignore_index=True)

    processed = run_pipeline(demo_df)
    export_processed(processed, filename="demo_fashion_processed", formats=["csv"])
    logger.info("Demo complete! Check data/processed/ for output.")
