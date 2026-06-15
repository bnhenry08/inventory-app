import streamlit as st
import pandas as pd
import os

FILE = "inventory.csv"

# Load existing data
if os.path.exists(FILE):
    inventory = pd.read_csv(FILE)
else:
    inventory = pd.DataFrame(columns=["Item", "Category", "Quantity", "Location"])

st.title("📦 Inventory Manager")

# Add item
st.header("Add Item")

with st.form("add_item"):
    item = st.text_input("Item Name")
    category = st.text_input("Category")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    location = st.text_input("Location")

    submitted = st.form_submit_button("Add")

    if submitted:
        new_row = pd.DataFrame([[item, category, quantity, location]],
                               columns=["Item", "Category", "Quantity", "Location"])
        inventory = pd.concat([inventory, new_row], ignore_index=True)
        inventory.to_csv(FILE, index=False)
        st.success(f"Added {item}")

# Search
st.header("Search")
search = st.text_input("Search items")

if search:
    filtered = inventory[inventory["Item"].str.contains(search, case=False, na=False)]
else:
    filtered = inventory

# Show table
st.dataframe(filtered, use_container_width=True)

# Delete
st.header("Delete Item")

if len(inventory) > 0:
    index = st.selectbox("Select row to delete", inventory.index)

    if st.button("Delete"):
        inventory = inventory.drop(index).reset_index(drop=True)
        inventory.to_csv(FILE, index=False)
        st.success("Item deleted")

# Download
csv = inventory.to_csv(index=False)

st.download_button("Download CSV", csv, "inventory.csv", "text/csv")
