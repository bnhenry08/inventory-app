import streamlit as st

st.set_page_config(
    page_title="Laboratory Inventory",
    page_icon="🧬"
)

st.title("🧬 Laboratory Inventory")

st.write("Select the freezer inventory you would like to open.")

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "❄️ -20°C Inventory",
        use_container_width=True
    ):
        st.switch_page("pages/freezer_20C.py")


with col2:
    if st.button(
        "🧊 -80°C Inventory",
        use_container_width=True
    ):
        st.switch_page("pages/freezer_80C.py")
