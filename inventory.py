import streamlit as st
import pandas as pd
import os

FILE = "inventory.csv"

# -----------------------------
# 📌 COLUMN SCHEMA
# -----------------------------
COLUMNS = [
    "Item",
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
# 📂 LOAD / SAVE
# -----------------------------
def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)

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
    quantity = st.number_input("Quantity", min_value=0, step=1)
    freezer_name = st.text_input("Freezer Name")
    rack_number = st.text_input("Rack Number")
    box_number = st.text_input("Box Number")

    submitted = st.form_submit_button("Add")

    if submitted and item:
        new_row = pd.DataFrame([[
            item,
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
# 🔍 SEARCH (GENERAL)
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
# 🗑 DELETE (SEARCH → SELECT ROW → DELETE ONE)
# -----------------------------
st.header("Delete Item (select one row)")

delete_search = st.text_input("Search item to delete")

if delete_search:
    matches = inventory[
        inventory["Item"].str.contains(delete_search, case=False, na=False)
    ].reset_index()

    if len(matches) == 0:
        st.warning("No matching items found.")
    else:
        st.write("Select the exact row to delete:")

        # build label for dropdown
        options = {
            i: f"{row['Item']} | Freezer:{row['Freezer Name']} | Rack:{row['Rack Number']} | Box:{row['Box Number']}"
            for i, row in matches.iterrows()
        }

        selected = st.selectbox(
            "Matching rows",
            list(options.keys()),
            format_func=lambda x: options[x]
        )

        if st.button("Delete selected row"):
            # map back to original index
            original_index = matches.loc[selected, "index"]

            inventory = inventory.drop(original_index).reset_index(drop=True)
            save_data(inventory)

            st.success("Row deleted")
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
