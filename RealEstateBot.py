import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import time
import csv
import os
import streamlit as st
import pandas as pd

# Set up retry-enabled session
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount('http://', adapter)
session.mount('https://', adapter)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/113.0.0.0 Safari/537.36"
    )
}

# Scraper function
def scrape_bassanesi(page):
    url = f"https://www.bassanesi.com.br/comprar/cidade/caxias-do-sul/{page}"
    print(f"Scraping {url}")
    try:
        response = session.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed for page {page}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    listings = []

    for item in soup.select("div.col-lg-3.col-sm-6.col-12.my-3"):
        try:
            code = item.select_one("span.co").text.strip()
            title = item.select_one("a.info h2").text.strip()
            link = item.select_one("a.info")["href"]
            price_tag = item.select_one("span.valor")
            price = price_tag.text.strip() if price_tag else None

            ul = item.select_one("a.info ul")
            size = None
            if ul:
                details = [li.text.strip() for li in ul.find_all("li")]
                size_candidates = [d for d in details if "m²" in d]
                size = size_candidates[0] if size_candidates else None

            listings.append({
                "Code": code,
                "Title": title,
                "Size": size,
                "Price": price,
                "Link": link
            })
        except Exception as e:
            print(f"Failed to parse listing: {e}")
    return listings

# Save listings to CSV
def scrape_and_save(max_pages=2):
    all_listings = []
    for page in range(1, max_pages + 1):
        listings = scrape_bassanesi(page)
        if not listings:
            break
        all_listings.extend(listings)
        time.sleep(2)
    if all_listings:
        keys = ["Code", "Title", "Size", "Price", "Link"]
        with open("listings_today.csv", "w", newline="", encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_listings)
        print(f"Saved {len(all_listings)} listings to listings_today.csv")
        return len(all_listings)
    return 0

# Compare today's and yesterday's listings
def compare_today_vs_yesterday():
    try:
        today_df = pd.read_csv("listings_today.csv")
        yesterday_df = pd.read_csv("listings_yesterday.csv")
    except Exception as e:
        st.error(f"Error loading CSV files: {e}")
        return None, None, None

    today_df["Code"] = today_df["Code"].astype(str)
    yesterday_df["Code"] = yesterday_df["Code"].astype(str)

    merged_df = pd.merge(today_df, yesterday_df, on="Code", how="outer", suffixes=("_today", "_yesterday"), indicator=True)

    new_listings = merged_df[merged_df["_merge"] == "left_only"]
    removed_listings = merged_df[merged_df["_merge"] == "right_only"]

    changed_listings = merged_df[
        (merged_df["_merge"] == "both") &
        (
            (merged_df["Price_today"] != merged_df["Price_yesterday"]) |
            (merged_df["Title_today"] != merged_df["Title_yesterday"]) |
            (merged_df["Size_today"] != merged_df["Size_yesterday"])
        )
    ]

    return new_listings, removed_listings, changed_listings

# Streamlit UI
st.set_page_config(page_title="Real Estate Scraper", layout="wide")

st.title("🏡 Real Estate Scraper Dashboard")

# Run scraper
if st.button("📥 Run Scraper Now"):
    total = scrape_and_save(max_pages=2)
    if total > 0:
        st.success(f"Scraped and saved {total} listings to listings_today.csv")
    else:
        st.error("No listings scraped. Check the website or your connection.")

# Compare files
if st.button("🔍 Compare Today vs Yesterday"):
    if not os.path.exists("listings_yesterday.csv"):
        st.error("listings_yesterday.csv not found!")
    else:
        new_df, removed_df, changed_df = compare_today_vs_yesterday()
        if new_df is not None:
            st.subheader("🆕 New Listings")
            st.dataframe(new_df[["Code", "Title_today", "Price_today", "Link_today"]])

            st.subheader("❌ Removed Listings")
            st.dataframe(removed_df[["Code", "Title_yesterday", "Price_yesterday", "Link_yesterday"]])

            st.subheader("🔁 Changed Listings")
            st.dataframe(changed_df[[
                "Code", "Title_today", "Price_yesterday", "Price_today", "Link_today"
            ]])
