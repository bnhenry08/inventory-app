import streamlit as st
import pandas as pd
import os

FILE = "inventory.csv"

# -----------------------------
# 🔐 SIMPLE PASSWORD LOGIN (OPTIONAL)
# -----------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("📦 Inventory Login")

    password = st.text_input("Enter password", type="password")

    if st.button("Login"):
        # You can later move this to st.secrets
        if password == st.secrets["password"]:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong password")

    st.stop()

# -----------------------------
# 📂 LOAD DATA SAFELY
# -----------------------------
def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    return pd.DataFrame(columns=["Item", "Category", "Quantity", "Freezer Name", "Rack Number", "Box Number"])

def save_data(df):
    df.to_csv(FILE, index=False)

inventory = load_data()

st.title("📦 Inventory Manager")

# -----------------------------
# ➕ ADD ITEM
# -----------------------------
st.header("Add Item")

with st.form("add_item"):
    item = st.text_input("Item Name")
    category = st.text_input("Category")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    freezer_name = st.text_input("Freezer Name")
    rack_number = st.text_input("Rack Number")
    box_number = st.text_input("Box Number")

    submitted = st.form_submit_button("Add")

    if submitted and item:
        new_row = pd.DataFrame([[item, category, quantity, freezer_name, rack_number, box_number]],
                               columns=inventory.columns)
        inventory = pd.concat([inventory, new_row], ignore_index=True)
        save_data(inventory)
        st.success(f"Added {item}")
        st.rerun()

# -----------------------------
# 🔍 SEARCH
# -----------------------------
st.header("Search")
search = st.text_input("Search items")

filtered = inventory.copy()

if search:
    filtered = filtered[
        filtered["Item"].str.contains(search, case=False, na=False)
    ]

st.dataframe(filtered, use_container_width=True)

# -----------------------------
# 🗑 DELETE (FIXED SAFE INDEXING)
# -----------------------------
st.header("Delete Item")

if len(inventory) > 0:
    # show display index safely
    inventory_reset = inventory.reset_index(drop=True)

    delete_index = st.selectbox(
        "Select row to delete",
        inventory_reset.index,
        format_func=lambda x: f"{inventory_reset.loc[x, 'Item']} | {inventory_reset.loc[x, 'Location']}"
    )

    if st.button("Delete"):
        inventory = inventory_reset.drop(delete_index)
        save_data(inventory)
        st.success("Item deleted")
        st.rerun()

# -----------------------------
# ⬇ DOWNLOAD
# -----------------------------
csv = inventory.to_csv(index=False)

st.download_button(
    "Download CSV",
    csv,
    "inventory.csv",
    "text/csv"
)
