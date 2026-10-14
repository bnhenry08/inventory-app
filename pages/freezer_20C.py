
import streamlit as st
import pandas as pd
import requests
import base64
from io import StringIO

COLUMNS = [
    "Box Name",
    "Item",
    "Quantity",
    "Freezer Name",
    "Rack Number",
    "Box Number",
    "Notes"
]

BOX_NAMES = [
    "Antibiotics [Puromycin, Kanamycin, Carbenicillin]",
    "Antibiotics [Hygromycin, Tetracyclin]",
    "Xgal, IPTG Aliquotes [Blue/White Screening]",
    "dNTP",
    "Western Blot",
    "DNase, Pro.K, Phosphotase, RNase, PUREExpress, Capping",
    "1KB+ DNA Ladder Aliquotes",
    "T4 Ligase, Monarch Carrier RNA",
    "PCR MM Aliquot, Cloning MM Aliquots", 
    "Restriction Enzymes"
]

FREEZER_NAMES = [
    "Pig 150",
    "Rabbit 150",
    "Frog 144",
    "Lobster 144"
]

RACK_NUMBERS = [str(i) for i in range(1, 13)]
BOX_NUMBERS = [str(i) for i in range(1, 10)]


# -----------------------------
# GITHUB FUNCTIONS
# -----------------------------

def github_headers():
    return {
        "Authorization": f"token {st.secrets['github_token']}",
        "Accept": "application/vnd.github+json"
    }


def github_url():
    return (
        f"https://api.github.com/repos/"
        f"{st.secrets['github_repo']}/contents/"
        f"{st.secrets['github_file']}"
    )


def load_from_github():
    response = requests.get(
        github_url(),
        headers=github_headers(),
        timeout=30
    )

    if response.status_code == 404:
        return pd.DataFrame(columns=COLUMNS), None

    if response.status_code != 200:
        st.error(f"GitHub load failed: {response.text}")
        return pd.DataFrame(columns=COLUMNS), None

    data = response.json()

    csv_content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    if not csv_content.strip():
        return pd.DataFrame(columns=COLUMNS), data["sha"]

    df = pd.read_csv(StringIO(csv_content))

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df["Freezer Name"] = df["Freezer Name"].fillna("").astype(str)
    df["Rack Number"] = df["Rack Number"].fillna("").astype(str)
    df["Box Number"] = df["Box Number"].fillna("").astype(str)
    df["Notes"] = df["Notes"].fillna("").astype(str)

    return df[COLUMNS], data["sha"]


def save_to_github(df, sha):
    csv_content = df.to_csv(index=False)

    encoded = base64.b64encode(
        csv_content.encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": f"Inventory update {pd.Timestamp.now()}",
        "content": encoded
    }

    if sha:
        payload["sha"] = sha

    response = requests.put(
        github_url(),
        headers=github_headers(),
        json=payload,
        timeout=30
    )

    if response.status_code in [200, 201]:
        return response.json()["content"]["sha"]

    st.error(f"GitHub update failed: {response.text}")
    return sha


# -----------------------------
# LOGIN
# -----------------------------

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:

    st.title("🧬 Inventory Login 🧬")

    with st.form("login_form"):
        password = st.text_input(
            "Enter password",
            type="password"
        )

        login_submitted = st.form_submit_button("Login")

        if login_submitted:
            if password == st.secrets["password"]:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Wrong password")

    st.stop()


# -----------------------------
# LOAD INVENTORY
# -----------------------------

inventory, github_sha = load_from_github()

st.title("❄️ -20°C Freezer Inventory ❄️")


# -----------------------------
# ADD ITEM TO EXISTING BOX
# -----------------------------

st.header("➕ Add Item to Existing Box")

with st.form("add_existing_box_form"):

    # 1. Box Name
    box_name = st.radio(
        "Box Name",
        BOX_NAMES,
        horizontal=True,
        key="existing_box_name"
    )

    # 2. Freezer Name
    freezer_name = st.radio(
        "Freezer Name",
        FREEZER_NAMES,
        horizontal=True,
        key="existing_freezer_name"
    )

    # 3. Rack Number
    rack_number = st.radio(
        "Rack Number",
        RACK_NUMBERS,
        horizontal=True,
        key="existing_rack_number"
    )

    # 4. Box Number
    box_number = st.radio(
        "Box Number",
        BOX_NUMBERS,
        horizontal=True,
        key="existing_box_number"
    )

    # 5. Item Name and Quantity on the same row
    item_col, quantity_col = st.columns([3, 1])

    with item_col:
        item = st.text_input(
            "Item Name",
            placeholder="Enter item name",
            key="existing_item_name"
        )

    with quantity_col:
        quantity = st.number_input(
            "Quantity",
            min_value=0,
            step=1,
            key="existing_quantity"
        )

    # 6. Notes
    notes = st.text_area(
        "Box Notes",
        placeholder="Enter notes for this box...",
        height=80,
        key="existing_box_notes"
    )

    existing_submitted = st.form_submit_button("Add")

    if existing_submitted:

        if not item.strip():
            st.error("Please enter an item name.")

        else:
            new_row = pd.DataFrame(
                [[
                    box_name,
                    item.strip(),
                    quantity,
                    freezer_name,
                    rack_number,
                    box_number,
                    notes
                ]],
                columns=COLUMNS
            )

            updated_inventory = pd.concat(
                [inventory, new_row],
                ignore_index=True
            )

            new_sha = save_to_github(
                updated_inventory,
                github_sha
            )

            if new_sha != github_sha or github_sha is not None:
                inventory = updated_inventory
                github_sha = new_sha
                st.success(
                    f"{item.strip()} added and saved to GitHub."
                )
                st.rerun()


