import streamlit as st

st.title("🧬 Laboratory Inventory")

st.write("Select an inventory from the navigation menu on the left.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("❄️ -20°C Inventory")
    st.write("Browse and manage materials stored in the -20°C freezer.")

with col2:
    st.subheader("🧊 -80°C Inventory")
    st.write("Browse and manage materials stored in the -80°C freezer.")

with col3:
    st.subheader("✂️ Restriction Enzymes")
    st.write("Browse and manage the restriction enzyme inventory.")

