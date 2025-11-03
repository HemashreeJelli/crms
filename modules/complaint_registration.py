import streamlit as st
from db_connection import get_connection, execute_query, fetch_data

def app():
    st.title("📝 COMPLAINT REGISTRATION")

    with st.form("COMPLAINT_FORM"):
        COMPLAINANT_ID = st.text_input("COMPLAINANT ID")
        CRIME_TYPE_ID  = st.text_input("CRIME TYPE ID")
        CASE_TITLE     = st.text_input("CASE TITLE")
        DESCRIPTION    = st.text_area("DESCRIPTION")
        INCIDENT_LOCATION = st.text_input("INCIDENT LOCATION")
        STAFFID        = st.text_input("OFFICER STAFF ID (NCO)")
        SUBMIT = st.form_submit_button("REGISTER CASE")

        if SUBMIT:
            if not all([COMPLAINANT_ID, CRIME_TYPE_ID, CASE_TITLE, DESCRIPTION, INCIDENT_LOCATION, STAFFID]):
                st.warning("⚠️ PLEASE FILL IN ALL REQUIRED FIELDS.")
                return

            conn = get_connection()
            if not conn:
                st.error("❌ DATABASE CONNECTION FAILED. PLEASE CHECK YOUR ORACLE CREDENTIALS.")
                return

            try:
                case_id = "C" + __import__("datetime").datetime.now().strftime("%Y%m%d%H%M%S")
                query = """
                    INSERT INTO CASE_TABLE
                    (CASE_ID, COMPLAINANT_ID, CRIME_TYPE_ID, CASE_TITLE,
                    INCIDENT_DATETIME, INCIDENT_LOCATION, DESCRIPTION,
                    NCO_STAFFID, STATUS)
                    VALUES (
                        :0, :1, :2, :3, SYSTIMESTAMP, :4, :5, :6, 'Reported'
                    )
                """
                # Lookup LOCATION_ID using LOCATION_NAME
                loc_query = """
                    SELECT LOCATION_ID FROM LOCATION
                    WHERE LOWER(LOCATION_NAME) = LOWER(:loc)
                """
                loc_result = fetch_data(loc_query, {"loc": INCIDENT_LOCATION})

                if not loc_result:
                    st.error("❌ LOCATION NOT FOUND. Check spelling.")
                    return

                LOCATION_ID = loc_result[0]["LOCATION_ID"]

                success = execute_query(query, (case_id, COMPLAINANT_ID, CRIME_TYPE_ID, CASE_TITLE, LOCATION_ID, DESCRIPTION, STAFFID))

                if success:
                    st.success("✅ CASE REGISTERED SUCCESSFULLY!")
                    st.info(f"🆔 Your Case ID is: **{case_id}**")
                else:
                    st.error("❌ CASE REGISTRATION FAILED.")
            except Exception as e:
                st.error(f"❌ ERROR DURING REGISTRATION: {e}")
