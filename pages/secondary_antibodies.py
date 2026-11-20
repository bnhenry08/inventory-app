
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

# Remove extra spaces and non-breaking spaces from headers

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

filter_columns = [
    ("Host (Species used to develop the antibody)", "Host"),
    ("Target Species (Species to which antibody binds)", "Target Species"),
    ("Antibody Reactivity Target", "Reactivity Target")
]

filter_values = {}

for column_name, filter_label in filter_columns:

    if column_name in antibody_data.columns:

        options = (
            antibody_data[column_name]
            .dropna()
            .astype(str)
            .str.strip()
        )

        options = sorted(
            [value for value in options.unique() if value],
            key=str.casefold
        )

        filter_values[filter_label] = options

    else:
        filter_values[filter_label] = []

with col1:
    selected_host = st.selectbox(
        "Host Species",
        ["All"] + filter_values["Host"],
        key="secondary_host_filter"
    )

with col2:
    selected_target = st.selectbox(
        "Target Species",
        ["All"] + filter_values["Target Species"],
        key="secondary_target_filter"
    )

with col3:
    selected_reactivity = st.selectbox(
        "Antibody Reactivity Target",
        ["All"] + filter_values["Reactivity Target"],
        key="secondary_reactivity_filter"
    )

# -----------------------------
# APPLY FILTERS
# -----------------------------

filtered_data = antibody_data.copy()

if selected_host != "All":
    filtered_data = filtered_data[
        filtered_data["Host (Species used to develop the antibody)"]
        .astype("string")
        .str.strip()
        == selected_host
    ]

if selected_target != "All":
    filtered_data = filtered_data[
        filtered_data["Target Species (Species to which antibody binds)"]
        .astype("string")
        .str.strip()
        == selected_target
    ]

if selected_reactivity != "All":
    filtered_data = filtered_data[
        filtered_data["Antibody Reactivity Target"]
        .astype("string")
        .str.strip()
        == selected_reactivity
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
