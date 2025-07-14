import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import date

# -----------------------
# SQLAlchemy DB Connection
# -----------------------
DB_URL = "mysql+pymysql://root:@localhost/zatigwera"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# -----------------------
# Password Utilities
# -----------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# -----------------------
# User Operations
# -----------------------
def username_exists(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM users WHERE username = :username"), {"username": username})
        return result.fetchone() is not None

def get_user(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
        row = result.mappings().first()
        return dict(row) if row else None

def register_user(data):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO users (full_name, username, password_hash, role, village, date_of_birth, gender)
            VALUES (:full_name, :username, :password_hash, :role, :village, :dob, :gender)
        """), {
            "full_name": data[0], "username": data[1], "password_hash": data[2],
            "role": data[3], "village": data[4], "dob": data[5], "gender": data[6]
        })

# -----------------------
# Funeral Logging
# -----------------------
def log_funeral(data):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO funerals (full_name, age, gender, village, date_of_birth, date_of_death, cause_of_death, reported_by)
            VALUES (:full_name, :age, :gender, :village, :dob, :dod, :cod, :reporter)
        """), {
            "full_name": data[0], "age": data[1], "gender": data[2], "village": data[3],
            "dob": data[4], "dod": data[5], "cod": data[6], "reporter": data[7]
        })

# -----------------------
# Age Calculation
# -----------------------
def calculate_age_at_death(dob, dod):
    return max(0, dod.year - dob.year - ((dod.month, dod.day) < (dob.month, dob.day)))

# -----------------------
# Dashboards
# -----------------------
def admin_dashboard(user):
    st.sidebar.title("⚙️ Admin Menu")
    action = st.sidebar.radio("Admin Options", ["➕ Add User", "📊 Statistics", "📁 All Funeral Records"])

    if action == "➕ Add User":
        st.subheader("Register New User")
        with st.form("add_user_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            village = st.text_input("Village")
            dob = st.date_input("Date of Birth", max_value=date.today())
            gender = st.selectbox("Gender", ["Male", "Female"])
            role = st.selectbox("Role", ["reporter", "admin"])
            submit = st.form_submit_button("Register")

        if submit:
            if password != confirm_password:
                st.error("Passwords do not match.")
            elif username_exists(username):
                st.warning("Username already exists. Try another.")
            else:
                register_user((full_name, username, hash_password(password), role, village, dob, gender))
                st.success(f"🎉 User '{username}' registered successfully!")

    elif action == "📊 Statistics":
        st.subheader("Funeral Stats Dashboard")
        df = pd.read_sql("SELECT * FROM funerals", engine)

        if not df.empty:
            st.metric("Total Records", len(df))
            st.dataframe(df)

            st.subheader("Gender Distribution")
            chart = df['gender'].value_counts().reset_index()
            chart.columns = ['Gender', 'Count']
            fig, ax = plt.subplots()
            sns.barplot(data=chart, x="Gender", y="Count", ax=ax)
            st.pyplot(fig)

    elif action == "📁 All Funeral Records":
        st.subheader("Browse All Funerals")
        df = pd.read_sql("""
            SELECT f.*, u.full_name AS reporter 
            FROM funerals f 
            LEFT JOIN users u ON f.reported_by = u.id
        """, engine)

        keyword = st.text_input("🔍 Search name or village")
        if keyword:
            df = df[df['full_name'].str.contains(keyword, case=False) | df['village'].str.contains(keyword, case=False)]

        st.dataframe(df)

        if not df.empty:
            st.download_button("📥 Download CSV", data=df.to_csv(index=False).encode(), file_name="funerals.csv")
            excel_buf = BytesIO()
            df.to_excel(excel_buf, index=False)
            excel_buf.seek(0)
            st.download_button("📥 Download Excel", data=excel_buf, file_name="funerals.xlsx")

            fig, ax = plt.subplots()
            df['gender'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
            ax.set_ylabel('')
            st.pyplot(fig)

def reporter_dashboard(user):
    st.sidebar.title("📝 Reporter Menu")
    action = st.sidebar.radio("Options", ["🏠 Dashboard", "➕ Log Funeral", "📁 My Records"])

    if action == "🏠 Dashboard":
        st.markdown(f"### Welcome, {user['full_name']}")
        df = pd.read_sql(f"SELECT * FROM funerals WHERE reported_by = {user['id']}", engine)
        st.metric("Records Submitted", len(df))

        if not df.empty:
            st.subheader("Gender Breakdown")
            chart = df['gender'].value_counts().reset_index()
            chart.columns = ['Gender', 'Count']
            fig, ax = plt.subplots()
            sns.barplot(data=chart, x="Gender", y="Count", ax=ax)
            st.pyplot(fig)

    elif action == "➕ Log Funeral":
        st.subheader("New Funeral Entry")
        with st.form("funeral_form"):
            full_name = st.text_input("Deceased Full Name")
            gender = st.selectbox("Gender", ["Male", "Female"])
            village = st.text_input("Village")
            cause_of_death = st.text_area("Cause of Death")
            dob = st.date_input("Date of Birth", max_value=date.today())
            dod = st.date_input("Date of Death", max_value=date.today())
            age = calculate_age_at_death(dob, dod)
            st.text_input("Age at Death", str(age), disabled=True)
            submit = st.form_submit_button("Submit")

        if submit:
            log_funeral((full_name, age, gender, village, dob, dod, cause_of_death, user['id']))
            st.success(f"✅ Funeral for {full_name} logged.")

    elif action == "📁 My Records":
        df = pd.read_sql(f"SELECT * FROM funerals WHERE reported_by = {user['id']}", engine)

        search = st.text_input("Search your funerals")
        if search:
            df = df[df['full_name'].str.contains(search, case=False) | df['village'].str.contains(search, case=False)]

        st.dataframe(df)

        if not df.empty:
            csv = df.to_csv(index=False).encode()
            excel_buf = BytesIO()
            df.to_excel(excel_buf, index=False)
            excel_buf.seek(0)
            st.download_button("📥 CSV", data=csv, file_name="my_funerals.csv")
            st.download_button("📥 Excel", data=excel_buf, file_name="my_funerals.xlsx")

# -----------------------
# App Entry Point
# -----------------------
def main():
    st.set_page_config("Zatigwera Funeral System", layout="centered")
    st.title("⚰️ Zatigwera - Funeral Management System")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    if not st.session_state.logged_in:
        st.subheader("🔐 Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Login")

        if login:
            user = get_user(username)
            if user and verify_password(password, user["password_hash"]):
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        user = st.session_state.user
        st.sidebar.success(f"Logged in as {user['full_name']} ({user['role']})")

        if user["role"] == "admin":
            admin_dashboard(user)
        elif user["role"] == "reporter":
            reporter_dashboard(user)

        if st.sidebar.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

if __name__ == "__main__":
    main()
