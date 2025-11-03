import streamlit as st
import tempfile
from filemanager import insert_evidence_record, insert_evidence_file
from db_connection import get_connection, fetch_data

def app():
    st.title("🧾 EVIDENCE UPLOAD PORTAL")

    conn = get_connection()
    if not conn:
        st.error("❌ DATABASE CONNECTION FAILED.")
        return
    
    cases = fetch_data("SELECT CASE_ID, CASE_TITLE FROM CASE_TABLE WHERE STATUS != 'Closed'")
    if not cases:
        st.info("NO OPEN CASES AVAILABLE.")
        return

    case_options = {f"{c['CASE_ID']} - {c['CASE_TITLE']}": c['CASE_ID'] for c in cases}
    selected_case = st.selectbox("SELECT CASE", list(case_options.keys()))

    evidence_type = st.selectbox(
        "EVIDENCE TYPE",
        ["Physical", "Digital", "Document", "Biological", "Photographic", "Video", "Audio", "Other"]
    )

    uploaded_by = st.text_input("OFFICER STAFF ID (UPLOADER)")
    description = st.text_area("DESCRIPTION OF EVIDENCE")

    uploaded_file = st.file_uploader(
        "UPLOAD EVIDENCE FILE",
        type=["jpg", "png", "pdf", "mp4", "wav", "txt", "docx", "JPG", "PNG"]
    )

    if uploaded_file and st.button("SUBMIT EVIDENCE"):

        if not uploaded_by.strip():
            st.error("Uploader Staff ID is required.")
            return

        if not description.strip():
            st.error("Description cannot be empty.")
            return

        try:
            # ✅ First insert parent row
            new_evidence_id = insert_evidence_record(
                connection=conn,
                case_id=case_options[selected_case],
                evidence_type=evidence_type,
                description=description,
                collected_by=uploaded_by,
                storage_location="Pending Processing",
                chain_of_custody="Uploaded into digital vault",
                status="Collected"
            )

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.getbuffer())
                temp_path = tmp.name

            insert_evidence_file(
                connection=conn,
                evidence_id=new_evidence_id,
                filename=uploaded_file.name,
                file_type=uploaded_file.type,
                uploaded_by=uploaded_by,
                description=description,
                file_path=temp_path
            )

            st.success("✅ Uploaded successfully!")

        except Exception as e:
            st.error(f"❌ UPLOAD FAILED: {e}")
