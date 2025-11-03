import streamlit as st
import time
from db_connection import get_connection, fetch_data, execute_query

def app():
    st.title("👮 CASE ASSIGNMENT")

    from db_connection import check_tables_exist
    if not check_tables_exist():
        st.error("❌ REQUIRED DATABASE TABLES ARE MISSING. Please run the SQL setup script first.")
        return

    conn = get_connection()
    if not conn:
        st.error("❌ DATABASE CONNECTION FAILED.")
        return

    try:
        # ✅ Show Reported + Assigned
        cases = fetch_data(
            "SELECT CASE_ID, CASE_TITLE, STATUS FROM CASE_TABLE WHERE STATUS IN ('Reported')"
        )

        if not cases:
            st.info("✅ NO UNASSIGNED CASES.")
            return

        # ✅ Search box with key to retain value
        search_query = st.text_input("🔍 Search Case (ID / Title)", key="case_search").lower()

        # Filter cases by search query
        filtered_cases = [
            case for case in cases
            if search_query in case['CASE_ID'].lower()
            or search_query in case['CASE_TITLE'].lower()
        ]

        if not filtered_cases:
            st.warning("No matching cases found.")
            return

        cid_officers = fetch_data(
            "SELECT STAFFID, SURNAME, OTHERNAMES FROM USERLOGIN WHERE ROLE = 'CID' AND IS_ACTIVE = 1"
        )
        
        officer_options = {f"{o['STAFFID']} - {o['SURNAME']}, {o['OTHERNAMES']}": o['STAFFID'] for o in cid_officers}

        for case in filtered_cases:
            with st.expander(f"{case['CASE_ID']} - {case['CASE_TITLE']}"):

                # ✅ show status inside expander
                st.write(f"📌 Current Status: **{case['STATUS']}**")

                if not officer_options:
                    st.warning("No CID officers available for assignment")
                    continue
                    
                selected_officer = st.selectbox(
                    f"ASSIGN CID OFFICER",
                    options=list(officer_options.keys()),
                    key=f"officer_{case['CASE_ID']}"
                )
                
                officer_id = officer_options[selected_officer]
                
                reason = st.text_area(
                    f"ASSIGNMENT REASON",
                    placeholder="Explain why this case is being assigned...",
                    key=f"reason_{case['CASE_ID']}"
                )

                if st.button(f"ASSIGN CASE", key=f"btn_{case['CASE_ID']}"):
                    if not reason.strip():
                        st.warning("Please provide an assignment reason")
                        return

                    try:
                        update_success = execute_query(
                            """
                            UPDATE CASE_TABLE
                            SET CID_OFFICER_STAFFID = :1,
                                STATUS = 'Assigned',
                                ASSIGNED_AT = CURRENT_TIMESTAMP,
                                UPDATED_AT = CURRENT_TIMESTAMP
                            WHERE CASE_ID = :2
                            """,
                            (officer_id, case['CASE_ID'])
                        )

                        if update_success:
                            history_success = execute_query(
                                """
                                INSERT INTO CASE_ASSIGNMENT_HISTORY
                                (CASE_ID, ASSIGNED_FROM, ASSIGNED_TO, ASSIGNMENT_REASON, STATUS)
                                VALUES (:1, NULL, :2, :3, 'Active')
                                """,
                                (case['CASE_ID'], officer_id, reason)
                            )

                            if history_success:
                                # show message
                                msg = st.empty()
                                msg.success(f"✅ CASE {case['CASE_ID']} ASSIGNED TO {selected_officer}")

                                time.sleep(3)

                                # clear message
                                msg.empty()

                                # ❌ clear search bar
                                st.session_state.pop("case_search", None)


                                # 🔁 refresh screen
                                st.rerun()

                            else:
                                st.error("❌ Failed to record assignment history")

                        else:
                            st.error("❌ Failed to update case assignment")

                    except Exception as e:
                        st.error(f"❌ ASSIGNMENT FAILED: {str(e)}")

    except Exception as e:
        st.error(f"❌ ERROR FETCHING CASES: {str(e)}")
