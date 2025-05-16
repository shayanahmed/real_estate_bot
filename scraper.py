import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import time
import csv

# Setup session with retry strategy
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
            size = None
            price = None
            link = item.select_one("a.info")["href"]

            # Extract size, price, and other details
            ul = item.select_one("a.info ul")
            if ul:
                details = [li.text.strip() for li in ul.find_all("li")]
                # Assuming size is in details - look for something with m²
                size_candidates = [d for d in details if "m²" in d]
                size = size_candidates[0] if size_candidates else None

            price_tag = item.select_one("span.valor")
            price = price_tag.text.strip() if price_tag else None

            listings.append({
                "Code": code,
                "Title": title,
                "Size": size,
                "Price": price,
                "Link": link
            })
        except Exception as e:
            print(f"Failed to parse a listing: {e}")

    return listings


def scrape_and_save(max_pages=2):
    all_listings = []
    for page in range(1, max_pages + 1):
        listings = scrape_bassanesi(page)
        if not listings:
            print(f"No listings found on page {page}, stopping.")
            break
        all_listings.extend(listings)
        time.sleep(2)  # be polite and avoid hammering the server

    # Save to CSV
    keys = ["Code", "Title", "Size", "Price", "Link"]
    with open("listings_today.csv", "w", newline="", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_listings)

    print(f"Saved {len(all_listings)} listings to listings_today.csv")


if __name__ == "__main__":
    scrape_and_save(max_pages=2)
# This script scrapes the listings from Bassanesi's website and saves them to a CSV file.
# It handles pagination and retries on request failures.    