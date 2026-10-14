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

# Buffer options are displayed in this order.
BUFFER_OPTIONS = [
    "rCutSmart™ Buffer",
    "NEBuffer r3.1",
    "NEBuffer r1.1",
    "NEBuffer r2.1"
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
    try:
        response = requests.get(
            github_url(),
            headers=github_headers(),
            timeout=30
        )
    except requests.RequestException as exc:
        st.error(f"Could not connect to GitHub: {exc}")
        return None, None

    if response.status_code == 404:
        return pd.DataFrame(columns=ENZYME_COLUMNS), None

    if response.status_code != 200:
        st.error(
            "Could not load the restriction enzyme CSV from GitHub. "
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
        st.error(f"Could not read the restriction enzyme CSV: {exc}")
        return None, None

    for column in ENZYME_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[ENZYME_COLUMNS].fillna("")

    for column in ENZYME_COLUMNS:
        df[column] = df[column].astype(str)

    return df, data["sha"]


def save_enzymes(df, sha):
    csv_content = df[ENZYME_COLUMNS].to_csv(index=False)

    encoded_content = base64.b64encode(
        csv_content.encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": (
            f"Update restriction enzyme inventory "
            f"{pd.Timestamp.now()}"
        ),
        "content": encoded_content
    }

    if sha:
        payload["sha"] = sha

    try:
        response = requests.put(
            github_url(),
            headers=github_headers(),
            json=payload,
            timeout=30
        )
    except requests.RequestException as exc:
        st.error(f"Could not connect to GitHub to save changes: {exc}")
        return None

    if response.status_code in [200, 201]:
        return response.json()["content"]["sha"]

    st.error(
        "Could not save the restriction enzyme CSV to GitHub. "
        f"HTTP {response.status_code}: {response.text}"
    )

    return None


# -----------------------------
# BUFFER SELECTION
# -----------------------------

def buffer_checkboxes(prefix, selected_buffers=None):
    """
    Display buffer checkboxes in the configured order.
    Return all selected buffers as a comma-separated string.
    """

    if selected_buffers is None:
        selected_buffers = []

    selected_buffers = [b.strip() for b in selected_buffers]

    st.write("**Buffer(s) for 100% Activity**")

    chosen_buffers = []

    for i, buffer_name in enumerate(BUFFER_OPTIONS):
        checked = st.checkbox(
            buffer_name,
            value=buffer_name in selected_buffers,
            key=f"{prefix}_buffer_{i}"
        )

        if checked:
            chosen_buffers.append(buffer_name)

    different_buffer = st.checkbox(
        "Different Buffer",
        value=any(
            b not in BUFFER_OPTIONS and b.strip()
            for b in selected_buffers
        ),
        key=f"{prefix}_different_buffer"
    )

    if different_buffer:
        existing_custom_buffers = [
            b for b in selected_buffers
            if b not in BUFFER_OPTIONS and b.strip()
        ]

        custom_default = ", ".join(existing_custom_buffers)

        custom_buffer_names = st.text_input(
            "Enter other buffer name(s)",
            value=custom_default,
            placeholder="Enter buffer name(s)",
            key=f"{prefix}_custom_buffer_names"
        )

        if custom_buffer_names.strip():
            chosen_buffers.extend(
                b.strip()
                for b in custom_buffer_names.split(",")
                if b.strip()
            )

    return ", ".join(chosen_buffers)


def parse_buffers(buffer_value):
    if not buffer_value or not str(buffer_value).strip():
        return []

    return [
        b.strip()
        for b in str(buffer_value).split(",")
        if b.strip()
    ]


# -----------------------------
# LOGIN
# -----------------------------

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🧬 Inventory Login 🧬")

    with st.form("restriction_enzyme_login_form"):
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

inventory, github_sha = load_enzymes()

if inventory is None:
    st.error(
        "The enzyme inventory could not be loaded. "
        "No changes can be made until the problem is resolved."
    )
    st.stop()


# -----------------------------
# PAGE TITLE
# -----------------------------

st.title("🧬 Restriction Enzymes")

st.caption(
    "Storage location for these enzymes: "
    f"{FREEZER_NAME} | Rack {RACK_NUMBER} | Box {BOX_NUMBER}"
)


# -----------------------------
# ADD ENZYME
# -----------------------------

st.header("➕ Add Restriction Enzyme")

enzyme_name = st.text_input(
    "Enzyme Name",
    placeholder="Enter enzyme name",
    key="add_enzyme_name"
)

time_saver = st.radio(
    "Time Saver",
    YES_NO,
    horizontal=True,
    index=0,
    key="add_time_saver"
)

temperature = st.selectbox(
    "Temperature",
    TEMPERATURES,
    index=TEMPERATURES.index("37°C"),
    key="add_temperature"
)

buffer_value = buffer_checkboxes(
    prefix="add",
    selected_buffers=[]
)

dilute_before_use = st.radio(
    "Dilute Before Use",
    YES_NO,
    horizontal=True,
    index=1,
    key="add_dilute_before_use"
)

notes = st.text_area(
    "Notes",
    placeholder="Enter any additional notes",
    key="add_enzyme_notes"
)

if st.button("Add Enzyme", key="add_enzyme_button"):

    if not enzyme_name.strip():
        st.error("Please enter an enzyme name.")

    elif not buffer_value:
        st.error("Please select at least one buffer.")

    else:
        new_row = pd.DataFrame(
            [[
                enzyme_name.strip(),
                FREEZER_NAME,
                RACK_NUMBER,
                BOX_NUMBER,
                time_saver,
                temperature,
                buffer_value,
                dilute_before_use,
                notes.strip()
            ]],
            columns=ENZYME_COLUMNS
        )

        updated_inventory = pd.concat(
            [inventory, new_row],
            ignore_index=True
        )

        new_sha = save_enzymes(updated_inventory, github_sha)

        if new_sha is not None:
            st.success(
                f"{enzyme_name.strip()} was saved to GitHub."
            )
            st.rerun()


# -----------------------------
# SEARCH AND VIEW ENZYMES
# -----------------------------

st.divider()
st.header("🔍 Search and View Enzymes")

search = st.text_input(
    "Search enzymes",
    key="enzyme_search"
)

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
    use_container_width=True,
    hide_index=True
)


