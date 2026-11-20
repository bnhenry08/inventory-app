
import streamlit as st
import pandas as pd
from pathlib import Path
import re

# -----------------------------
# PAGE TITLE
# -----------------------------

st.title("🧪 Secondary Antibodies")

st.write("Search and view the laboratory secondary antibody inventory.")

# -----------------------------
# MANUALLY DEFINED FILTER OPTIONS
# -----------------------------

HOST_OPTIONS = [
    "Goat",
    "Donkey",
    "Rabbit",
    "Mouse",
    "Sheep",
    "Chicken"
]

TARGET_SPECIES_OPTIONS = [
    "Mouse",
    "Rabbit",
    "Rat",
    "Human",
    "Chicken",
    "Bovine",
    "Canine",
    "Porcine",
    "Multiple Species"
]

REACTIVITY_OPTIONS = [
    "IgG",
    "IgM",
    "IgA",
    "IgG (H+L)",
    "Heavy Chain",
    "Light Chain",
    "Other"
]

# -----------------------------
# LOAD CSV
# -----------------------------

csv_path = Path(__file__).resolve().parent.parent / "secondary_antibodies.csv"

try:
    antibody_data = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        low_memory=False
    )

except UnicodeDecodeError:
    antibody_data = pd.read_csv(
        csv_path,
        encoding="latin1",
        low_memory=False
    )

except FileNotFoundError:
    st.error(
        "Could not find secondary_antibodies.csv. "
        "Make sure it is in the main inventory-app repository folder."
    )
    st.stop()

# -----------------------------
# CLEAN COLUMN NAMES
# -----------------------------

antibody_data.columns = [
    re.sub(r"\s+", " ", str(column)).strip()
    for column in antibody_data.columns
]

# -----------------------------
# INVENTORY SUMMARY
# -----------------------------

st.metric(
    label="Number of Secondary Antibodies",
    value=len(antibody_data)
)

st.write("")

# -----------------------------
# SEARCH
# -----------------------------

search_term = st.text_input(
    "🔎 Search secondary antibodies",
    placeholder="Enter antibody name, catalog number, company, species, reactivity, or keyword..."
)

# -----------------------------
# FILTER OPTIONS
# -----------------------------

st.subheader("Filter Antibodies")

col1, col2, col3 = st.columns(3)

with col1:
    selected_host = st.selectbox(
        "Host Species",
        ["All"] + HOST_OPTIONS,
        key="secondary_host_filter"
    )

with col2:
    selected_target = st.selectbox(
        "Target Species",
        ["All"] + TARGET_SPECIES_OPTIONS,
        key="secondary_target_filter"
    )

with col3:
    selected_reactivity = st.selectbox(
        "Antibody Reactivity Target",
        ["All"] + REACTIVITY_OPTIONS,
        key="secondary_reactivity_filter"
    )

# -----------------------------
# APPLY FILTERS
# -----------------------------

filtered_data = antibody_data.copy()

host_column = "Host (Species used to develop the antibody)"
target_column = "Target Species (Species to which antibody binds)"
reactivity_column = "Antibody Reactivity Target"

if selected_host != "All" and host_column in filtered_data.columns:
    filtered_data = filtered_data[
        filtered_data[host_column]
        .astype("string")
        .str.strip()
        .str.casefold()
        == selected_host.casefold()
    ]

if selected_target != "All" and target_column in filtered_data.columns:
    filtered_data = filtered_data[
        filtered_data[target_column]
        .astype("string")
        .str.strip()
        .str.casefold()
        == selected_target.casefold()
    ]

if selected_reactivity != "All" and reactivity_column in filtered_data.columns:
    filtered_data = filtered_data[
        filtered_data[reactivity_column]
        .astype("string")
        .str.strip()
        .str.casefold()
        == selected_reactivity.casefold()
    ]

# -----------------------------
# APPLY KEYWORD SEARCH
# -----------------------------

if search_term:

    matching_rows = filtered_data.astype(str).apply(
        lambda column: column.str.contains(
            search_term,
            case=False,
            na=False,
            regex=False
        )
    ).any(axis=1)

    filtered_data = filtered_data[matching_rows]

# -----------------------------
# SEARCH RESULTS
# -----------------------------

st.caption(
    f"Showing {len(filtered_data)} of {len(antibody_data)} secondary antibodies"
)

st.write("")

# -----------------------------
# READ-ONLY TABLE
# -----------------------------

st.dataframe(
    filtered_data,
    use_container_width=True,
    hide_index=True,
    height="content"
)