# -----------------------------
# ADD NEW BOX
# -----------------------------

st.header("➕ New Box")

with st.form("add_new_box_form"):

    # 1. Box Name
    new_box_name = st.text_input(
        "Box Name",
        placeholder="Enter a new box name",
        key="new_box_name"
    )

    # 2. Freezer Name
    new_freezer_name = st.radio(
        "Freezer Name",
        FREEZER_NAMES,
        horizontal=True,
        key="new_freezer_name"
    )

    # 3. Rack Number
    new_rack_number = st.radio(
        "Rack Number",
        RACK_NUMBERS,
        horizontal=True,
        key="new_rack_number"
    )

    # 4. Box Number
    new_box_number = st.radio(
        "Box Number",
        BOX_NUMBERS,
        horizontal=True,
        key="new_box_number"
    )

    # 5. Item Name and Quantity on the same row
    new_item_col, new_quantity_col = st.columns([3, 1])

    with new_item_col:
        new_item = st.text_input(
            "Item Name",
            placeholder="Enter item name",
            key="new_item_name"
        )

    with new_quantity_col:
        new_quantity = st.number_input(
            "Quantity",
            min_value=0,
            step=1,
            key="new_item_quantity"
        )

    # 6. Notes
    new_notes = st.text_area(
        "Box Notes",
        placeholder="Enter notes for this box...",
        height=80,
        key="new_box_notes"
    )

    new_box_submitted = st.form_submit_button("Add")

    if new_box_submitted:

        if not new_box_name.strip():
            st.error("Please enter a box name.")

        elif not new_item.strip():
            st.error("Please enter an item name.")

        else:
            new_row = pd.DataFrame(
                [[
                    new_box_name.strip(),
                    new_item.strip(),
                    new_quantity,
                    new_freezer_name,
                    new_rack_number,
                    new_box_number,
                    new_notes
                ]],
                columns=COLUMNS
            )

            updated_inventory = pd.concat(
                [inventory, new_row],
                ignore_index=True
            )

            new_sha = save_to_github(
                updated_inventory,
                github_sha
            )

            if new_sha != github_sha or github_sha is not None:
                inventory = updated_inventory
                github_sha = new_sha
                st.success(
                    f"New box '{new_box_name.strip()}' and item "
                    f"'{new_item.strip()}' saved to GitHub."
                )
                st.rerun()


# -----------------------------
# SEARCH
# -----------------------------

st.header("🔍 Search")

search = st.text_input("Search items", key="inventory_search")

if search:
    filtered = inventory[
        inventory.astype(str).apply(
            lambda row: row.str.contains(
                search,
                case=False,
                na=False,
                regex=False
            ).any(),
            axis=1
        )
    ]
else:
    filtered = inventory

st.dataframe(
    filtered,
    use_container_width=True
)


# -----------------------------
# UPDATE ITEM INFORMATION
# -----------------------------

st.header("✏️ Update Item Information")

update_search = st.text_input(
    "Search item to update",
    key="update_search"
)

