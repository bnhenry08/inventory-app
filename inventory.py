import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Laboratory Inventory",
    page_icon="🧬",
    layout="wide"
)

# ============================================================
# PAGE NAVIGATION
# ============================================================

home_page = st.Page(
    "inventory.py",
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

# ============================================================
# HOME PAGE CONTENT
# ============================================================

if pg == home_page:

    st.title("🧬 Laboratory Inventory")

    st.write(
        "Select an inventory from the navigation menu "
        "on the left."
    )

    st.divider()

    st.subheader("Available Inventories")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ❄️ -20°C Inventory")
        st.write(
            "Browse and manage laboratory materials "
            "stored in the -20°C freezer."
        )

    with col2:
        st.markdown("### 🧊 -80°C Inventory")
        st.write(
            "Browse and manage laboratory materials "
            "stored in the -80°C freezer."
        )

    with col3:
        st.markdown("### ✂️ Restriction Enzymes")
        st.write(
            "Browse and manage the restriction enzyme inventory."
        )

# ============================================================
# RUN SELECTED PAGE
# ============================================================

pg.run()
