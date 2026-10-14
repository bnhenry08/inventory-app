import streamlit as st
import pandas as pd
import requests
import base64
from io import StringIO

# -----------------------------
# CONFIGURATION
# -----------------------------

ENZYME_COLUMNS = [
    "Enzyme Name",
    "Freezer Name",
    "Rack Number",
    "Box Number",
    "Time Saver",
    "Temperature",
    "Buffer for 100% Activity",
    "Dilute Before Use",
    "Notes"
]

FREEZER_NAME = "Pig 150"
RACK_NUMBER = "11"
BOX_NUMBER = "1"

YES_NO = ["Y", "N"]

TEMPERATURES = [
    "25°C",
    "37°C",
    "50°C",
    "55°C",
    "60°C",
    "65°C",
    "75°C"
]

BUFFER_OPTIONS = [
    "NEBuffer r3.1",
    "rCutSmart™ Buffer",
    "Different Buffer"
]


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
        "https://api.github.com/repos/"
        f"{st.secrets['github_repo']}/contents/"
        f"{st.secrets['restriction_enzymes_file']}"
    )


def load_enzymes():
    """Load the dedicated restriction enzyme CSV from GitHub."""

    response = requests.get(
        github_url(),
        headers=github_headers(),
        timeout=30
    )

    if response.status_code == 404:
        # File does not exist yet; start with an empty inventory.
        return pd.DataFrame(columns=ENZYME_COLUMNS), None

    if response.status_code != 200:
        st.error(
            "Could not load restriction enzyme inventory from GitHub. "
            f"HTTP {response.status_code}: {response.text}"
        )
        return None, None

    data = response.json()

    try:
        csv_content = base64.b64decode(
            data["content"]
        ).decode("utf-8")

        if csv_content.strip():
            df = pd.read_csv(StringIO(csv_content))
        else:
            df = pd.DataFrame(columns=ENZYME_COLUMNS)

    except Exception as exc:
        st.error(f"Could not read the enzyme CSV: {exc}")
        return None, None

    # Add any missing columns without discarding existing data.
    for column in ENZYME_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[ENZYME_COLUMNS]

    # Normalize missing values.
    df = df.fillna("")

    for column in ENZYME_COLUMNS:
        df[column] = df[column].astype(str)

    return df, data["sha"]


def save_enzymes(df, sha):
    """Save the enzyme inventory to its dedicated GitHub CSV."""

    csv_content = df[ENZYME_COLUMNS].to_csv(index=False)

    encoded_content = base64.b64encode(
        csv_content.encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": (
            "Update restriction enzyme inventory "
            f"{pd.Timestamp.now()}"
        ),
        "content": encoded_content
    }

    # GitHub requires the current SHA when updating an existing file.
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

    st.error(
        "Could not save restriction enzyme inventory to GitHub. "
        f"HTTP {response.status_code}: {response.text}"
    )

    return None


# -----------------------------
# LOGIN
# -----------------------------

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:

    st.title("🧬 Restriction Enzyme Inventory")

    with st.form("restriction_enzyme_login"):

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

st.title("🧬 Restriction Enzyme Inventory")

st.info(
    "Storage location for all enzymes: "
    "**Pig 150 → Rack 11 → Box 1**"
)

inventory, github_sha = load_enzymes()

if inventory is None:
    st.warning(
        "The enzyme inventory could not be loaded. "
        "No changes can be made until the loading problem is fixed."
    )
    st.stop()


# -----------------------------
# ADD RESTRICTION ENZYME
# -----------------------------

st.header("➕ Add Restriction Enzyme")

