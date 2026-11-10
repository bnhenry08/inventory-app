
import streamlit as st

st.title("🧬 Lab Inventory")

st.markdown(
    """
    <style>
    div[data-testid="stPageLink"] a {
        min-height: 115px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 16px;
        font-size: 20px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("")

col1, col2 = st.columns(2, gap="medium")

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

col3, col4 = st.columns(2, gap="medium")

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
            <div style="text-align:center; padding:20px 5px;">
                <div style="font-size:36px;">🔬</div>
                <div style="font-weight:600;">Lab Inventory</div>
                <div style="font-size:12px; opacity:0.65;">
                    Storage & Organization
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
