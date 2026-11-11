import streamlit as st

st.set_page_config(
    page_title="Laboratory Inventory",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Responsive styling for phones and tablets.
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: clamp(0.8rem, 3vw, 2.5rem);
        padding-right: clamp(0.8rem, 3vw, 2.5rem);
    }
    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stDownloadButton"] button {
        min-height: 2.8rem;
        border-radius: 0.65rem;
        font-weight: 600;
        width: 100%;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] div[role="combobox"] {
        min-height: 2.7rem;
    }
    div[data-testid="stRadio"] > div {
        flex-wrap: wrap;
        gap: 0.45rem 0.9rem;
    }
    div[data-testid="stDataFrame"] {
        width: 100%;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 2rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
        h1 { font-size: 1.65rem !important; }
        h2 { font-size: 1.35rem !important; }
        h3 { font-size: 1.12rem !important; }
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.7rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        div[data-testid="stRadio"] > div {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.55rem !important;
        }
        div[data-testid="stRadio"] label {
            align-items: flex-start;
            line-height: 1.25;
        }
        div[data-testid="stDataFrame"] {
            overflow-x: auto;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

home_page = st.Page(
    "pages/home.py",
    title="Home",
    icon="🧬",
    default=True
)

freezer_20C_page = st.Page(
    "pages/freezer_20C.py",
    title="-20°C Inventory",
    icon="❄️"
)

freezer_80C_page = st.Page(
    "pages/freezer_80C.py",
    title="-80°C Inventory",
    icon="🧊"
)

restriction_enzymes_page = st.Page(
    "pages/restriction_enzymes.py",
    title="Restriction Enzymes",
    icon="✂️"
)

# NEW: Read-only Plasmid Inventory
plasmid_inventory_page = st.Page(
    "pages/plasmid_inventory.py",
    title="View Plasmid Inventory",
    icon="⭕"
)

pg = st.navigation([
    home_page,
    freezer_20C_page,
    freezer_80C_page,
    restriction_enzymes_page,
    plasmid_inventory_page
])

pg.run()