with st.form("add_restriction_enzyme_form"):

    enzyme_name = st.text_input(
        "Enzyme Name",
        placeholder="e.g., EcoRI, BamHI, HindIII"
    )

    time_saver = st.radio(
        "Time Saver",
        YES_NO,
        horizontal=True,
        index=0
    )

    temperature = st.radio(
        "Temperature",
        TEMPERATURES,
        horizontal=True,
        index=1
    )

    buffer = st.radio(
        "Buffer for 100% Activity",
        BUFFER_OPTIONS,
        horizontal=True,
        index=1
    )

    custom_buffer = ""

    if buffer == "Different Buffer":
        custom_buffer = st.text_input(
            "Specify Buffer",
            placeholder="Enter the buffer name"
        )

    dilute_before_use = st.radio(
        "Dilute Before Use",
        YES_NO,
        horizontal=True,
        index=1
    )

    notes = st.text_area(
        "Notes",
        placeholder="Optional notes",
        height=80
    )

    add_submitted = st.form_submit_button(
        "Add Restriction Enzyme"
    )

    if add_submitted:

        if not enzyme_name.strip():
            st.error("Please enter an enzyme name.")

        elif (
            buffer == "Different Buffer"
            and not custom_buffer.strip()
        ):
            st.error("Please specify the buffer.")

        else:

            final_buffer = (
                custom_buffer.strip()
                if buffer == "Different Buffer"
                else buffer
            )

            new_row = pd.DataFrame(
                [{
                    "Enzyme Name": enzyme_name.strip(),
                    "Freezer Name": FREEZER_NAME,
                    "Rack Number": RACK_NUMBER,
                    "Box Number": BOX_NUMBER,
                    "Time Saver": time_saver,
                    "Temperature": temperature,
                    "Buffer for 100% Activity": final_buffer,
                    "Dilute Before Use": dilute_before_use,
                    "Notes": notes.strip()
                }],
                columns=ENZYME_COLUMNS
            )

            updated_inventory = pd.concat(
                [inventory, new_row],
                ignore_index=True
            )

            new_sha = save_enzymes(
                updated_inventory,
                github_sha
            )

            if new_sha is not None:
                st.success(
                    f"{enzyme_name.strip()} saved to "
                    "restriction_enzymes.csv."
                )
                st.rerun()


# -----------------------------
# VIEW AND SEARCH ENZYMES
# -----------------------------

st.divider()
st.header("📋 Restriction Enzyme Inventory")

search = st.text_input(
    "Search enzyme name, buffer, temperature, or notes",
    key="enzyme_search"
)

if search:
    search_mask = inventory.astype(str).apply(
        lambda column: column.str.contains(
            search,
            case=False,
            na=False,
            regex=False
        )
    ).any(axis=1)

    displayed_inventory = inventory.loc[
        search_mask
    ].copy()

else:
    displayed_inventory = inventory.copy()

st.dataframe(
    displayed_inventory,
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Total enzymes registered: {len(inventory)}"
)


# -----------------------------
# UPDATE RESTRICTION ENZYME
# -----------------------------

st.divider()
st.header("✏️ Update Restriction Enzyme")

if inventory.empty:

    st.info("Add an enzyme before trying to update one.")

