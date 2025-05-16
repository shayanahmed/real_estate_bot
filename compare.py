import pandas as pd

print("Comparing listings_yesterday.csv with listings_today_cleaned.csv")

df_yesterday = pd.read_csv("listings_yesterday.csv")
df_today = pd.read_csv("listings_today_cleaned.csv")

# Normalize links and codes
df_yesterday["Link"] = df_yesterday["Link"].astype(str)
df_today["Link"] = df_today["Link"].astype(str)

# Identify new listings
new = df_today[~df_today["Code"].isin(df_yesterday["Code"])]

# Identify removed listings
removed = df_yesterday[~df_yesterday["Code"].isin(df_today["Code"])]

# Identify price changes
merged = pd.merge(df_today, df_yesterday, on="Code", suffixes=("_today", "_yesterday"))
price_changed = merged[merged["CleanPrice_today"] != merged["CleanPrice_yesterday"]]

print("\n🆕 New Listings:", len(new))
print(new.head())

print("\n❌ Removed Listings:", len(removed))
print(removed.head())

print("\n💲 Price Changed Listings:", len(price_changed))
print(price_changed[["Code", "Title_today", "CleanPrice_today", "CleanPrice_yesterday", "Link_today"]].head())
