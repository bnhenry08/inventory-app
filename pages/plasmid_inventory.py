
import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------
# PAGE TITLE
# -----------------------------

st.title("🧬 Plasmid Inventory")

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

st.dataframe(
    filtered_data,
    use_container_width=True,
    hide_index=True,
    height="content"
)
