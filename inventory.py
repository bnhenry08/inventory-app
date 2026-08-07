import streamlit as st

st.set_page_config(page_title="Laboratory Inventory", page_icon="🧬")

st.title("🧬 Laboratory Inventory")

st.write("Select the freezer inventory you would like to open.")

col1, col2 = st.columns(2)

with col1:
    st.page_link(
        "pages/inventory_20C.py",
        label="❄️ -20°C Inventory",
        icon="📦"
    )

with col2:
    st.page_link(
        "pages/inventory_80C.py",
        label="🧊 -80°C Inventory",
        icon="🧪"
    )
