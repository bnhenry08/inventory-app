import streamlit as st

st.set_page_config(
    page_title="Laboratory Inventory",
    page_icon="🧬",
    layout="wide"
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

pg = st.navigation(
    [
        home_page,
        freezer_20C_page,
        freezer_80C_page,
        restriction_enzymes_page
    ]
)

pg.run()
