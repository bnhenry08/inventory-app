import streamlit as st

st.set_page_config(
    page_title="Laboratory Inventory",
    page_icon="🧬"
)

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

if pg.title == "Home":

    st.title("🧬 Laboratory Inventory")

    st.write("Select the inventory you would like to open.")

    col1, col2, col3 = st.columns(3)

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

    with col3:
        if st.button(
            "✂️ Restriction Enzymes",
            use_container_width=True
        ):
            st.switch_page("pages/restriction_enzymes.py")

pg.run()
