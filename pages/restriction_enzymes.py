# -----------------------------
# RESTRICTION ENZYMES
# -----------------------------

st.header("🧬 Restriction Enzymes")

st.info(
    "Storage location: Pig 150 → Rack 11 → Box 1"
)

# -----------------------------
# ADD RESTRICTION ENZYME
# -----------------------------

st.subheader("➕ Add Restriction Enzyme")

with st.form("restriction_enzyme_form"):

    enzyme_name = st.text_input(
        "Enzyme Name",
        placeholder="Enter enzyme name (e.g., EcoRI)"
    )

    time_saver = st.radio(
        "Time Saver",
        ["Y", "N"],
        horizontal=True,
        index=0
    )

    temperature = st.radio(
        "Temperature",
        ["25°C", "37°C", "50°C", "55°C",
         "60°C", "65°C", "75°C"],
        horizontal=True,
        index=1
    )

    buffer = st.radio(
        "Buffer for 100% Activity",
        [
            "NEBuffer r3.1",
            "rCutSmart™ Buffer",
            "Different Buffer"
        ],
        horizontal=True,
        index=1
    )

    different_buffer = st.text_input(
        "Specify Different Buffer (if applicable)",
        placeholder="Enter buffer name",
        help="Only needed if Different Buffer is selected."
    )

    dilute_before_use = st.radio(
        "Dilute Before Use",
        ["Y", "N"],
        horizontal=True,
        index=1
    )

    enzyme_notes = st.text_area(
        "Notes",
        placeholder="Optional notes",
        height=80
    )

    add_enzyme = st.form_submit_button(
        "Add Restriction Enzyme"
    )

    if add_enzyme:

        if not enzyme_name.strip():
            st.error("Please enter an enzyme name.")

        elif (
            buffer == "Different Buffer"
            and not different_buffer.strip()
        ):
            st.error("Please specify the buffer.")

        else:

            final_buffer = (
                different_buffer.strip()
                if buffer == "Different Buffer"
                else buffer
            )

            new_row = pd.DataFrame(
                [{
                    "Box Name": "Restriction Enzymes",
                    "Item": enzyme_name.strip(),
                    "Quantity": 1,
                    "Freezer Name": "Pig 150",
                    "Rack Number": "11",
                    "Box Number": "1",
                    "Notes": enzyme_notes.strip(),
                    "Time Saver": time_saver,
                    "Temperature": temperature,
                    "Buffer for 100% Activity": final_buffer,
                    "Dilute Before Use": dilute_before_use
                }],
                columns=COLUMNS
            )

            updated_inventory = pd.concat(
                [inventory, new_row],
                ignore_index=True
            )

            new_sha = save_to_github(
                updated_inventory,
                github_sha
            )

            if new_sha is not None:
                st.success(
                    f"{enzyme_name.strip()} saved successfully!"
                )
                st.rerun()


# -----------------------------
# VIEW ALL RESTRICTION ENZYMES
# -----------------------------

st.subheader("📋 Restriction Enzyme Inventory")

restriction_enzymes = inventory[
    inventory["Box Name"].astype(str)
    == "Restriction Enzymes"
].copy()

if restriction_enzymes.empty:

    st.info("No restriction enzymes have been added yet.")

else:

    enzyme_columns = [
        "Item",
        "Time Saver",
        "Temperature",
        "Buffer for 100% Activity",
        "Dilute Before Use",
        "Notes"
    ]

    st.dataframe(
        restriction_enzymes[enzyme_columns],
        use_container_width=True,
        hide_index=True
    )


# -----------------------------
# SEARCH AND UPDATE RESTRICTION ENZYME
# -----------------------------

st.subheader("✏️ Update Restriction Enzyme")

enzyme_search = st.text_input(
    "Search enzyme to update",
    key="restriction_enzyme_search"
)

