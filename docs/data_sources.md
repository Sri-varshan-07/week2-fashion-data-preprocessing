# Data Sources for Fashion & Apparel Analysis

## 1. Fashion Datasets on Kaggle

| Dataset | Link | Key Columns |
|---------|------|-------------|
| H&M Personalized Fashion Recommendations | [Link](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data) | article_id, product_type, colour_group, customer_id, t_dat (transaction date) |
| Fashion Product Images | [Link](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset) | gender, masterCategory, subCategory, articleType, season, year, usage |
| Clothing Fit Dataset | [Link](https://www.kaggle.com/datasets/rmisra/clothing-fit-dataset-for-size-recommendation) | fit, user_id, bust_size, height, item_id, rating |
| Women's E-Commerce Clothing Reviews | [Link](https://www.kaggle.com/datasets/nicapotato/womens-ecommerce-clothing-reviews) | Clothing ID, Age, Title, Review Text, Rating, Recommended IND |
| Fashion Retail Sales | [Link](https://www.kaggle.com/datasets/sahilprajapati13/retail-analysis-large-dataset) | Category, Product, Price, Quantity, Revenue |

---

## 2. Open Government & Economic Databases

| Source | URL | Data Type |
|--------|-----|-----------|
| US Census Bureau — Retail Trade | https://www.census.gov/retail | Monthly retail clothing sales |
| Bureau of Labor Statistics | https://www.bls.gov | Apparel price index, employment |
| FRED (Federal Reserve) | https://fred.stlouisfed.org | Retail: Clothing & Accessories (RSCCASN) |
| UN Comtrade | https://comtrade.un.org | Textile & apparel import/export |
| World Bank DataBank | https://databank.worldbank.org | Textile industry GDP contributions |
| OECD Statistics | https://stats.oecd.org | Consumer spending on clothing |

---

## 3. Google Trends — Fashion Keywords to Monitor

```
Keywords:
- "sustainable fashion"
- "fast fashion"
- "streetwear"
- "luxury fashion"
- "athleisure"
- "vintage clothing"
- "thrift store fashion"
- "capsule wardrobe"
```

Access via: https://trends.google.com or the `pytrends` Python library.

---

## 4. Social Media & Consumer Sentiment

| Platform | Data Type | Access Method |
|----------|-----------|---------------|
| Twitter/X | Fashion hashtags, sentiment | Twitter API v2 |
| Reddit (r/fashion, r/femalefashionadvice) | Reviews, discussions | Reddit PSAW API |
| Pinterest | Trending styles | Pinterest API |
| Instagram | Hashtag trends | Instagram Basic Display API |

---

## 5. Industry Reports (Free Versions)

| Report | Publisher | URL |
|--------|-----------|-----|
| State of Fashion | McKinsey / BOF | https://www.mckinsey.com/industries/retail/our-insights/state-of-fashion |
| Textile Exchange Report | Textile Exchange | https://textileexchange.org/reports |
| Global Apparel Outlook | Euromonitor | https://www.euromonitor.com |

---

## 6. Notes on Data Licensing

> Always verify the license before using any dataset commercially.
> 
> - Kaggle datasets: Check individual dataset license (CC0, CC BY, Custom)
> - Government data: Generally public domain (CC0)
> - Web scraped data: Must comply with robots.txt and Terms of Service
