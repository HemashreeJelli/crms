import oracledb
import streamlit as st

# --- Oracle Connection Configuration ---
DB_USER = "police_system"
DB_PASSWORD = "Police123#"  # your password
DB_DSN = "localhost:1521/XEPDB1"  # ✅ connect to correct PDB


# --- 1️⃣ Persistent Connection via Streamlit Session ---
def get_connection():
    """Return a persistent Oracle DB connection stored in Streamlit session."""
    # Check if a connection already exists and is alive
    if "db_conn" in st.session_state:
        try:
            st.session_state.db_conn.ping()  # check if still valid
            return st.session_state.db_conn
        except Exception:
            st.session_state.db_conn = None  # connection dropped — reset

    # If not connected, create a new one
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
        st.session_state.db_conn = conn
        st.session_state.db_cursor = conn.cursor()
        st.toast("✅ Connected to Oracle Database.")  # nicer UI, not repetitive
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.session_state.db_conn = None
        return None


# --- 2️⃣ Safe Query Executor ---
def execute_query(query, params=None):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        st.error(f"❌ Query execution error: {e}")
        return False


# --- 3️⃣ Fetch Data ---
def fetch_data(query, params=None):
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        cols = [col[0] for col in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return rows
    except Exception as e:
        st.error(f"❌ Data fetch error: {e}")
        return []
def check_tables_exist():
    """Check if required tables exist and are accessible"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        # Check what tables are available to the current user
        tables_query = """
        SELECT table_name FROM user_tables 
        WHERE table_name IN (
            'CASE_TABLE', 'COMPLAINANT', 'CRIME_TYPE', 'USERLOGIN',
            'INVESTIGATION', 'CASE_ASSIGNMENT_HISTORY', 'EVIDENCE',
            'SUSPECT', 'WITNESS', 'EVIDENCE_FILE'
        )
        """
        existing_tables = fetch_data(tables_query)
        
        #st.write("📋 **Existing Tables:**")
        #for table in existing_tables:
        #    st.write(f"✅ {table['TABLE_NAME']}")

        required_tables = ['CASE_TABLE', 'COMPLAINANT', 'CRIME_TYPE', 'USERLOGIN']
        missing_tables = []
        
        for table in required_tables:
            if not any(t['TABLE_NAME'] == table for t in existing_tables):
                missing_tables.append(table)
        
        if missing_tables:
            st.error(f"❌ Missing required tables: {', '.join(missing_tables)}")
            return False
            
        return True
        
    except Exception as e:
        st.error(f"❌ Error checking tables: {e}")
        return False
    
if __name__ == "__main__":
    st.title("🚓 Crime Management System - DB Connectivity Test")

    connected = get_connection()

    if connected:
        st.success("✅ Connected to Oracle Database!")
        
        if check_tables_exist():
            st.success("✅ All required tables exist!")
        else:
            st.warning("⚠️ Some required tables are missing.")
    else:
        st.error("❌ Could not connect to database.")
