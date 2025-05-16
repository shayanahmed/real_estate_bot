import requests
from bs4 import BeautifulSoup
import pandas as pd

# Target URL
URL = 'https://www.bassanesi.com.br/alugar/cidade/caxias-do-sul/1/'

# Send request
response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

# All property containers
properties = soup.find_all('div', class_='box-imovel')

# Extract data
data = []
for prop in properties:
    try:
        title = prop.find('h2').text.strip()
        size = prop.find('ul').text.strip()
        price = prop.find('span', class_='valor').text.strip()
        link = prop.find('a', class_='info')['href']
        code = prop.find('span', class_='co').text.strip()

        data.append({
            'Code': code,
            'Title': title,
            'Size': size,
            'Price': price,
            'Link': link
        })
    except Exception as e:
        print(f"Skipping one listing due to error: {e}")

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('listings_today.csv', index=False)
print("✅ Data scraped and saved to 'listings_today.csv'")
