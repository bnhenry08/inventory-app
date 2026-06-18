import streamlit as st
import pandas as pd
import requests
import base64
from io import StringIO

COLUMNS = [
    "Item",
    "Quantity",
    "Freezer Name",
    "Rack Number",
    "Box Number"
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

    item = st.text_input(
        "Item Name"
    )

    quantity = st.number_input(
        "Quantity",
        min_value=0,
        step=1
    )

    freezer_name = st.text_input(
        "Freezer Name"
    )

    rack_number = st.text_input(
        "Rack Number"
    )

    box_number = st.text_input(
        "Box Number"
    )


    submitted = st.form_submit_button(
        "Add"
    )


    if submitted and item:

        new_row = pd.DataFrame(
            [[
                item,
                quantity,
                freezer_name,
                rack_number,
                box_number
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
# UPDATE QUANTITY
# -----------------------------

st.header("Update Quantity")


update_search = st.text_input(
    "Search item to update quantity"
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
                f"{row['Item']} | "
                f"Freezer:{row['Freezer Name']} | "
                f"Rack:{row['Rack Number']} | "
                f"Box:{row['Box Number']} | "
                f"Qty:{row['Quantity']}"
            )

            for i, row in matches.iterrows()
        }


        selected = st.selectbox(
            "Matching items",
            list(options.keys()),
            format_func=lambda x: options[x]
        )


        new_qty = st.number_input(
            "New quantity",
            min_value=0,
            step=1,
            value=int(
                matches.loc[selected, "Quantity"]
            )
        )


        if st.button(
            "Update quantity"
        ):

            index = matches.loc[
                selected,
                "index"
            ]


            inventory.loc[
                index,
                "Quantity"
            ] = new_qty


            github_sha = save_to_github(
                inventory,
                github_sha
            )


            st.success(
                "Quantity updated and saved to GitHub"
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
