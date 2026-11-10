import base64
from io import StringIO

import pandas as pd
import requests
import streamlit as st

# -----------------------------
# CONFIGURATION
# -----------------------------

ENZYME_COLUMNS = [
    "Enzyme Name",
    "Temperature",
    "Buffer for 100% Activity",
    "Time Saver",
    "Dilute Before Use",
    "Freezer Name",
    "Rack Number",
    "Box Number",
    "Notes",
]

FREEZER_NAME = "Pig 150"
RACK_NUMBER = "11"
BOX_NUMBER = "1"
YES_NO = ["Y", "N"]
TEMPERATURES = ["25°C", "37°C", "50°C", "55°C", "60°C", "65°C", "75°C"]
BUFFER_OPTIONS = [
    "rCutSmart™ Buffer",
    "NEBuffer r3.1",
    "NEBuffer r1.1",
    "NEBuffer r2.1",
]


# -----------------------------
# GITHUB FUNCTIONS
# -----------------------------

def github_headers():
    return {
        "Authorization": f"token {st.secrets['github_token']}",
        "Accept": "application/vnd.github+json",
    }


def github_url():
    return (
        "https://api.github.com/repos/"
        f"{st.secrets['github_repo']}/contents/"
        f"{st.secrets['restriction_enzymes_file']}"
    )


def load_enzymes():
    try:
        response = requests.get(github_url(), headers=github_headers(), timeout=30)
    except requests.RequestException as exc:
        st.error(f"Could not connect to GitHub: {exc}")
        return None, None

    if response.status_code == 404:
        return pd.DataFrame(columns=ENZYME_COLUMNS), None

    if response.status_code != 200:
        st.error(
            "Could not load the restriction enzyme inventory from GitHub. "
            f"HTTP {response.status_code}: {response.text}"
        )
        return None, None

    try:
        data = response.json()
        csv_content = base64.b64decode(data["content"]).decode("utf-8")
        df = (
            pd.read_csv(StringIO(csv_content))
            if csv_content.strip()
            else pd.DataFrame(columns=ENZYME_COLUMNS)
        )
    except Exception as exc:
        st.error(f"Could not read the enzyme CSV: {exc}")
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
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"Update restriction enzyme inventory {pd.Timestamp.now()}",
        "content": encoded_content,
    }
    if sha:
        payload["sha"] = sha

    try:
        response = requests.put(
            github_url(),
            headers=github_headers(),
            json=payload,
            timeout=30,
        )
    except requests.RequestException as exc:
        st.error(f"Could not connect to GitHub to save changes: {exc}")
        return None

    if response.status_code in (200, 201):
        return response.json()["content"]["sha"]

    st.error(
        "Could not save the enzyme inventory to GitHub. "
        f"HTTP {response.status_code}: {response.text}"
    )
    return None


# -----------------------------
# BUFFER CHECKBOXES
# -----------------------------

def buffer_checkboxes(prefix, selected_buffers=None):
    selected_buffers = selected_buffers or []
    selected_buffers = [value.strip() for value in selected_buffers if value.strip()]
    st.write("**Buffer(s) for 100% Activity**")
    chosen_buffers = []
    for i, buffer_name in enumerate(BUFFER_OPTIONS):
        if st.checkbox(
            buffer_name,
            value=buffer_name in selected_buffers,
            key=f"{prefix}_buffer_{i}",
        ):
            chosen_buffers.append(buffer_name)
    return ", ".join(chosen_buffers)


def parse_buffers(buffer_value):
    if not buffer_value or not str(buffer_value).strip():
        return []
    return [value.strip() for value in str(buffer_value).split(",") if value.strip()]


# -----------------------------
# LOGIN
# -----------------------------

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🧬 Inventory Login")
    with st.form("restriction_enzyme_login_form"):
        password = st.text_input("Enter password", type="password")
        login_submitted = st.form_submit_button("Login", use_container_width=True)
        if login_submitted:
            if password == st.secrets["password"]:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Wrong password")
    st.stop()


# -----------------------------
# LOAD INVENTORY AND PAGE TITLE
# -----------------------------

inventory, github_sha = load_enzymes()
if inventory is None:
    st.error("The enzyme inventory could not be loaded. No changes can be made until the problem is resolved.")
    st.stop()

st.title("🧬 Restriction Enzymes")
st.caption(f"Storage location: {FREEZER_NAME} | Rack {RACK_NUMBER} | Box {BOX_NUMBER}")


# -----------------------------
# ADD ENZYME
# -----------------------------

st.header("Add Restriction Enzyme")
with st.form("add_enzyme_form"):
    enzyme_name = st.text_input("Enzyme Name", placeholder="Enter enzyme name")
    dilute_before_use = st.radio("Dilute Before Use", YES_NO, index=1, horizontal=True)
    time_saver = st.radio("Time Saver", YES_NO, index=0, horizontal=True)

    buffer_value = buffer_checkboxes("add", [])
    temperature = st.selectbox(
        "Temperature",
        TEMPERATURES,
        index=TEMPERATURES.index("37°C"),
    )
    notes = st.text_area("Notes", placeholder="Enter any additional notes", height=110)
    add_submitted = st.form_submit_button("Add Enzyme", use_container_width=True)

