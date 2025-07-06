import streamlit as st
import requests
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="CSV InsightHUB 💼", layout="wide")

# ─── Backend Endpoints ──────────────────────────────────────────
BACKEND = "http://127.0.0.1:8000"
AUTH = "/auth"
UPLOAD_URL = f"{BACKEND}/upload/upload"
CHAT_PREFIX = "/chat"
FILES_URL = f"{BACKEND}{CHAT_PREFIX}/files"
DOWNLOAD_URL = f"{BACKEND}{CHAT_PREFIX}/download"
CHAT_URL = f"{BACKEND}{CHAT_PREFIX}/chat"

# ─── Session Setup ─────────────────────────────────────────────
st.session_state.setdefault("token", "")
st.session_state.setdefault("email", "")
st.session_state.setdefault("files", [])
st.session_state.setdefault("df", None)
st.session_state.setdefault("chosen_file", None)

# ─── Auth Block ────────────────────────────────────────────────
st.title("Welcome to CSV InsightHUB 💬")
st.markdown("Secure HR analytics and conversational insights—powered by your data.")

if not st.session_state.token:
    with st.form("auth_form"):
        mode = st.radio("🔐 Login / Signup", ["Login", "Signup"], horizontal=True)
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button(mode)
    if submit:
        r = requests.post(f"{BACKEND}{AUTH}/{mode.lower()}",
                          json={"email": email, "password": pwd})
        if r.ok:
            st.session_state.token = r.json()["access_token"]
            st.session_state.email = email
            st.success("Login successful. Welcome!")
            st.rerun()  # ✅ Refresh app after login
        else:
            st.error(r.json().get("detail", f"{mode} failed."))
            st.stop()
    else:
        st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ─── Sidebar Navigation ────────────────────────────────────────
st.sidebar.success(f"👤 {st.session_state.email}")
st.sidebar.markdown("## 🧭 Navigation")
page = st.sidebar.radio("", ["📈 Analytics", "🤖 Chatbot"])

# ─── Upload CSV ────────────────────────────────────────────────
with st.sidebar.expander("📤 Upload CSV"):
    uploaded = st.file_uploader("", type=["csv"])
    if uploaded:
        resp = requests.post(
            UPLOAD_URL,
            headers=headers,
            files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")},
        )
        if resp.ok:
            st.success(f"Uploaded: `{uploaded.name}`")
            st.session_state.chosen_file = uploaded.name
            st.session_state.df = pd.read_csv(uploaded)

# ─── Show recent uploads (outside expander) ─────────────────────
rf = requests.get(FILES_URL, headers=headers)
if rf.ok:
    files = sorted(rf.json().get("files", []))[-5:]
    st.session_state.files = files
    if files:
        st.sidebar.markdown("#### 📁 Recently uploaded CSVs")
        st.sidebar.selectbox(
            "Recently uploaded (view only):",
            options=files,
            index=0
        )
    else:
        st.sidebar.info("No recent uploads yet.")
else:
    st.sidebar.warning("⚠️ Could not fetch uploaded file list.")

# ─── Skip auto-loading any CSV ──────────────────────────────────
if not st.session_state.files:
    st.warning("No uploaded CSVs found.")
    st.stop()

# ─── Analytics View ────────────────────────────────────────────
if page == "📈 Analytics":
    st.subheader("📊 HR Dashboard")
    df = st.session_state.df
    if df is not None:
        df.columns = [c.lower().strip() for c in df.columns]
        col1, col2, col3 = st.columns(3)
        if "years_at_company" in df:
            with col1:
                st.metric("⏳ Avg Tenure (yrs)", f"{df['years_at_company'].mean():.1f}")
        if "attrition" in df:
            high = df[df["attrition"].astype(str).str.lower() == "yes"]
            with col2:
                st.metric("⚠️ High Risk", len(high))
        if "promotion_ready" in df:
            promo = df[df["promotion_ready"].astype(str).str.lower() == "yes"]
            with col3:
                st.metric("🚀 Promotion Ready", len(promo))

        st.markdown("---")
        if "department" in df:
            st.bar_chart(df["department"].value_counts())
        if "attrition" in df:
            fig = df["attrition"].astype(str).str.lower().value_counts().plot.pie(
                autopct="%1.1f%%", ylabel="", figsize=(4, 4)).figure
            st.pyplot(fig)

        st.markdown("---")
        show = [c for c in df.columns if c in [
            "employee_id", "name", "department", "attrition",
            "training_hours", "promotion_ready", "leaves_taken"
        ]]
        if show:
            gb = GridOptionsBuilder.from_dataframe(df[show])
            gb.configure_pagination()
            gb.configure_default_column(filterable=True, sortable=True)
            AgGrid(df[show], gridOptions=gb.build(), theme="alpine", height=350)
    else:
        st.info("Upload a file to view analytics.")

# ─── Chatbot View ──────────────────────────────────────────────
else:
    st.subheader("🤖 Ask a question")
    prompt = st.chat_input("Ask something about your uploaded CSV")
    if prompt:
        rp = requests.post(CHAT_URL, headers=headers, json={"message": prompt})
        if not rp.ok:
            st.error("⚠️ Bot error—try again")
        else:
            response_json = rp.json()
            reply = response_json.get("response", "No reply received.")

            # Show chat dialogue
            st.chat_message("user").write(prompt)
            st.chat_message("assistant").write(reply)
