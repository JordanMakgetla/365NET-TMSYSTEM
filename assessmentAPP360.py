import streamlit as st
from datetime import datetime
import pandas as pd
import os
import io
import matplotlib.pyplot as plt
import seaborn as sns
import smtplib
from email.message import EmailMessage
import hashlib


# ------------------------- Custom Styling ----------------------------
st.markdown("""
    <style>
    /* Background */
    .stApp {
        background-color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Titles */
    h1, h2, h3 {
        color: #DE6814 !important;
        font-weight: 600;
    }

    /* Subheaders */
    .stMarkdown p, .stText {
        font-size: 16px !important;
        line-height: 1.6;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background-color: #DE6814;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-size: 16px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }

    div.stButton > button:first-child:hover {
        background-color: #c4560f;
        color: #fff;
    }

    /* Radio buttons */
    .stRadio label {
        font-weight: 500;
        color: #333333;
    }

    /* Selectbox labels */
    .stSelectbox label {
        font-weight: 500;
        color: #333333;
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: #DE6814 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
    }

    .stDownloadButton > button:hover {
        background-color: #c4560f !important;
    }

    /* Success & Warning messages */
    .stAlert {
        border-radius: 8px;
        padding: 0.8em;
    }

    /* Banner Header */
    .banner {
        background-color: #DE6814;
        color: white;
        padding: 1em;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
    }
    .banner h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------- Branded Banner ----------------------------
# ------------------------- Branded Banner ----------------------------
from PIL import Image

# Load logo image from the same folder
logo = Image.open("logo.png")  # Make sure the file name is correct
logo_width = 80  # adjust size as needed

st.markdown("""
<div class="banner" style="background-color:#DE6814; padding: 1em; border-radius:8px; text-align:center;">
    <h1 style="color:white !important; margin:0;">360 Assessment System</h1>
</div>
""", unsafe_allow_html=True)


# Ensure text color is white via CSS (already in your CSS block)
st.markdown("""
<style>
.banner {
    background-color: #DE6814;
    padding: 1em;
    border-radius: 8px;
    text-align: center;
}
.banner h1 {
    color: white !important;
    margin: 0;
    font-size: 26px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# Display the logo above the banner
st.image(logo, width=120)


st.set_page_config(page_title="360 Assessment Tool", layout="centered")

# ------------------------- Page Navigation Setup ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"  # default starting page

# ------------------------- Landing & Consent Pages ----------------------------
if st.session_state.page == "landing":
    st.title("WELCOME TO THE 360 ASSESSMENT")
    st.write("""
    This assessment aims to gather feedback from multiple sources (self, peer and line management) 
    in order to provide a holistic view of an individual's competencies.
    """)
    st.markdown("""
    **Please keep in mind when completing the assessment:**
    1. There is no right or wrong answer, answer as honestly as possible.  
    2. Respond with the first answer that comes to mind.  
    3. Each statement describes a behavior — indicate how much you agree or disagree that the statement reflects typical behavior at work.  
    4. The assessment responses will be confidential and will be used for developmental purposes only.  
    """)
    st.subheader("ESTIMATED COMPLETION TIME: 25-30 MINUTES")

    if st.button("Continue"):
        st.session_state.page = "consent"
        st.rerun()

elif st.session_state.page == "consent":
    st.header("Consent Form")
    st.write("""
    By proceeding with this assessment I acknowledge that I:  
    1. Have read and understood the guidelines.  
    2. Provide voluntary consent to participate in the assessment.  
    3. Understand that the results will be reported in aggregate and used for development purposes.  
    """)

    if st.button("I agree and give consent to participate"):
        st.session_state.page = "login"
        st.rerun()

# ------------------------- Helper Functions ----------------------------
def get_competencies():
    return [
        "Predictive Maintenance", "Value Add Management", "Business Acumen",
        "Decision Quality", "Conceptual Thinking"
    ]

def get_ratings():
    return {
        "Poorly Competent": 1,
        "Minimally Competent": 2,
        "Effectively Competent": 3,
        "Highly Competent": 4,
        "Mastery Competent": 5
    }

def get_definitions():
    return {
        "Predictive Maintenance": {
            "Poorly Competent": "Does not understand predictive maintenance concepts. Relies entirely on reactive or routine maintenance. Unable to interpret equipment data or use monitoring tools.",
            "Minimally Competent": "Has basic awareness of predictive maintenance principles. Can follow instructions to collect data but needs significant support to analyse or interpret it. Limited use of early warning indicators.",
            "Effectively Competent": "Understands key equipment health indicators and uses data to anticipate failures. Applies standard monitoring techniques with moderate accuracy. Can suggest and implement basic preventative actions.",
            "Highly Competent": "Proactively uses data analytics and monitoring tools to accurately predict equipment failures. Adjusts maintenance strategies based on trend analysis and drives equipment reliability improvements.",
            "Mastery Competent": "Demonstrates expert-level skill in designing and implementing predictive maintenance systems. Leverages advanced technologies (e.g., AI, machine learning, IoT) to optimise performance, reduce downtime, and create predictive models. Coaches others and leads innovation in maintenance practices"
        },
        "Value Add Management": {
            "Poorly Competent": "Lacks awareness of what constitutes value-adding activities. Performs tasks without considering impact or contribution to organizational goals. Rarely questions the effectiveness of current processes.",
            "Minimally Competent": "Understands the basic concept of value addition. Occasionally identifies opportunities to improve processes or eliminate inefficiencies but requires direction to implement changes.",
            "Effectively Competent": "Consistently identifies and contributes to initiatives that enhance organizational value. Uses data and stakeholder input to assess and improve processes with measurable outcomes. Aligns efforts with business goals.",
            "Highly Competent": "Strategically drives value-adding initiatives across teams or departments. Uses performance metrics, customer insights, and best practices to enhance organizational effectiveness. Promotes a culture of continuous improvement.",
            "Mastery Competent": "Recognized as a transformational leader in value creation. Designs and implements high-impact strategies that significantly improve performance and competitive advantage. Builds systems and frameworks for sustainable value generation and mentors others in value-focused thinking."
        },
        "Business Acumen": {
            "Poorly Competent": "Lacks understanding of basic business operations, financial principles, and strategic context. Struggles to see how their role contributes to business outcomes. Frequently misinterprets or ignores business priorities.",
            "Minimally Competent": "Has limited understanding of business fundamentals. Occasionally applies basic financial or industry knowledge but inconsistently aligns work with organizational goals. Requires guidance to make business-aligned decisions.",
            "Effectively Competent": "Demonstrates a solid grasp of business operations, industry context, and financial concepts. Applies this knowledge to guide routine decisions. Aligns work with business priorities and contributes to achieving organizational goals.",
            "Highly Competent": "Uses a deep understanding of business drivers and industry dynamics to make informed, value-adding decisions. Consistently aligns work with strategic objectives and contributes to business growth. Recognized as a commercially savvy team member.",
            "Mastery Competent": "Demonstrates exceptional strategic and financial acumen. Anticipates business challenges and proactively recommends or leads initiatives that drive significant value. Influences senior decision-making and mentors others in business thinking."
        },
        "Decision Quality": {
            "Poorly Competent": "Struggles to make decisions, often delays unnecessarily, or makes choices without considering relevant information. Shows limited critical thinking and poor judgment under pressure. Decisions frequently result in negative consequences.",
            "Minimally Competent": "Consistently makes timely, logical decisions using available data and sound judgment. Balances risks and benefits, considers stakeholder impact, and generally achieves positive outcomes. Demonstrates structured thinking.",
            "Effectively Competent": "Consistently makes timely, sound, and informed decisions using strong critical thinking, thorough data analysis, and sound judgment aligned with business strategy.",
            "Highly Competent": "Makes well-reasoned, data-driven decisions in complex or high-pressure situations. Considers short- and long-term impacts and incorporates a wide range of perspectives. Trusted for sound judgment.",
            "Mastery Competent": "Demonstrates exceptional judgment and decisiveness. Anticipates risks, interprets complex data, and makes high-stakes decisions that drive strategic value. Coaches others in decision-making and creates decision-making frameworks for teams."
        },
        "Conceptual Thinking": {
            "Poorly Competent": "Has difficulty understanding complex problems or identifying relevant patterns. Struggles to see the big picture.",
            "Minimally Competent": "Begins to identify patterns or connections in familiar situations but often overlooks broader implications. Tends to rely on straightforward or conventional thinking when faced with complexity.",
            "Effectively Competent": "Understands and interprets complex situations by identifying relationships, trends, and root causes. Thinks beyond the immediate issue and can simplify complexity into understandable concepts.",
            "Highly Competent": "Recognizes patterns and interdependencies in complex and ambiguous situations. Connects abstract ideas to real-world challenges and anticipates potential consequences of actions. Develops logical frameworks for understanding issues.",
            "Mastery Competent": "Demonstrates exceptional ability to deconstruct complexity, uncover core issues, and envision innovative, systems-level solutions. Recognized for strategic, high-level thinking and shaping organizational understanding of complex challenges."
        }
    }

def get_general_definitions():
    return {
        "Predictive Maintenance": "The ability to anticipate equipment failures and maintenance needs by analysing data and using advanced monitoring techniques.",
        "Value Add Management": "The ability to identify, create, and enhance activities, processes, or initiatives that contribute measurable value to the organization.",
        "Business Acumen": "The ability to understand and apply knowledge of business operations, industry trends, financial principles, and strategic drivers to make informed decisions that contribute to organizational success.",
        "Decision Quality": "The ability to make sound, timely, and well-informed decisions based on critical thinking, data analysis, and a clear understanding of the situation.",
        "Conceptual Thinking": "The ability to rely on one’s intelligence in understanding complex situations or problems by identifying patterns, relationships, and underlying principles."
    }

def get_tier(percent):
    if percent < 40:
        return "Poorly Competent"
    elif 40 <= percent < 55:
        return "Minimally Competent"
    elif 55 <= percent < 70:
        return "Effectively Competent"
    elif 70 <= percent < 85:
        return "Highly Competent"
    else:
        return "Mastery Competent"

def aggregate_scores(df, user_name):
    if 'user_id' not in df.columns:
        return {}
    subset = df[df['user_id'] == user_name]
    competencies = get_competencies()
    results = {}
    for comp in competencies:
        scores = subset[comp].tolist()
        if len(scores) == 3:
            total = sum(scores)
            percent = round((total / 15) * 100, 2)

            tier = get_tier(percent)
            results[comp] = (tier, percent)
    return results

def send_confirmation_email(to_email, name):
    try:
        msg = EmailMessage()
        msg['Subject'] = "360 Assessment Confirmation"
        msg['From'] = "makgetlajordan@gmail.com"
        msg['To'] = to_email
        msg.set_content(f"Hi {name},\n\nThank you for completing your self-assessment. Your responses have been saved successfully.\n\nBest regards,\n360 Assessment System")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("makgetlajordan@gmail.com", "your_app_password_here")
            smtp.send_message(msg)
    except Exception as e:
        print(f"Email error: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------------- Admin Account Creation ----------------------------
if st.session_state.page == "login":  # only show after consent
    if 'create_account' not in st.session_state:
        st.session_state.create_account = False

    if st.session_state.create_account:
        st.header("Create Admin Account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            hashed = hash_password(new_password)
            acc_file = "admin_accounts.csv"
            if os.path.exists(acc_file):
                df_acc = pd.read_csv(acc_file)
            else:
                df_acc = pd.DataFrame(columns=["username", "password"])
            if new_username in df_acc['username'].values:
                st.error("Username already exists.")
            else:
                new_row = pd.DataFrame([[new_username, hashed]], columns=["username", "password"])
                new_row.to_csv(acc_file, mode="a", header=not os.path.exists(acc_file), index=False)
                st.success("Account created successfully.")
                st.session_state.create_account = False
    else:
        st.button("Create Admin Account", on_click=lambda: st.session_state.update({'create_account': True}))

    # ------------------------- Login Page ----------------------------
    if 'role' not in st.session_state:
        st.title("360 Assessment Login")
        role = st.radio("Select your role:", ["Self", "Peer", "Line Manager", "Admin Report Viewer"])
        user_name = st.text_input("Enter your full name or username:")
        assessed_user = user_name

        if role == "Peer":
            if os.path.exists("assessments.csv"):
                df = pd.read_csv("assessments.csv")
                candidates = df[df['role'] == 'self']['user_id'].unique().tolist()
                if candidates:
                    assessed_user = st.selectbox("Who are you assessing?", candidates)

        if role == "Admin Report Viewer":
            st.write("Login required")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                acc_file = "admin_accounts.csv"
                if os.path.exists(acc_file):
                    acc_df = pd.read_csv(acc_file)
                    hashed_input = hash_password(password)
                    if ((acc_df['username'] == user_name) & (acc_df['password'] == hashed_input)).any():
                        st.session_state['role'] = role
                        st.session_state['user_name'] = user_name
                        st.session_state['assessed_user'] = None
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.error("No admin accounts found.")
        elif role in ["Self", "Peer", "Line Manager"] and st.button("Continue") and user_name:
            st.session_state["role"] = role
            st.session_state["user_name"] = user_name
            st.session_state["assessed_user"] = assessed_user
            st.rerun()
    else:
        role = st.session_state["role"]
        user_name = st.session_state["user_name"]
        assessed_user = st.session_state["assessed_user"]

        competencies = get_competencies()
        ratings = get_ratings()
        definitions = get_definitions()

        file_path = "assessments.csv"
        if not os.path.exists(file_path):
            pd.DataFrame(columns=["user_id", "timestamp", "role"] + competencies).to_csv(file_path, index=False)

        if role == "Self":
            st.header("Self Assessment")
            email_address = st.text_input("Enter your email address for confirmation:")
            self_scores = {}
            for comp in competencies:
                val = st.selectbox(f"{comp}", ratings.keys(), key=comp+"_self")
                self_scores[comp] = ratings[val]

            if st.button("Submit Self Assessment"):
                df = pd.read_csv(file_path)
                if ((df['user_id'] == user_name) & (df['role'] == 'self')).any():
                    st.warning("Self-assessment already submitted.")
                else:
                    data = {"user_id": user_name, "timestamp": datetime.now(), "role": "self", **self_scores}
                    pd.DataFrame([data]).to_csv(file_path, mode="a", index=False, header=False)
                    if email_address:
                        send_confirmation_email(email_address, user_name)
                    st.success("Self assessment saved. Returning to login...")
                    st.session_state.clear()
                    st.rerun()

        elif role == "Peer":
            st.header(f"Peer Assessment for {assessed_user}")
            peer_scores = {}
            for comp in competencies:
                val = st.selectbox(f"{comp}", ratings.keys(), key=comp+"_peer")
                peer_scores[comp] = ratings[val]

            if st.button("Submit Peer Assessment"):
                df = pd.read_csv(file_path)
                already_rated = ((df['user_id'] == assessed_user) & (df['role'] == 'peer') & (df['timestamp'].astype(str).str.contains(user_name))).any()
                if already_rated:
                    st.warning("You have already rated this person.")
                else:
                    data = {"user_id": assessed_user, "timestamp": f"{datetime.now()}_{user_name}", "role": "peer", **peer_scores}
                    pd.DataFrame([data]).to_csv(file_path, mode="a", index=False, header=False)

                    df = pd.read_csv(file_path)
                    peer_count = df[(df['user_id'] == assessed_user) & (df['role'] == 'peer')].shape[0]
                    if peer_count >= 3:
                        st.success("Peer assessment saved. 3 peer reviews are now complete.")
                        if st.button("Return to Home"):
                            st.session_state.clear()
                            st.rerun()
                    else:
                        st.success("Peer assessment saved. Returning to login...")
                        st.session_state.clear()
                        st.rerun()

        elif role == "Line Manager":
            st.header("Line Manager Assessment")

            if os.path.exists("assessments.csv"):
                df = pd.read_csv("assessments.csv")
                candidates = df[df['role'] == 'self']['user_id'].unique().tolist()
                if candidates:
                    assessed_user = st.selectbox("Select employee to assess:", candidates)

            manager_scores = {}
            for comp in competencies:
                val = st.selectbox(f"{comp}", ratings.keys(), key=comp+"_manager")
                manager_scores[comp] = ratings[val]

            if st.button("Submit Line Manager Assessment"):
                df = pd.read_csv(file_path)
                already_rated = ((df['user_id'] == assessed_user) & (df['role'] == 'manager') & (df['timestamp'].astype(str).str.contains(user_name))).any()
                if already_rated:
                    st.warning("You have already assessed this person.")
                else:
                    data = {"user_id": assessed_user, "timestamp": f"{datetime.now()}_{user_name}", "role": "manager", **manager_scores}
                    pd.DataFrame([data]).to_csv(file_path, mode="a", index=False, header=False)

                    st.success("Line Manager assessment saved. Returning to login...")
                    st.session_state.clear()
                    st.rerun()

        elif role == "Admin Report Viewer":
            st.markdown("---")
            st.subheader("Admin: View Final Reports")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                if 'user_id' in df.columns:
                    names = df[df['role'] == 'self']['user_id'].unique().tolist()
                    selected_name = st.selectbox("Select name for report:", names)
                    final_results = aggregate_scores(df, selected_name)
                    definitions = get_definitions()
                    if final_results:
                        report_data = []
                        for comp, (tier, percent) in final_results.items():
                            st.markdown(f"**{comp}**: {percent}% – **{tier}**")
                            st.write(definitions.get(comp, {}).get(tier, ""))
                            st.markdown("---")
                            report_data.append({
                                "Competency": comp,
                                "Percentage Score": percent,
                                "Tier": tier,
                                "Definition": definitions.get(comp, {}).get(tier, "")
                            })

                        df_report = pd.DataFrame(report_data)
                        st.subheader("Visual Summary")
                        fig, ax = plt.subplots()
                        sns.barplot(x="Percentage Score", y="Competency", data=df_report, hue="Tier", dodge=False, palette="Set2", ax=ax)
                        st.pyplot(fig)

                        csv_buffer = io.StringIO()
                        df_report.to_csv(csv_buffer, index=False)
                        st.download_button("Download Report as CSV", data=csv_buffer.getvalue(), file_name=f"{selected_name}_360_report.csv", mime="text/csv")
                    else:
                        st.warning("Not enough assessments submitted yet.")
                else:
                    st.info("No assessments found.")