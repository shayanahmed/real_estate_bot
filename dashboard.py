import streamlit as st
import pandas as pd
import os

st.title("Real Estate Listings Dashboard")

# Helper function to load CSV safely
def load_csv(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        st.warning(f"File '{filename}' not found.")
        return pd.DataFrame()  # empty dataframe

# Load your data files with fallback
price_changes = load_csv('price_changed_listings.csv')
new_listings = load_csv('new_listings.csv')
removed_listings = load_csv('removed_listings.csv')

# Show data summaries or tables if data exists
if not price_changes.empty:
    st.subheader("Price Changed Listings")
    st.dataframe(price_changes)
else:
    st.info("No price changed listings data available.")

if not new_listings.empty:
    st.subheader("New Listings")
    st.dataframe(new_listings)
else:
    st.info("No new listings data available.")

if not removed_listings.empty:
    st.subheader("Removed Listings")
    st.dataframe(removed_listings)
else:
    st.info("No removed listings data available.")
