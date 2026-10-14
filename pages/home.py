import streamlit as st

st.title("🧬 Laboratory Inventory")

st.write("Select an inventory to get started.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("❄️ -20°C Inventory")
    st.write("Browse and manage materials stored in the -20°C freezer.")
    st.page_link(
        "pages/freezer_20C.py",
        label="Open -20°C Inventory →",
        icon="❄️",
        use_container_width=True
    )

with col2:
    st.subheader("🧊 -80°C Inventory")
    st.write("Browse and manage materials stored in the -80°C freezer.")
    st.page_link(
        "pages/freezer_80C.py",
        label="Open -80°C Inventory →",
        icon="🧊",
        use_container_width=True
    )

with col3:
    st.subheader("✂️ Restriction Enzymes")
    st.write("Browse and manage the restriction enzyme inventory.")
    st.page_link(
        "pages/restriction_enzymes.py",
        label="Open Restriction Enzymes →",
        icon="✂️",
        use_container_width=True
    )
