import streamlit as st
from streamlit_option_menu import option_menu

# Module imports
from modules import (
    complaint_registration,
    case_assignment,
    investigation,
    case_closure,
    reports,
    evidence_upload,
    Report
)

import utils.session_state as session_state

# Page Configuration
st.set_page_config(
    page_title="Crime Record Management System",
    layout="wide",
    page_icon="🛡️"
)

# Initialize session
session_state.init_session_state()

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        "🛡️ CRIME RECORD SYSTEM",
        ["Home", "Complaint Registration", "Case Assignment", "Investigation", "Case Closure", "Reports", "Evidence Upload", "Crime Analytics"],
        icons=["house", "pencil", "person-badge", "search", "check2-circle", "file-earmark", "upload", "bar-chart"],
        menu_icon="list-task",
        default_index=0,
    )

# ---------------- HOME PAGE ---------------- #

def home_page():
    st.title("🏠 Crime Record Management Dashboard")
    st.write("Welcome to the centralized system for crime tracking, investigation, case management and reporting.")

    st.subheader("📈 System Overview")

    st.info("""
    This platform allows law enforcement to:
    - Register complaints efficiently
    - Assign investigators
    - Track case progress
    - Upload digital evidence
    - Generate analytical reports
    """)


# ---------------- ROUTING ---------------- #

# Helper function to swap pages from buttons
if not hasattr(session_state, "change_page"):
    def change_page(page):
        session_state.selected = page
    session_state.change_page = change_page

# Routing logic
if selected == "Home":
    home_page()
elif selected == "Complaint Registration":
    complaint_registration.app()
elif selected == "Case Assignment":
    case_assignment.app()
elif selected == "Investigation":
    investigation.app()
elif selected == "Case Closure":
    case_closure.app()
elif selected == "Reports":
    reports.app()
elif selected == "Evidence Upload":
    evidence_upload.app()
elif selected == "Crime Analytics":
    Report.app()
