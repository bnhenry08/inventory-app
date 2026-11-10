
import streamlit as st

st.set_page_config(
    page_title="Lab Inventory",
    page_icon="🧬",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Make inventory tiles larger */
    div[data-testid="stPageLink"] a {
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 18px;
        font-size: 25px !important;
        font-weight: 700;
        padding: 20px;
    }

    /* Increase the icon size */
    div[data-testid="stPageLink"] a span {
        font-size: 45px !important;
    }

    /* Make the page title larger */
    h1 {
        font-size: 42px !important;
        text-align: center;
        padding-bottom: 20px;
    }

    /* Add space between rows */
    div[data-testid="stHorizontalBlock"] {
        gap: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧬 Lab Inventory")

st.write("")

col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.page_link(
            "pages/freezer_20C.py",
            label="-20°C Freezer",
            icon="❄️",
            use_container_width=True
        )

with col2:
    with st.container(border=True):
        st.page_link(
            "pages/freezer_80C.py",
            label="-80°C Freezer",
            icon="🧊",
            use_container_width=True
        )

st.write("")

col3, col4 = st.columns(2, gap="large")

with col3:
    with st.container(border=True):
        st.page_link(
            "pages/restriction_enzymes.py",
            label="Restriction Enzymes",
            icon="🧬",
            use_container_width=True
        )

with col4:
    with st.container(border=True):
        st.markdown(
            """
            <div style="
                text-align:center;
                padding:25px 5px;
                min-height:150px;
            ">
                <div style="font-size:60px;">🔬</div>
                <div style="
                    font-size:24px;
                    font-weight:700;
                ">
                    Lab Inventory
                </div>
                <div style="font-size:15px; opacity:0.65;">
                    Storage & Organization
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