# -----------------------------
# UPDATE ENZYME
# -----------------------------

st.divider()
st.header("✏️ Update Enzyme Information")

if inventory.empty:
    st.info("No enzymes have been added yet.")

else:
    enzyme_options = {
        i: (
            f"{row['Enzyme Name']} | "
            f"Buffers: {row['Buffer for 100% Activity']} | "
            f"Temperature: {row['Temperature']}"
        )
        for i, row in inventory.iterrows()
    }

    selected_index = st.selectbox(
        "Select enzyme to update",
        list(enzyme_options.keys()),
        format_func=lambda x: enzyme_options[x],
        key="update_enzyme_selection"
    )

    current = inventory.loc[selected_index]

    st.write("**Enzyme Name**")

    updated_enzyme_name = st.text_input(
        "Edit enzyme name",
        value=str(current["Enzyme Name"]),
        key=f"edit_enzyme_name_{selected_index}"
    )

    current_time_saver = str(current["Time Saver"])
    time_saver_index = (
        YES_NO.index(current_time_saver)
        if current_time_saver in YES_NO
        else 0
    )

    updated_time_saver = st.radio(
        "Time Saver",
        YES_NO,
        index=time_saver_index,
        horizontal=True,
        key=f"edit_time_saver_{selected_index}"
    )

    current_temperature = str(current["Temperature"])
    temperature_index = (
        TEMPERATURES.index(current_temperature)
        if current_temperature in TEMPERATURES
        else TEMPERATURES.index("37°C")
    )

    updated_temperature = st.selectbox(
        "Temperature",
        TEMPERATURES,
        index=temperature_index,
        key=f"edit_temperature_{selected_index}"
    )

    current_buffers = parse_buffers(
        current["Buffer for 100% Activity"]
    )

    updated_buffer_value = buffer_checkboxes(
        prefix=f"edit_{selected_index}",
        selected_buffers=current_buffers
    )

    current_dilute = str(current["Dilute Before Use"])
    dilute_index = (
        YES_NO.index(current_dilute)
        if current_dilute in YES_NO
        else 1
    )

    updated_dilute = st.radio(
        "Dilute Before Use",
        YES_NO,
        index=dilute_index,
        horizontal=True,
        key=f"edit_dilute_{selected_index}"
    )

    updated_notes = st.text_area(
        "Notes",
        value=str(current["Notes"]),
        key=f"edit_notes_{selected_index}"
    )

    if st.button("Save Enzyme Updates", key="save_enzyme_updates"):

        if not updated_enzyme_name.strip():
            st.error("Please enter an enzyme name.")

        elif not updated_buffer_value:
            st.error("Please select at least one buffer.")

        else:
            updated_inventory = inventory.copy()

            updated_inventory.loc[
                selected_index, "Enzyme Name"
            ] = updated_enzyme_name.strip()

            updated_inventory.loc[
                selected_index, "Time Saver"
            ] = updated_time_saver

            updated_inventory.loc[
                selected_index, "Temperature"
            ] = updated_temperature

            updated_inventory.loc[
                selected_index, "Buffer for 100% Activity"
            ] = updated_buffer_value

            updated_inventory.loc[
                selected_index, "Dilute Before Use"
            ] = updated_dilute

            updated_inventory.loc[
                selected_index, "Notes"
            ] = updated_notes.strip()

            new_sha = save_enzymes(
                updated_inventory,
                github_sha
            )

            if new_sha is not None:
                st.success("Enzyme information updated in GitHub.")
                st.rerun()


# -----------------------------
# DOWNLOAD CSV
# -----------------------------

st.divider()
st.header("⬇️ Download Restriction Enzyme Inventory")

csv_content = inventory.to_csv(index=False)

st.download_button(
    "Download Enzyme CSV",
    data=csv_content,
    file_name="restriction_enzymes.csv",
    mime="text/csv",
    key="download_enzyme_csv"
)


# -----------------------------
# DELETE ENZYME
# -----------------------------

st.divider()
st.header("❌ Delete Enzyme")

if inventory.empty:
    st.info("There are no enzymes to delete.")

else:
    delete_options = {
        i: (
            f"{row['Enzyme Name']} | "
            f"Buffers: {row['Buffer for 100% Activity']} | "
            f"Temperature: {row['Temperature']}"
        )
        for i, row in inventory.iterrows()
    }

    delete_index = st.selectbox(
        "Select enzyme to delete",
        list(delete_options.keys()),
        format_func=lambda x: delete_options[x],
        key="delete_enzyme_selection"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this enzyme.",
        key="confirm_delete_enzyme"
    )

    if st.button("Delete Enzyme", key="delete_enzyme_button"):

        if not confirm_delete:
            st.warning("Please confirm before deleting.")

        else:
            updated_inventory = (
                inventory.drop(index=delete_index)
                .reset_index(drop=True)
            )

            new_sha = save_enzymes(
                updated_inventory,
                github_sha
            )

            if new_sha is not None:
                st.success("Enzyme deleted from GitHub.")
                st.rerun()
