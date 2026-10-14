import streamlit as st

st.set_page_config(
    page_title="Laboratory Inventory",
    page_icon="🧬"
)

# ============================================================
# PAGE NAVIGATION
# ============================================================

pg = st.navigation(
    [
        st.Page(
            "inventory.py",
            title="Home",
            icon="🧬"
        ),
        st.Page(
            "pages/freezer_20C.py",
            title="20°C Inventory",
            icon="❄️"
        ),
        st.Page(
            "pages/freezer_80C.py",
            title="-80°C Inventory",
            icon="🧊"
        ),
        st.Page(
            "pages/restriction_enzymes.py",
            title="estriction Enzymes",
            icon="✂️"
        )
    ]
)

# ============================================================
# HOME PAGE
# ============================================================

if pg.title == "Home":

    st.title("🧬 Laboratory Inventory")

    st.write(
        "Select the inventory you would like to open."
    )

    # Three buttons side by side
    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # -20°C FREEZER
    # --------------------------------------------------------

    with col1:
        if st.button(
            "❄️ -20°C Inventory",
            key="home_freezer_20C",
            use_container_width=True
        ):
            st.switch_page("pages/freezer_20C.py")

    # --------------------------------------------------------
    # -80°C FREEZER
    # --------------------------------------------------------

    with col2:
        if st.button(
            "🧊 -80°C Inventory",
            key="home_freezer_80C",
            use_container_width=True
        ):
            st.switch_page("pages/freezer_80C.py")

    # --------------------------------------------------------
    # RESTRICTION ENZYMES
    # --------------------------------------------------------

    with col3:
        if st.button(
            "✂️ Restriction Enzymes",
            key="home_restriction_enzymes",
            use_container_width=True
        ):
            st.switch_page("pages/restriction_enzymes.py")

# ============================================================
# RUN SELECTED PAGE
# ============================================================

pg.run()