if add_submitted:
    if not enzyme_name.strip():
        st.error("Please enter an enzyme name.")
    elif not buffer_value:
        st.error("Please select at least one buffer.")
    else:
        new_row = pd.DataFrame(
            [[enzyme_name.strip(), temperature, buffer_value, time_saver,
              dilute_before_use, FREEZER_NAME, RACK_NUMBER, BOX_NUMBER, notes.strip()]],
            columns=ENZYME_COLUMNS,
        )
        updated = pd.concat([inventory, new_row], ignore_index=True)
        new_sha = save_enzymes(updated, github_sha)
        if new_sha is not None:
            st.success(f"{enzyme_name.strip()} was saved to GitHub.")
            st.rerun()


# -----------------------------
# SEARCH AND VIEW
# -----------------------------

st.divider()
st.header("Search and View Enzymes")
search = st.text_input("Search enzymes", key="enzyme_search")
if search:
    filtered = inventory[
        inventory.astype(str).apply(
            lambda row: row.str.contains(search, case=False, na=False, regex=False).any(),
            axis=1,
        )
    ]
else:
    filtered = inventory

st.dataframe(filtered, use_container_width=True, hide_index=True)


# -----------------------------
# UPDATE ENZYME
# -----------------------------

st.divider()
st.header("Update Enzyme Information")
if inventory.empty:
    st.info("No enzymes have been added yet.")
else:
    enzyme_options = {
        i: f"{row['Enzyme Name']} | {row['Buffer for 100% Activity']} | {row['Temperature']}"
        for i, row in inventory.iterrows()
    }
    selected_index = st.selectbox(
        "Select enzyme to update",
        list(enzyme_options),
        format_func=lambda value: enzyme_options[value],
        key="update_enzyme_selection",
    )
    current = inventory.loc[selected_index]

    with st.form(f"edit_enzyme_form_{selected_index}"):
        updated_enzyme_name = st.text_input("Enzyme Name", value=str(current["Enzyme Name"]))
        current_dilute = str(current["Dilute Before Use"])
        updated_dilute = st.radio(
            "Dilute Before Use", YES_NO,
            index=YES_NO.index(current_dilute) if current_dilute in YES_NO else 1,
            horizontal=True,
        )
        current_saver = str(current["Time Saver"])
        updated_time_saver = st.radio(
            "Time Saver", YES_NO,
            index=YES_NO.index(current_saver) if current_saver in YES_NO else 0,
            horizontal=True,
        )
        updated_buffer_value = buffer_checkboxes(
            f"edit_{selected_index}",
            parse_buffers(current["Buffer for 100% Activity"]),
        )
        current_temperature = str(current["Temperature"])
        updated_temperature = st.selectbox(
            "Temperature",
            TEMPERATURES,
            index=TEMPERATURES.index(current_temperature)
            if current_temperature in TEMPERATURES else TEMPERATURES.index("37°C"),
        )
        updated_notes = st.text_area("Notes", value=str(current["Notes"]), height=110)
        save_edit = st.form_submit_button("Save Enzyme Updates", use_container_width=True)

    if save_edit:
        if not updated_enzyme_name.strip():
            st.error("Please enter an enzyme name.")
        elif not updated_buffer_value:
            st.error("Please select at least one buffer.")
        else:
            updated = inventory.copy()
            updated.loc[selected_index, "Enzyme Name"] = updated_enzyme_name.strip()
            updated.loc[selected_index, "Time Saver"] = updated_time_saver
            updated.loc[selected_index, "Temperature"] = updated_temperature
            updated.loc[selected_index, "Buffer for 100% Activity"] = updated_buffer_value
            updated.loc[selected_index, "Dilute Before Use"] = updated_dilute
            updated.loc[selected_index, "Notes"] = updated_notes.strip()
            new_sha = save_enzymes(updated, github_sha)
            if new_sha is not None:
                st.success("Enzyme information updated and saved to GitHub.")
                st.rerun()


# -----------------------------
# DOWNLOAD
# -----------------------------

st.divider()
st.header("Download Restriction Enzyme Inventory")
st.download_button(
    "Download Enzyme CSV",
    data=inventory.to_csv(index=False),
    file_name="restriction_enzymes.csv",
    mime="text/csv",
    key="download_enzyme_csv",
    use_container_width=True,
)


# -----------------------------
# DELETE ENZYME
# -----------------------------

st.divider()
st.header("Delete Enzyme")
if inventory.empty:
    st.info("There are no enzymes to delete.")
else:
    delete_options = {
        i: f"{row['Enzyme Name']} | {row['Buffer for 100% Activity']} | {row['Temperature']}"
        for i, row in inventory.iterrows()
    }
    delete_index = st.selectbox(
        "Select enzyme to delete",
        list(delete_options),
        format_func=lambda value: delete_options[value],
        key="delete_enzyme_selection",
    )
    confirm_delete = st.checkbox("I confirm that I want to delete this enzyme.", key="confirm_delete_enzyme")
    if st.button("Delete Enzyme", key="delete_enzyme_button", use_container_width=True):
        if not confirm_delete:
            st.warning("Please confirm before deleting.")
        else:
            updated = inventory.drop(index=delete_index).reset_index(drop=True)
            new_sha = save_enzymes(updated, github_sha)
            if new_sha is not None:
                st.success("Enzyme deleted from GitHub.")
                st.rerun()
