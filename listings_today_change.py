import pandas as pd

def clean_price(price):
    if pd.isna(price):
        return None
    if isinstance(price, str):
        # Remove comments after '#'
        price = price.split('#')[0]
        # Remove 'R$', spaces and strip
        price = price.replace('R$', '').replace(' ', '').strip()
        # Remove thousands separator dots
        price = price.replace('.', '')
        # Replace comma with dot if decimal separator
        price = price.replace(',', '.')
    try:
        return float(price)
    except Exception as e:
        print(f"Warning: Unable to convert price '{price}' to float. Error: {e}")
        return None

# Load today's listings
df_today_test = pd.read_csv('listings_today.csv')

# Clean the price column to numeric
df_today_test['CleanPrice'] = df_today_test['Price'].apply(clean_price)

print("Raw prices sample:")
print(df_today_test['Price'].head())

# Check how many prices could not be converted
num_none = df_today_test['CleanPrice'].isna().sum()
if num_none > 0:
    print(f"Number of prices that could not be converted: {num_none}")

# Example modification to test price changed detection
if df_today_test['CleanPrice'].iloc[0] is not None:
    df_today_test.loc[0, 'CleanPrice'] = df_today_test.loc[0, 'CleanPrice'] * 1.1  # 10% increase
else:
    print("First price is None, can't multiply.")

# Save cleaned today's listings for next steps or testing
df_today_test.to_csv('listings_today_cleaned.csv', index=False)

# Load yesterday's listings (assuming you have it saved from before)
df_yesterday = pd.read_csv('listings_yesterday.csv')
df_yesterday['CleanPrice'] = df_yesterday['Price'].apply(clean_price)

# Find new listings (present today but not yesterday)
new_listings = df_today_test[~df_today_test['Title'].isin(df_yesterday['Title'])]

# Find removed listings (present yesterday but not today)
removed_listings = df_yesterday[~df_yesterday['Title'].isin(df_today_test['Title'])]

# Find price changed listings (same title but price changed)
merged = pd.merge(df_today_test, df_yesterday, on='Title', suffixes=('_today', '_yesterday'))
price_changed_listings = merged[merged['CleanPrice_today'] != merged['CleanPrice_yesterday']]

# Save outputs
new_listings.to_csv('new_listings.csv', index=False)
removed_listings.to_csv('removed_listings.csv', index=False)
price_changed_listings.to_csv('price_changed_listings.csv', index=False)

print(f"New listings: {len(new_listings)}")
print(f"Removed listings: {len(removed_listings)}")
print(f"Price changed listings: {len(price_changed_listings)}")

# For debug: print samples
print("\nSample new listings:")
print(new_listings.head())
print("\nSample removed listings:")
print(removed_listings.head())
print("\nSample price changed listings:")
print(price_changed_listings.head())
