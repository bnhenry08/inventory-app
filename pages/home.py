
import streamlit as st

# -----------------------------
# HOMEPAGE STYLING
# -----------------------------

st.markdown(
    """
    <style>
    /* Main page title */
    .home-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 30px;
    }

    /* Inventory page tiles */
    div[data-testid="stPageLink"] {
        width: 100%;
    }

    div[data-testid="stPageLink"] a {
        min-height: 155px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 14px !important;
        border-radius: 18px !important;
        padding: 20px 10px !important;
        text-align: center !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }

    /* Keep the icon and text vertically arranged */
    div[data-testid="stPageLink"] a > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 12px !important;
    }

    /* Icon size */
    div[data-testid="stPageLink"] a [data-testid="stIconEmoji"],
    div[data-testid="stPageLink"] a [data-testid="stIconMaterial"] {
        font-size: 48px !important;
        line-height: 1.2 !important;
    }

    /* Keep two columns on smaller screens */
    div[data-testid="stHorizontalBlock"] {
        gap: 16px !important;
    }

    @media (max-width: 640px) {
        .home-title {
            font-size: 30px;
            margin-bottom: 20px;
        }

        div[data-testid="stPageLink"] a {
            min-height: 135px !important;
            font-size: 16px !important;
            padding: 12px 5px !important;
        }

        div[data-testid="stPageLink"] a [data-testid="stIconEmoji"],
        div[data-testid="stPageLink"] a [data-testid="stIconMaterial"] {
            font-size: 42px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HOMEPAGE TITLE
# -----------------------------

st.markdown(
    '<div class="home-title">🧬 Lab Inventory</div>',
    unsafe_allow_html=True
)

# -----------------------------
# FIRST ROW
# -----------------------------

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

# -----------------------------
# SECOND ROW
# -----------------------------

col3, col4 = st.columns(2, gap="medium")

with col3:
    st.page_link(
        "pages/restriction_enzymes.py",
        label="Restriction Enzymes",
        icon="🧬",
        use_container_width=True
    )
