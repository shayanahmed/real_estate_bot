import pandas as pd
import os

# Load data
df_today = pd.read_csv('listings_today.csv')
df_yesterday_path = 'listings_yesterday.csv'

if os.path.exists(df_yesterday_path):
    df_yesterday = pd.read_csv(df_yesterday_path)
else:
    # If yesterday's data not found, create it from today and exit
    df_today.to_csv(df_yesterday_path, index=False)
    print("Created 'listings_yesterday.csv' from today's data for baseline comparison.")
    exit()

# Unique key column (adjust if you use different)
key_col = 'Code'

# New listings (in today but not yesterday)
new_listings = df_today[~df_today[key_col].isin(df_yesterday[key_col])]

# Removed listings (in yesterday but not today)
removed_listings = df_yesterday[~df_yesterday[key_col].isin(df_today[key_col])]

# Merge on key to find price changes
merged = df_today.merge(df_yesterday, on=key_col, suffixes=('_today', '_yesterday'))

# Find price changed listings
price_changed = merged[merged['Price_today'] != merged['Price_yesterday']]

# Save outputs
new_listings.to_csv('new_listings.csv', index=False)
removed_listings.to_csv('removed_listings.csv', index=False)
price_changed.to_csv('price_changed_listings.csv', index=False)

print(f"New listings: {len(new_listings)}")
print(f"Removed listings: {len(removed_listings)}")
print(f"Price changed listings: {len(price_changed)}")

# Update yesterday's baseline file for next run
df_today.to_csv(df_yesterday_path, index=False)
