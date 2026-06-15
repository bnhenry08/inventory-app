import streamlit as st
import pandas as pd
import os

FILE = "inventory.csv"

# -----------------------------
# 📌 FIXED COLUMN SCHEMA (GLOBAL)
# -----------------------------
COLUMNS = [
    "Item",
    "Category",
    "Quantity",
    "Freezer Name",
    "Rack Number",
    "Box Number"
]

# -----------------------------
# 🔐 LOGIN
# -----------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("📦 Inventory Login")

    password = st.text_input("Enter password", type="password")

    if st.button("Login"):
        if password == st.secrets["password"]:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong password")

    st.stop()

# -----------------------------
# 📂 LOAD / SAVE SAFE DATA
# -----------------------------
def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)

        # ensure all required columns exist
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""

        return df[COLUMNS]

    return pd.DataFrame(columns=COLUMNS)

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
        new_row = pd.DataFrame([[
            item,
            category,
            quantity,
            freezer_name,
            rack_number,
            box_number
        ]], columns=COLUMNS)

        inventory = pd.concat([inventory, new_row], ignore_index=True)
        save_data(inventory)

        st.success(f"Added {item}")
        st.rerun()

# -----------------------------
# 🔍 SEARCH
# -----------------------------
st.header("Search")

search = st.text_input("Search items")

if search:
    filtered = inventory[
        inventory.astype(str).apply(
            lambda row: row.str.contains(search, case=False, na=False).any(),
            axis=1
        )
    ]
else:
    filtered = inventory

st.dataframe(filtered, use_container_width=True)

# -----------------------------
# 🗑 DELETE ITEM
# -----------------------------
st.header("Delete Item")

if len(inventory) > 0:
    inventory_reset = inventory.reset_index(drop=True)

    delete_index = st.selectbox(
        "Select row to delete",
        inventory_reset.index,
        format_func=lambda x: (
            f"{inventory_reset.loc[x, 'Item']} | "
            f"{inventory_reset.loc[x, 'Freezer Name']} | "
            f"Rack {inventory_reset.loc[x, 'Rack Number']} | "
            f"Box {inventory_reset.loc[x, 'Box Number']}"
        )
    )

    if st.button("Delete"):
        inventory = inventory_reset.drop(delete_index)
        save_data(inventory)
        st.success("Item deleted")
        st.rerun()

# -----------------------------
# ⬇ DOWNLOAD CSV
# -----------------------------
csv = inventory.to_csv(index=False)

st.download_button(
    "Download CSV",
    csv,
    "inventory.csv",
    "text/csv"
)