if update_search:

    matches = inventory[
        inventory["Item"].astype(str).str.contains(
            update_search,
            case=False,
            na=False,
            regex=False
        )
    ].reset_index()

    if len(matches) == 0:
        st.warning("No matching items found.")

    else:
        options = {
            i: (
                f"{row['Box Name']} | "
                f"{row['Item']} | "
                f"Freezer:{row['Freezer Name']} | "
                f"Rack:{row['Rack Number']} | "
                f"Box:{row['Box Number']} | "
                f"Qty:{row['Quantity']} | "
                f"Notes:{row['Notes']}"
            )
            for i, row in matches.iterrows()
        }

        selected = st.selectbox(
            "Select item to update",
            list(options.keys()),
            format_func=lambda x: options[x],
            key="update_item_selection"
        )

        index = matches.loc[selected, "index"]
        current = inventory.loc[index]

        # Box Name options
        box_name_options = [
            "Antibiotics [Puromycin, Kanamycin, Carbenicillin]",
            "Antibiotics [Hygromycin, Tetracyclin]",
            "Xgal, IPTG Aliquotes [Blue/White Screening]",
            "dNTP",
            "Western Blot",
            "DNase, Pro.K, Phosphotase, RNase, PUREExpress, Capping",
            "1KB+ DNA Ladder Aliquotes",
            "T4 Ligase, Monarch Carrier RNA",
            "PCR MM Aliquot, Cloning MM Aliquots"
        ]

        new_box_name = st.radio(
            "Box Name",
            box_name_options,
            index=(
                box_name_options.index(current["Box Name"])
                if current["Box Name"] in box_name_options
                else 0
            ),
            horizontal=True,
            key="update_box_name"
        )

        new_notes = st.text_area(
            "Box Notes",
            value=str(current["Notes"]),
            key="update_notes"
        )

        current_quantity = pd.to_numeric(
            current["Quantity"],
            errors="coerce"
        )

        if pd.isna(current_quantity):
            current_quantity = 0

        new_quantity = st.number_input(
            "Quantity",
            min_value=0,
            step=1,
            value=int(current_quantity),
            key="update_quantity"
        )

        current_freezer = str(current["Freezer Name"])
        freezer_index = (
            FREEZER_NAMES.index(current_freezer)
            if current_freezer in FREEZER_NAMES
            else 0
        )

        new_freezer = st.radio(
            "Freezer Name",
            FREEZER_NAMES,
            index=freezer_index,
            horizontal=True,
            key="update_freezer"
        )

        current_rack = str(current["Rack Number"])
        rack_index = (
            RACK_NUMBERS.index(current_rack)
            if current_rack in RACK_NUMBERS
            else 0
        )

        new_rack = st.radio(
            "Rack Number",
            RACK_NUMBERS,
            index=rack_index,
            horizontal=True,
            key="update_rack"
        )

        current_box = str(current["Box Number"])
        box_index = (
            BOX_NUMBERS.index(current_box)
            if current_box in BOX_NUMBERS
            else 0
        )

        new_box = st.radio(
            "Box Number",
            BOX_NUMBERS,
            index=box_index,
            horizontal=True,
            key="update_box"
        )

        if st.button("Save Updates"):

            old_box_name = current["Box Name"]

            inventory.loc[index, "Box Name"] = new_box_name
            inventory.loc[index, "Quantity"] = new_quantity
            inventory.loc[index, "Freezer Name"] = new_freezer
            inventory.loc[index, "Rack Number"] = str(new_rack)
            inventory.loc[index, "Box Number"] = str(new_box)

            # Update notes for all items in the same box.
            same_box = (
            (inventory["Box Name"] == current["Box Name"]) &
            (inventory["Freezer Name"] == new_freezer) &
            (inventory["Rack Number"] == str(new_rack)) &
            (inventory["Box Number"] == str(new_box))
            )

            inventory.loc[same_box, "Notes"] = str(new_notes)

            new_sha = save_to_github(
                inventory,
                github_sha
            )

            if new_sha != github_sha or github_sha is not None:
                github_sha = new_sha
                st.success(
                    "Item information updated and saved to GitHub."
                )
                st.rerun()


# -----------------------------
# DOWNLOAD
# -----------------------------

st.header("⬇️ Download Inventory")

csv = inventory.to_csv(index=False)

st.download_button(
    "Download CSV",
    csv,
    "inventory.csv",
    "text/csv",
    key="download_inventory"
)


# -----------------------------
# DELETE ITEM
# -----------------------------

st.header("❌ Delete Item")

delete_search = st.text_input(
    "Search item to delete",
    key="delete_search"
)

if delete_search:

    delete_matches = inventory[
        inventory["Item"].astype(str).str.contains(
            delete_search,
            case=False,
            na=False,
            regex=False
        )
    ].reset_index()

    if len(delete_matches) == 0:
        st.warning("No matching items found.")

    else:
        delete_options = {
            i: (
                f"{row['Item']} | "
                f"Freezer:{row['Freezer Name']} | "
                f"Rack:{row['Rack Number']} | "
                f"Box:{row['Box Number']} | "
                f"Qty:{row['Quantity']} | "
                f"Notes:{row['Notes']}"
            )
            for i, row in delete_matches.iterrows()
        }

        selected_delete = st.selectbox(
            "Select item to delete",
            list(delete_options.keys()),
            format_func=lambda x: delete_options[x],
            key="delete_item_selection"
        )

        if st.button("Delete Item", key="delete_item_button"):

            index_to_delete = delete_matches.loc[
                selected_delete,
                "index"
            ]

            updated_inventory = inventory.drop(
                index_to_delete
            ).reset_index(drop=True)

            new_sha = save_to_github(
                updated_inventory,
                github_sha
            )

            if new_sha != github_sha or github_sha is not None:
                inventory = updated_inventory
                github_sha = new_sha
                st.success("Item deleted and saved to GitHub.")
                st.rerun()
