
import streamlit as st

st.set_page_config(
    page_title="Lab Inventory",
    page_icon="🧬",
    layout="wide"
)

st.markdown(
    """
    <style>
    .home-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 25px;
    }

    div[data-testid="stPageLink"] a {
        min-height: 155px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        border-radius: 18px;
        font-size: 21px !important;
        font-weight: 700;
        text-align: center;
        padding: 15px;
    }

    div[data-testid="stPageLink"] a span {
        font-size: 48px !important;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 16px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="home-title">🧬 Lab Inventory</div>',
    unsafe_allow_html=True
)

# First row
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.page_link(
        "pages/freezer_20C.py",
        label="-20°C Freezer",
        icon="❄️",
        use_container_width=True
    )

with col2:
    st.page_link(
        "pages/freezer_80C.py",
        label="-80°C Freezer",
        icon="🧊",
        use_container_width=True
    )

st.write("")

# Second row
col3, col4 = st.columns(2, gap="medium")

with col3:
    st.page_link(
        "pages/restriction_enzymes.py",
        label="Restriction Enzymes",
        icon="🧬",
        use_container_width=True
    )

with col4:
    st.page_link(
        "inventory.py",
        label="Home",
        icon="🏠",
        use_container_width=True
    )