else:

    enzyme_options = {
        i: (
            f"{row['Enzyme Name']} | "
            f"{row['Temperature']} | "
            f"{row['Buffer for 100% Activity']}"
        )
        for i, row in inventory.iterrows()
    }

    selected_index = st.selectbox(
        "Select enzyme to update",
        list(enzyme_options.keys()),
        format_func=lambda i: enzyme_options[i],
        key="selected_enzyme_update"
    )

    current = inventory.loc[selected_index]

    with st.form("update_restriction_enzyme_form"):

        updated_name = st.text_input(
            "Enzyme Name",
            value=str(current["Enzyme Name"])
        )

        current_time_saver = str(current["Time Saver"])

        updated_time_saver = st.radio(
            "Time Saver",
            YES_NO,
            index=(
                YES_NO.index(current_time_saver)
                if current_time_saver in YES_NO
                else 0
            ),
            horizontal=True
        )

        current_temperature = str(current["Temperature"])

        updated_temperature = st.radio(
            "Temperature",
            TEMPERATURES,
            index=(
                TEMPERATURES.index(current_temperature)
                if current_temperature in TEMPERATURES
                else 1
            ),
            horizontal=True
        )

        current_buffer = str(
            current["Buffer for 100% Activity"]
        )

        if current_buffer in BUFFER_OPTIONS:
            buffer_index = BUFFER_OPTIONS.index(current_buffer)
            current_custom_buffer = ""
        elif current_buffer:
            buffer_index = BUFFER_OPTIONS.index("Different Buffer")
            current_custom_buffer = current_buffer
        else:
            buffer_index = 1
            current_custom_buffer = ""

        updated_buffer = st.radio(
            "Buffer for 100% Activity",
            BUFFER_OPTIONS,
            index=buffer_index,
            horizontal=True
        )

        updated_custom_buffer = ""

        if updated_buffer == "Different Buffer":
            updated_custom_buffer = st.text_input(
                "Specify Buffer",
                value=current_custom_buffer
            )

        current_dilute = str(current["Dilute Before Use"])

        updated_dilute = st.radio(
            "Dilute Before Use",
            YES_NO,
            index=(
                YES_NO.index(current_dilute)
                if current_dilute in YES_NO
                else 1
            ),
            horizontal=True
        )

        updated_notes = st.text_area(
            "Notes",
            value=str(current["Notes"])
        )

        update_submitted = st.form_submit_button(
            "Save Enzyme Updates"
        )

        if update_submitted:

            if not updated_name.strip():
                st.error("Please enter an enzyme name.")

            elif (
                updated_buffer == "Different Buffer"
                and not updated_custom_buffer.strip()
            ):
                st.error("Please specify the buffer.")

            else:

                final_buffer = (
                    updated_custom_buffer.strip()
                    if updated_buffer == "Different Buffer"
                    else updated_buffer
                )

                inventory.loc[
                    selected_index, "Enzyme Name"
                ] = updated_name.strip()

                inventory.loc[
                    selected_index, "Freezer Name"
                ] = FREEZER_NAME

                inventory.loc[
                    selected_index, "Rack Number"
                ] = RACK_NUMBER

                inventory.loc[
                    selected_index, "Box Number"
                ] = BOX_NUMBER

                inventory.loc[
                    selected_index, "Time Saver"
                ] = updated_time_saver

                inventory.loc[
                    selected_index, "Temperature"
                ] = updated_temperature

                inventory.loc[
                    selected_index, "Buffer for 100% Activity"
                ] = final_buffer

                inventory.loc[
                    selected_index, "Dilute Before Use"
                ] = updated_dilute

                inventory.loc[
                    selected_index, "Notes"
                ] = updated_notes.strip()

                new_sha = save_enzymes(
                    inventory,
                    github_sha
                )

                if new_sha is not None:
                    st.success("Enzyme updates saved to GitHub.")
                    st.rerun()


# -----------------------------
# DELETE RESTRICTION ENZYME
# -----------------------------

st.divider()
st.header("❌ Delete Restriction Enzyme")

if inventory.empty:

    st.info("There are no enzymes to delete.")

else:

    delete_options = {
        i: (
            f"{row['Enzyme Name']} | "
            f"{row['Temperature']} | "
            f"{row['Buffer for 100% Activity']}"
        )
        for i, row in inventory.iterrows()
    }

    selected_delete = st.selectbox(
        "Select enzyme to delete",
        list(delete_options.keys()),
        format_func=lambda i: delete_options[i],
        key="selected_enzyme_delete"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this enzyme.",
        key="confirm_enzyme_delete"
    )

    if st.button(
        "Delete Enzyme",
        key="delete_restriction_enzyme"
    ):

        if not confirm_delete:
            st.warning("Please confirm deletion first.")

        else:

            updated_inventory = inventory.drop(
                index=selected_delete
            ).reset_index(drop=True)

            new_sha = save_enzymes(
                updated_inventory,
                github_sha
            )

            if new_sha is not None:
                st.success("Enzyme deleted from GitHub.")
                st.rerun()