if enzyme_search:

    enzyme_matches = inventory[
        (
            inventory["Box Name"].astype(str)
            == "Restriction Enzymes"
        )
        &
        (
            inventory["Item"].astype(str).str.contains(
                enzyme_search,
                case=False,
                na=False,
                regex=False
            )
        )
    ].copy()

    if enzyme_matches.empty:

        st.warning("No matching restriction enzymes found.")

    else:

        enzyme_matches = enzyme_matches.reset_index()

        enzyme_options = {
            i: (
                f"{row['Item']} | "
                f"Time Saver: {row['Time Saver']} | "
                f"Temp: {row['Temperature']} | "
                f"Buffer: {row['Buffer for 100% Activity']}"
            )
            for i, row in enzyme_matches.iterrows()
        }

        selected_enzyme = st.selectbox(
            "Select enzyme",
            list(enzyme_options.keys()),
            format_func=lambda x: enzyme_options[x],
            key="restriction_enzyme_selection"
        )

        enzyme_index = enzyme_matches.loc[
            selected_enzyme,
            "index"
        ]

        current_enzyme = inventory.loc[enzyme_index]

        with st.form("update_restriction_enzyme_form"):

            updated_enzyme_name = st.text_input(
                "Enzyme Name",
                value=str(current_enzyme["Item"])
            )

            current_time_saver = str(
                current_enzyme["Time Saver"]
            )

            updated_time_saver = st.radio(
                "Time Saver",
                ["Y", "N"],
                index=(
                    ["Y", "N"].index(current_time_saver)
                    if current_time_saver in ["Y", "N"]
                    else 0
                ),
                horizontal=True
            )

            temperatures = [
                "25°C", "37°C", "50°C", "55°C",
                "60°C", "65°C", "75°C"
            ]

            current_temperature = str(
                current_enzyme["Temperature"]
            )

            updated_temperature = st.radio(
                "Temperature",
                temperatures,
                index=(
                    temperatures.index(current_temperature)
                    if current_temperature in temperatures
                    else 1
                ),
                horizontal=True
            )

            buffers = [
                "NEBuffer r3.1",
                "rCutSmart™ Buffer",
                "Different Buffer"
            ]

            current_buffer = str(
                current_enzyme["Buffer for 100% Activity"]
            )

            if current_buffer in buffers:
                buffer_index = buffers.index(current_buffer)
                custom_buffer = ""
            elif current_buffer:
                buffer_index = 2
                custom_buffer = current_buffer
            else:
                buffer_index = 1
                custom_buffer = ""

            updated_buffer = st.radio(
                "Buffer for 100% Activity",
                buffers,
                index=buffer_index,
                horizontal=True
            )

            updated_custom_buffer = ""

            if updated_buffer == "Different Buffer":

                updated_custom_buffer = st.text_input(
                    "Specify Different Buffer",
                    value=custom_buffer
                )

            current_dilute = str(
                current_enzyme["Dilute Before Use"]
            )

            updated_dilute = st.radio(
                "Dilute Before Use",
                ["Y", "N"],
                index=(
                    ["Y", "N"].index(current_dilute)
                    if current_dilute in ["Y", "N"]
                    else 1
                ),
                horizontal=True
            )

            updated_notes = st.text_area(
                "Notes",
                value=str(current_enzyme["Notes"])
            )

            save_enzyme = st.form_submit_button(
                "Save Enzyme Updates"
            )

            if save_enzyme:

                if not updated_enzyme_name.strip():

                    st.error("Please enter an enzyme name.")

                elif (
                    updated_buffer == "Different Buffer"
                    and not updated_custom_buffer.strip()
                ):

                    st.error("Please specify the buffer.")

                else:

                    final_buffer = (
                        updated_custom_buffer.strip()
                        if updated_buffer == "Different Buffer"
                        else updated_buffer
                    )

                    inventory.loc[
                        enzyme_index, "Item"
                    ] = updated_enzyme_name.strip()

                    inventory.loc[
                        enzyme_index, "Time Saver"
                    ] = updated_time_saver

                    inventory.loc[
                        enzyme_index, "Temperature"
                    ] = updated_temperature

                    inventory.loc[
                        enzyme_index, "Buffer for 100% Activity"
                    ] = final_buffer

                    inventory.loc[
                        enzyme_index, "Dilute Before Use"
                    ] = updated_dilute

                    inventory.loc[
                        enzyme_index, "Notes"
                    ] = updated_notes

                    # Always enforce the designated location.
                    inventory.loc[
                        enzyme_index, "Box Name"
                    ] = "Restriction Enzymes"

                    inventory.loc[
                        enzyme_index, "Freezer Name"
                    ] = "Pig 150"

                    inventory.loc[
                        enzyme_index, "Rack Number"
                    ] = "11"

                    inventory.loc[
                        enzyme_index, "Box Number"
                    ] = "1"

                    new_sha = save_to_github(
                        inventory,
                        github_sha
                    )

                    if new_sha is not None:
                        st.success(
                            "Restriction enzyme updated and saved to GitHub."
                        )
                        st.rerun()
