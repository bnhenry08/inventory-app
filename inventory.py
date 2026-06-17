import streamlit as st
import pandas as pd
import os
from git import Repo

FILE = "inventory.csv"

# -----------------------------
# GITHUB SYNC
# -----------------------------
REPO_PATH = os.path.dirname(os.path.abspath(__file__))

def push_to_github(commit_message="Inventory updated"):
    try:
        repo = Repo(REPO_PATH)

        repo.git.add(FILE)

        # Only commit if there are changes
        if repo.is_dirty(untracked_files=True):
            repo.index.commit(commit_message)

            origin = repo.remote(name="origin")
            origin.push()

        return True

    except Exception as e:
        st.error(f"GitHub sync failed: {e}")
        return False


# -----------------------------
# COLUMN SCHEMA
# -----------------------------
COLUMNS = [
    "Item",
    "Quantity",
    "Freezer Name",
    "Rack Number",
    "Box Number"
]

# -----------------------------
# LOGIN
# -----------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("Inventory Login")

    password = st.text_input("Enter password", type="password")

    if st.button("Login"):
        if password == st.secrets["password"]:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong password")

    st.stop()

# -----------------------------
# LOAD / SAVE
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

    push_to_github(
        f"Inventory update {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


inventory = load_data()

st.title("Inventory Manager")

# -----------------------------
# ADD ITEM
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

        st.success(f"Added {item} and synced to GitHub")
        st.rerun()

# -----------------------------
# SEARCH
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
# UPDATE QUANTITY
# -----------------------------
st.header("Update Quantity")

update_search = st.text_input("Search item to update quantity")

if update_search:
    matches = inventory[
        inventory["Item"].str.contains(update_search, case=False, na=False)
    ].reset_index()

    if len(matches) == 0:
        st.warning("No matching items found.")
    else:
        st.write("Select item to update:")

        options = {
            i: (
                f"{row['Item']} | "
                f"Freezer:{row['Freezer Name']} | "
                f"Rack:{row['Rack Number']} | "
                f"Box:{row['Box Number']} | "
                f"Current Qty:{row['Quantity']}"
            )
            for i, row in matches.iterrows()
        }

        selected = st.selectbox(
            "Matching items",
            list(options.keys()),
            format_func=lambda x: options[x]
        )

        current_qty = int(matches.loc[selected, "Quantity"])

        new_qty = st.number_input(
            "New quantity",
            min_value=0,
            step=1,
            value=current_qty
        )

        if st.button("Update quantity"):
            original_index = matches.loc[selected, "index"]

            inventory.loc[original_index, "Quantity"] = new_qty

            save_data(inventory)

            st.success("Quantity updated and synced to GitHub")
            st.rerun()

# -----------------------------
# DOWNLOAD CSV
# -----------------------------
csv = inventory.to_csv(index=False)

st.download_button(
    "Download CSV",
    csv,
    "inventory.csv",
    "text/csv"
)
