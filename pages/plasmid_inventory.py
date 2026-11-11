
import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------
# PAGE TITLE
# -----------------------------

st.title("⭕  Plasmid Inventory")

st.write("Search and view the laboratory plasmid inventory.")

# -----------------------------
# LOAD CSV
# -----------------------------

csv_path = Path(__file__).resolve().parent.parent / "plasmids.csv"

try:
    plasmid_data = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        low_memory=False
    )

except UnicodeDecodeError:
    plasmid_data = pd.read_csv(
        csv_path,
        encoding="latin1",
        low_memory=False
    )

except FileNotFoundError:
    st.error(
        "Could not find plasmids.csv. "
        "Make sure it is in the main inventory-app repository folder."
    )
    st.stop()

# -----------------------------
# FIND SNAPGENE FILE COLUMN
# -----------------------------

snapgene_column = None

# First, look for a column containing a Google Drive URL
for column in plasmid_data.columns:
    values = plasmid_data[column].dropna().astype(str)

    if values.str.contains(
        r"https?://",
        case=False,
        regex=True
    ).any():
        snapgene_column = column
        break

# If no URL is present yet, look for a likely file column
if snapgene_column is None:
    for column in plasmid_data.columns:
        if any(
            word in column.lower()
            for word in ["snapgene", "sequence file", "plasmid file"]
        ):
            snapgene_column = column
            break

# -----------------------------
# INVENTORY SUMMARY
# -----------------------------

st.metric(
    label="Total Plasmids",
    value=len(plasmid_data)
)

st.write("")

# -----------------------------
# SEARCH
# -----------------------------

search_term = st.text_input(
    "🔎 Search plasmids",
    placeholder="Enter a plasmid name, gene, antibiotic, marker, or other keyword..."
)

if search_term:
    matching_rows = plasmid_data.astype(str).apply(
        lambda column: column.str.contains(
            search_term,
            case=False,
            na=False,
            regex=False
        )
    ).any(axis=1)

    filtered_data = plasmid_data[matching_rows]

else:
    filtered_data = plasmid_data

# -----------------------------
# SEARCH RESULTS
# -----------------------------

st.caption(
    f"Showing {len(filtered_data)} of {len(plasmid_data)} plasmids"
)

# -----------------------------
# READ-ONLY TABLE
# -----------------------------

column_config = {}

if snapgene_column is not None:
    column_config[snapgene_column] = st.column_config.LinkColumn(
        label=snapgene_column,
        display_text="Open SnapGene File"
    )

st.dataframe(
    filtered_data,
    column_config=column_config,
    use_container_width=True,
    hide_index=True,
    height="content"
)
