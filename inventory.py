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
        headers=github_headers()
    )

    if response.status_code == 404:
        return pd.DataFrame(columns=COLUMNS), None

    if response.status_code != 200:
        st.error(
            f"GitHub load failed: {response.text}"
        )
        return pd.DataFrame(columns=COLUMNS), None

    data = response.json()

    csv_content = base64.b64decode(
        data["content"]
    ).decode("utf-8")


    # Handle empty GitHub CSV
    if not csv_content.strip():
        return pd.DataFrame(columns=COLUMNS), data["sha"]


    df = pd.read_csv(
        StringIO(csv_content)
    )


    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""


    return df[COLUMNS], data["sha"]

def save_to_github(df, sha):

    csv_content = df.to_csv(
        index=False
    )

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
        json=payload
    )

    if response.status_code in [200, 201]:
        return response.json()["content"]["sha"]

    st.error(
        f"GitHub update failed: {response.text}"
    )

    return sha



# -----------------------------
# LOGIN
# -----------------------------

if "auth" not in st.session_state:
    st.session_state.auth = False


if not st.session_state.auth:

    st.title("Inventory Login")

    password = st.text_input(
        "Enter password",
        type="password"
    )

    if st.button("Login"):

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


st.title("Inventory Manager")



# -----------------------------
# ADD ITEM
# -----------------------------

st.header("Add Item")


with st.form("add_item"):

    box_name = st.text_input(
        "Box Name"
    )

    item = st.text_input(
        "Item Name"
    )

    quantity = st.number_input(
        "Quantity",
        min_value=0,
        step=1
    )

    freezer_name = st.radio(
        "Freezer Name",
        ["Pig 150", "B", "C", "D", "E"],
        horizontal=True
    )

    rack_number = st.radio(
        "Rack Number",
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        horizontal=True
    )

    box_number = st.radio(
        "Box Number",
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        horizontal=True
    ),

    notes = st.text_area(
        "Box Notes",
        placeholder="Enter notes for this box..."
    )


    submitted = st.form_submit_button(
        "Add"
    )


    if submitted and item:

        new_row = pd.DataFrame(
            [[
                box_name,
                item,
                quantity,
                freezer_name,
                rack_number,
                box_number,
                notes
            ]],
            columns=COLUMNS
        )


        inventory = pd.concat(
            [
                inventory,
                new_row
            ],
            ignore_index=True
        )


        github_sha = save_to_github(
            inventory,
            github_sha
        )


        st.success(
            f"{item} added and saved to GitHub"
        )

        st.rerun()

# -----------------------------
# SEARCH
# -----------------------------

st.header("Search")


search = st.text_input(
    "Search items"
)


if search:

    filtered = inventory[
        inventory.astype(str).apply(
            lambda row:
            row.str.contains(
                search,
                case=False,
                na=False
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

st.header("Update Item Information")


update_search = st.text_input(
    "Search item to update"
)


if update_search:

    matches = inventory[
        inventory["Item"].str.contains(
            update_search,
            case=False,
            na=False
        )
    ].reset_index()


    if len(matches) == 0:

        st.warning(
            "No matching items found."
        )


    else:

        options = {
            i:
            (
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
            format_func=lambda x: options[x]
        )


        index = matches.loc[
            selected,
            "index"
        ]


        # Current values
        current = inventory.loc[index]

        new_notes = st.text_area(
            "Box Notes",
            value=str(current["Notes"])
        )
        new_quantity = st.number_input(
            "Quantity",
            min_value=0,
            step=1,
            value=int(current["Quantity"])
        )


        new_freezer = st.radio(
            "Freezer Name",
            ["Pig 150", "B", "C", "D", "E"],
            index=[
                "Pig 150", "B", "C", "D", "E"
            ].index(current["Freezer Name"])
            if current["Freezer Name"] in ["Pig 150", "B", "C", "D", "E"]
            else 0,
            horizontal=True
        )


        new_rack = st.radio(
            "Rack Number",
            [
                "1", "2", "3", "4", "5", "6",
                "7", "8", "9", "10", "11", "12"
            ],
            index=[
                "1", "2", "3", "4", "5", "6",
                "7", "8", "9", "10", "11", "12"
            ].index(str(current["Rack Number"]))
            if str(current["Rack Number"]) in [
                "1", "2", "3", "4", "5", "6",
                "7", "8", "9", "10", "11", "12"
            ]
            else 0,
            horizontal=True
        )


        new_box = st.radio(
            "Box Number",
            [
                "1", "2", "3", "4", "5", "6",
                "7", "8", "9", "10", "11", "12"
            ],
            index=[
                "1", "2", "3", "4", "5", "6",
                "7", "8", "9", "10", "11", "12"
            ].index(str(current["Box Number"]))
            if str(current["Box Number"]) in [
                "1", "2", "3", "4", "5", "6",
                "7", "8", "9", "10", "11", "12"
            ]
            else 0,
            horizontal=True
        )
        new_notes = st.text_area(
                "Notes",
        value=str(current["Notes"])
        if "Notes" in current
        else ""
        )

        if st.button("Save Updates"):

            inventory.loc[index, "Quantity"] = new_quantity
            inventory.loc[index, "Freezer Name"] = new_freezer
            inventory.loc[index, "Rack Number"] = new_rack
            inventory.loc[index, "Box Number"] = new_box
            inventory.loc[index, "Notes"] = new_notes

    # Update Notes for the entire box
    same_box = (
        (inventory["Box Name"] == current["Box Name"]) &
        (inventory["Freezer Name"] == current["Freezer Name"]) &
        (inventory["Rack Number"] == current["Rack Number"]) &
        (inventory["Box Number"] == current["Box Number"])
    )


    inventory.loc[
        same_box,
        "Notes"
    ] = new_notes
        if st.button("Save Updates"):

            inventory.loc[index, "Quantity"] = new_quantity
            inventory.loc[index, "Freezer Name"] = new_freezer
            inventory.loc[index, "Rack Number"] = new_rack
            inventory.loc[index, "Box Number"] = new_box


            github_sha = save_to_github(
                inventory,
                github_sha
            )


            st.success(
                "Item information updated and saved to GitHub"
            )

            st.rerun()


# -----------------------------
# DOWNLOAD
# -----------------------------

csv = inventory.to_csv(
    index=False
)


st.download_button(
    "Download CSV",
    csv,
    "inventory.csv",
    "text/csv"
)

# -----------------------------
# DELETE ITEM
# -----------------------------

st.header("Delete Item")


delete_search = st.text_input(
    "Search item to delete"
)


if delete_search:

    delete_matches = inventory[
        inventory["Item"].str.contains(
            delete_search,
            case=False,
            na=False
        )
    ].reset_index()


    if len(delete_matches) == 0:

        st.warning(
            "No matching items found."
        )


    else:

        delete_options = {
            i:
            (
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
            format_func=lambda x: delete_options[x]
        )


        if st.button("Delete Item"):

            index_to_delete = delete_matches.loc[
                selected_delete,
                "index"
            ]


            inventory = inventory.drop(
                index_to_delete
            ).reset_index(
                drop=True
            )


            github_sha = save_to_github(
                inventory,
                github_sha
            )


            st.success(
                "Item deleted and saved to GitHub"
            )

            st.rerun()
