# 👗 Week 2: Data Acquisition & Preprocessing for Fashion & Apparel Industry

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Industry](https://img.shields.io/badge/Industry-Fashion%20%26%20Apparel-pink)

> **Week 2 Task** | Data Science Internship Program  
> A comprehensive guide and reproducible pipeline for sourcing, cleaning, and preparing fashion industry data for analysis.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Data Sources](#data-sources)
- [Preprocessing Pipeline](#preprocessing-pipeline)
- [Installation](#installation)
- [Usage](#usage)
- [Notebooks](#notebooks)
- [Report](#report)
- [Challenges & Solutions](#challenges--solutions)
- [Contributing](#contributing)

---

## 🎯 Overview

This project demonstrates a complete **Data Acquisition and Preprocessing pipeline** tailored for the **Fashion & Apparel Industry**. It covers:

- Identifying public data sources relevant to fashion trends, consumer behavior, and sales analytics
- Data cleaning strategies (missing values, duplicates, outliers)
- Normalization, feature engineering, and transformation techniques
- A reproducible, well-documented methodology for junior analysts

---

## 📁 Project Structure

```
week2-fashion-data-preprocessing/
│
├── 📂 data/
│   ├── 📂 raw/                    # Raw unprocessed datasets
│   └── 📂 processed/              # Cleaned & transformed datasets
│
├── 📂 notebooks/
│   ├── 01_data_acquisition.ipynb  # Data sourcing & scraping guide
│   ├── 02_eda.ipynb               # Exploratory Data Analysis
│   └── 03_preprocessing.ipynb     # Full preprocessing pipeline
│
├── 📂 src/
│   ├── data_acquisition.py        # Data sourcing utilities
│   ├── preprocessing.py           # Preprocessing functions
│   ├── feature_engineering.py     # Feature engineering module
│   └── utils.py                   # Helper utilities
│
├── 📂 reports/
│   └── Week2_Fashion_DataPreprocessing_Report.docx
│
├── 📂 docs/
│   └── data_sources.md            # Detailed data source documentation
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🌐 Data Sources

### 1. Public Datasets & Platforms

| Source | Type | URL | Description |
|--------|------|-----|-------------|
| **Kaggle** | CSV / JSON | [kaggle.com](https://www.kaggle.com) | Fashion MNIST, H&M Recommendations, Zalando datasets |
| **H&M Group Open Data** | CSV | [Kaggle H&M](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) | Customer transactions & article metadata |
| **Fashion-MNIST** | Image/CSV | [GitHub](https://github.com/zalandoresearch/fashion-mnist) | 70,000 grayscale clothing images |
| **Google Trends** | CSV | [trends.google.com](https://trends.google.com) | Fashion keyword search trends |
| **Statista** | Reports | [statista.com](https://www.statista.com) | Global apparel market statistics |
| **UN Comtrade** | CSV/API | [comtrade.un.org](https://comtrade.un.org) | International textile trade data |
| **FRED (Federal Reserve)** | API | [fred.stlouisfed.org](https://fred.stlouisfed.org) | Retail clothing sales data (US) |
| **Data.gov** | CSV | [data.gov](https://data.gov) | US retail & manufacturing datasets |
| **Open Fashion** | JSON | [openfashion.org](https://github.com/tensorflow/lucid) | Open-source fashion data |
| **World Bank** | API | [data.worldbank.org](https://data.worldbank.org) | Textile industry economic indicators |

### 2. Web Scraping Targets (Public/Legal)

| Platform | Data Available |
|----------|---------------|
| **ASOS** | Product listings, prices, categories |
| **Myntra** | Trends, ratings, reviews |
| **Amazon Fashion** | Prices, reviews, bestsellers |
| **Pinterest Trends** | Trending styles, colors, aesthetics |

---

## ⚙️ Preprocessing Pipeline

```
Raw Data → Ingestion → Validation → Cleaning → Transformation → Feature Engineering → Export
```

### Step-by-Step

1. **Data Ingestion** – Load CSVs, APIs, or web-scraped data
2. **Schema Validation** – Check column names, data types, expected ranges
3. **Missing Value Handling** – Mean/median imputation, forward-fill, or drop
4. **Duplicate Removal** – Detect exact and fuzzy duplicates
5. **Outlier Detection** – IQR method, Z-score filtering
6. **Normalization** – Min-Max Scaling, StandardScaler
7. **Encoding** – Label Encoding, One-Hot Encoding for categorical features
8. **Feature Engineering** – Create season, price-tier, discount-rate features
9. **Data Export** – Save processed data as CSV / Parquet

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/week2-fashion-data-preprocessing.git
cd week2-fashion-data-preprocessing

# Create a virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage

```bash
# Run the full preprocessing pipeline
python src/preprocessing.py

# Run data acquisition
python src/data_acquisition.py

# Launch Jupyter notebooks
jupyter notebook notebooks/
```

---

## 📓 Notebooks

| Notebook | Description |
|----------|-------------|
| [`01_data_acquisition.ipynb`](notebooks/01_data_acquisition.ipynb) | How to fetch data from Kaggle, APIs, and web scraping |
| [`02_eda.ipynb`](notebooks/02_eda.ipynb) | Exploratory Data Analysis with visualizations |
| [`03_preprocessing.ipynb`](notebooks/03_preprocessing.ipynb) | Full preprocessing pipeline walkthrough |

---

## 📄 Report

The full methodology report is available in the [`reports/`](reports/) folder:  
📑 **`Week2_Fashion_DataPreprocessing_Report.docx`**

---

## ⚠️ Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Inconsistent size formats (S/M/L vs 8/10/12) | Standardized size mapping dictionary |
| Missing price data | Median imputation grouped by category |
| Duplicate product listings (minor text changes) | Fuzzy matching with `rapidfuzz` |
| Seasonal data skew | Time-series decomposition & stratified sampling |
| Multi-language product descriptions | Language detection + translation with `langdetect` |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📜 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

*Developed as part of the Data Science Internship Program — Week 2 Task*
