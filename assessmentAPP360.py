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
logo = Image.open("logo.png")# Make sure the file name is correct
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
    2. Reflect on capability of self and of the individual you are assessing before responding.   
    3. The assessment responses will be confidential and will be used for developmental purposes only.  
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
        "Minimally Competent ": 1,
        "Partially Competent": 2,
        "Effectively Competent": 3,
        "Highly Competent": 4,
        "Mastery Competent": 5
    }

def get_definitions():
    return {
        "Predictive Maintenance": {
            "Minimally Competent": "Seems to have basic awareness of predictive maintenance principles and is able to follow instructions to collect data but seems to need significant support to analyse or interpret it. Furthermore, it looks like they have limited use of early warning indicators.",
            "Partially Competent": "Seems not to understand predictive maintenance concepts and seems like the individual relies entirely on reactive or routine maintenance and not able to interpret equipment data or use monitoring tools.",
            "Effectively Competent": "It looks like they understand key equipment, health indicators and uses data to anticipate failures. They seem to apply standard monitoring techniques with moderate accuracy. It seems they can suggest and implement basic preventative actions.",
            "Highly Competent": "They seem to proactively use data analytics and monitoring tools to accurately predict equipment failures. It looks like they could adjust maintenance strategies based on trend analysis and drives equipment reliability improvements.",
            "Mastery Competent": "Seems to demonstrate expert-level skill in designing and implementing predictive maintenance systems. It looks like they could leverage advanced technologies (e.g., AI, machine learning, IoT) to optimise performance, reduce downtime, and create predictive models. It seems they have the ability to coach others and lead innovation in maintenance practices."
        },
        "Trouble Shooting": {
            "Minimally Competent": "It looks like they can follow basic procedures or instructions to identify and resolve common problems. Seems to need guidance for complex or unfamiliar issues and may overlook underlying causes.",
            "Partially Competent": "Seems to struggle to recognize the root causes of problems, and it looks like they rely heavily on others for direction and solutions. Seem to lack a systematic approach to resolving issues.",
            "Effectively Competent": "It seems they can systematically identify root causes and applies appropriate solutions using tools, data, and experience. It looks like they can resolve routine and moderately complex problems with limited support.",
            "Highly Competent": "It looks like they can efficiently troubleshoot complex or unfamiliar issues and anticipates potential problems and implements preventative measures. They seem to be able share knowledge and improve troubleshooting practices across teams.",
            "Mastery Competent": "They seem to demonstrate expert-level skill in diagnosing and resolving critical, high-impact problems quickly. It looks like they could develop troubleshooting protocols, trains others, and lead systemic improvements across the organization."
        },
        "Value Add Management": {
            "Minimally Competent": "They seem to understand the basic concept of value addition and seem to occasionally identify opportunities to improve processes or eliminate inefficiencies but requires direction to implement changes.",
            "Partially Competent": "It looks like they lack awareness of what constitutes value-adding activities and seems like they perform tasks without considering impact or contribution to organizational goals. They seem like they rarely question the effectiveness of current processes.",
            "Effectively Competent": "They seem to consistently identify and contribute to initiatives that enhance organizational value. It looks like they use data and stakeholder input to assess and improve processes with measurable outcomes and seems to align efforts with business goals.",
            "Highly Competent": "They seem to strategically drive value-adding initiatives across teams or departments. They seem to use performance metrics, customer insights, and best practices to enhance organizational effectiveness. It looks like they promote a culture of continuous improvement.",
            "Mastery Competent": "They seem to be transformational leading in value creation. It looks like they are able to design and implement high-impact strategies that significantly improve performance and competitive advantage. They seem to be able to build systems and frameworks for sustainable value generation and mentors others in value-focused thinking."
        },
        "Business Acumen": {
            "Minimally Competent": "The individual seems able to apply basic business knowledge in familiar contexts. They seem to recognize simple trends, can interpret routine financial or operational data, and sometimes link their work to organizational goals, but it looks like they may need support for complex decisions.",
            "Partially Competent": "The individual seems to have limited skill in understanding how the organization and its environment function. They seem to rely on instructions and have difficulty connecting daily tasks to broader business objectives.",
            "Effectively Competent": "The individual seems skilled at understanding business operations, financial drivers, and industry trends. They seem to use this knowledge to make informed decisions, identify opportunities, and contribute to achieving organizational objectives.",
            "Highly Competent": "The individual seems highly skilled at applying business insight to complex or ambiguous situations. They anticipate challenges, analyse trends, and provide recommendations that enhance efficiency, competitiveness, and strategic outcomes.",
            "Mastery Competent": "The individual seems to have mastered business acumen. They seem to be able to consistently translate deep understanding of business, markets, and strategy into decisions that shape organizational direction. They seem to be able to mentor others, influence strategic priorities, and drive sustainable growth."
        },
        "Decision Quality": {
            "Minimally Competent": "The individual seems able to make decisions in familiar situations using basic analysis. They seem to consider some risks and benefits, but it looks like they may seek reassurance or delay action in complex circumstances.",
            "Partially Competent": "The individual seems to have limited decision-making skill. They seem to rely heavily on guidance, follow standard procedures, and often defer or delay decisions when faced with ambiguity.",
            "Effectively Competent": "The individual seems skilled at making timely, well-informed decisions. They seem to be able to evaluate options, consider risks, and take accountability for choices that align with organizational objectives.",
            "Highly Competent": "The individual seems highly skilled at making decisions in complex or ambiguous situations. They seem to be able to integrate diverse perspectives, anticipate consequences, and adapt decisions as needed, influencing outcomes positively.",
            "Mastery Competent": "The individual seems to have mastered decision quality. They seem to make high-impact decisions that shape organizational strategy, navigate uncertainty with confidence, and seem to be able to mentor others to strengthen decision-making capabilities."
        },
        "Conceptual Thinking": {
            "Minimally Competent": "The individual seems able to recognize simple patterns and relationships but looks like they may require guidance to apply insights to problem-solving or decision-making.",
            "Partially Competent": "The individual seems to grasp basic ideas but struggles to see connections between them. It looks like their thinking is primarily concrete and task focused.",
            "Effectively Competent": "The individual seems skilled at identifying trends, linking ideas, and using insights to solve problems and improve outcomes. They seem to think beyond immediate tasks to broader implications.",
            "Highly Competent": "The individual seems highly skilled at synthesizing complex information and spotting underlying patterns. They seem to be able to anticipate consequences, generate innovative solutions, and influence strategy.",
            "Mastery Competent": "The individual seems to have mastered conceptual thinking. They seem to consistently translate abstract ideas into strategic initiatives, guide organizational direction, and it looks like they are able to mentor others in developing deep analytical and conceptual skills."
        },
        "Managing Uncertainty": {
            "Minimally Competent": "The individual seems able to cope with minor ambiguity and change but it looks like they may need reassurance in complex or rapidly evolving situations. Their skill in managing uncertainty and adaptability seem to be emerging.",
            "Partially Competent": "The individual seems uncomfortable with uncertainty. They seem to rely on instructions and struggle to act when situations are ambiguous or rapidly changing.",
            "Effectively Competent": "The individual seems skilled at remaining focused and effective despite uncertainty. They seem able to adapt plans, manage risks, and make informed decisions under changing conditions.",
            "Highly Competent": "The individual seems highly skilled at navigating uncertainty. They seem able to anticipate challenges, adjust strategies quickly, and looks like is able to help others stay productive and resilient during unpredictable circumstances.",
            "Mastery Competent": "The individual seems to have mastered managing uncertainty. They seem to thrive in ambiguous environments, make proactive decisions, guide teams through complexity, and foster organizational resilience and adaptability."
        },
        "Innovation Enablement": {
            "Minimally Competent": "The individual seems to have emerging skill in fostering innovation. They seem to be able to occasionally support latest ideas or improvements, recognize creative efforts, and show some willingness to experiment. However, it looks like they may need guidance to consistently create an environment where innovation thrives.",
            "Partially Competent": "The individual seems to have limited skill in enabling innovation. They seem to tend to follow established processes, rarely challenge the status quo, and do not actively support latest ideas or creative approaches. It looks like learning from mistakes is minimal, and experimentation is seldom done by them.",
            "Effectively Competent": "The individual seems skilled at enabling innovation. They seem to be able to actively encourage team members to generate ideas, support experimentation, and integrate lessons from both successes and failures. They seem to be able to contribute to continuous improvement initiatives and help turn creative ideas into practical solutions.",
            "Highly Competent": "The individual seems highly skilled in creating a culture of innovation. They seem to proactively remove barriers to creativity, recognize, and reward contributions, and integrate innovative approaches into processes, products, or services. It looks like team members and others look to them for guidance on innovative problem-solving and improvement opportunities.",
            "Mastery Competent": "The individual seems to have mastered innovation enablement. They seem to be able to consistently cultivate an environment that inspires creativity across the organization, drive breakthrough solutions, and embed innovation as a core strategic capability. They seem to be able to coach and mentor others to think creatively, challenge conventional approaches, and apply innovative thinking to achieve organizational growth and competitive advantage."
        },
        "Strategic Agility": {
            "Minimally Competent": "The individual seems able to recognize emerging trends or changes in familiar contexts. They seem to occasionally adapt plans and make decisions in response to latest information, but it looks like they may need guidance for complex or high-impact situations.",
            "Partially Competent": "The individual seems to have limited skill in strategic agility. They seem to focus mainly on immediate tasks, react slowly to change, and struggle to see how current actions impact broader organizational objectives.",
            "Effectively Competent": "The individual seems skilled at anticipating market shifts and adjusting actions accordingly. They seem to respond effectively to emerging opportunities or threats, align decisions with strategy, and maintain focus on organizational objectives.",
            "Highly Competent": "The individual seems highly skilled in strategic agility. They seem to proactively anticipate changes in the environment, adjust strategies quickly, and guide teams in navigating complex or uncertain circumstances. Their actions looks like they consistently support organizational adaptability and growth.",
            "Mastery Competent": "The individual seems to have mastered strategic agility. They seem able to shape organizational strategy by foreseeing trends and opportunities, inspire others to act decisively in dynamic environments, and ensure the organization remains resilient, adaptive, and positioned for long-term success."
        },
        "Root Cause Analysis (RCA)": {
            "Minimally Competent": "The individual seems able to identify basic causes of problems in familiar situations. They seem able to gather relevant information and recognize patterns, but it looks like they may overlook deeper or less obvious contributing factors.",
            "Partially Competent": "The individual seems to have limited skill in identifying root causes. They seem to often focus on surface-level symptoms rather than investigating underlying issues, and it looks like they rely heavily on guidance or established solutions.",
            "Effectively Competent": "The individual seems skilled at analysing issues to identify underlying causes. They are able to use structured methods, collect and interpret relevant data, and recommend solutions that address the source of problems rather than just symptoms.",
            "Highly Competent": "The individual seems highly skilled in root cause analysis. They seem able to investigate complex or ambiguous issues, integrate multiple data sources, anticipate potential consequences, and develop robust solutions that prevent recurrence and improve organizational performance.",
            "Mastery Competent": "The individual seems to have mastered root cause analysis. They seem able to consistently identify systemic or strategic causes of problems, implement preventative measures across the organization, and it looks like they are able to coach others in using RCA to drive continuous improvement and operational excellence."
        },
        "Instrumentation and Control Systems": {
            "Minimally Competent": "The individual seems able to operate and maintain instrumentation and control systems in familiar contexts. They seem able to interpret common readings, perform routine adjustments, and identify minor faults, but may need guidance for complex issues.",
            "Partially Competent": "The individual seems to have limited skill with instrumentation and control systems. They seem able to follow basic instructions to operate or monitor equipment but struggle to interpret system data or troubleshoot problems independently.",
            "Effectively Competent": "The individual seems skilled at operating, maintaining, and troubleshooting instrumentation and control systems. They seem able to analyse system performance, adjust optimize processes, and respond to deviations with minimal supervision.",
            "Highly Competent": "The individual seems highly skilled in instrumentation and control systems. They seem to be able to integrate knowledge of system design, process requirements, and operational data to optimize performance, solve complex problems, and improve system reliability and safety.",
            "Mastery Competent": "The individual seems to have mastered instrumentation and control systems. They seem able to  lead in designing, implementing, and improving advanced control systems, guide others in troubleshooting and optimization, and ensure systems contribute to high performance, safety, and operational excellence."
        },
        "Project Engineering": {
            "Minimally Competent": "The individual seems able to contribute to engineering projects in familiar contexts. They seem able to follow plans, support coordination, and perform routine calculations or assessments but it looks like they would require supervision for complex decisions or project management tasks.",
            "Partially Competent": "The individual seems to have limited skill in project engineering. They seem able to assist with tasks under guidance but struggle to understand project requirements, schedules, or technical documentation independently.",
            "Effectively Competent": "The individual seems skilled in managing engineering projects. They seem able to plan, coordinate, and monitor project activities, ensure technical requirements are met, and identify risks or issues, taking corrective actions as needed.",
            "Highly Competent": "The individual seems highly skilled in project engineering. They seem able to lead complex projects, integrate multiple engineering disciplines, optimize resources, anticipate technical and logistical challenges, and ensure projects are delivered efficiently and safely.",
            "Mastery Competent": "The individual seems to have mastered project engineering. They seem able to consistently lead high-impact projects, develop innovative solutions to engineering challenges, mentor others in project management and technical execution, and ensure projects align with organizational strategy and objectives."
        },
        "Lean Manufacturing / Six Sigma": {
            "Minimally Competent": "The individual seems able to contribute to process improvement initiatives in familiar contexts. They seem able to identify obvious waste, support basic data collection and analysis, and follow established improvement tools, but it; looks like they would need support for more complex projects.",
            "Partially Competent": "The individual seems to have limited skill in Lean or Six Sigma. They seem able to understand basic concepts but rely on guidance to participate in process improvement activities and seldom apply structured problem-solving methods.",
            "Effectively Competent": "The individual seems skilled in applying Lean and Six Sigma principles. They seem able to lead improvement projects, analyse processes, identify root causes of inefficiencies, implement corrective actions, and track measurable results.",
            "Highly Competent": "The individual seems highly skilled in Lean and Six Sigma. They seem able to integrate methodology with strategic goals, optimize complex processes, mentor others in improvement techniques, and consistently deliver measurable efficiency, quality, and performance improvements.",
            "Mastery Competent": "The individual seems to have mastered Lean Manufacturing and Six Sigma. They seem able to design and implement enterprise-wide improvement initiatives, create a culture of continuous improvement, coach teams at all levels, and drive innovation and operational excellence across the organization."
        },
        "Technical Documentation and Reporting": {
            "Minimally Competent": "The individual seems able to produce routine technical documents and reports. They seem able to follow templates, capture key data, and communicate information adequately, but it looks like they may miss critical details or context in more complex situations.",
            "Partially Competent": "The individual seems to have limited skill in technical documentation and reporting. They seem able to record basic information but often produce incomplete or unclear reports and it looks like they would require guidance to meet standards.",
            "Effectively Competent": "The individual seems skilled at producing clear, accurate, and well-structured technical documents and reports. They seem to summarize findings effectively, ensure completeness, and provide information that supports operational and project decisions.",
            "Highly Competent": "The individual seems highly skilled in technical documentation and reporting. They seem to create comprehensive, precise, and actionable reports, tailor information for different audiences, and use documentation to drive efficiency, compliance, and informed decision-making.",
            "Mastery Competent": "The individual seems to have mastered technical documentation and reporting. They seem able to establish best practices, standardize documentation processes across teams or departments, ensure knowledge transfer, and seem able to coach others in producing high-quality, impactful technical reports."
        },
        "Data Analysis and Interpretation": {
            "Minimally Competent": "The individual seems able to perform basic data analysis and identify simple trends. They seem able to support decision-making in familiar contexts, but it looks like they may require guidance for complex datasets or advanced interpretation.",
            "Partially Competent": "The individual seems to have limited skill in data analysis. They seem able to collect and organize basic data, but it looks like they may struggle to interpret it meaningfully or draw actionable conclusions.",
            "Effectively Competent": "The individual seems skilled at analysing and interpreting data. They seem able to identify patterns, correlations, and trends, summarize findings clearly, and provide actionable insights to support operational or strategic decisions.",
            "Highly Competent": "The individual seems highly skilled in data analysis and interpretation. They seem able to handle complex datasets, integrate multiple sources of information, apply advanced analytical techniques, and deliver insights that guide process improvements, strategy, or innovation.",
            "Mastery Competent": "The individual seems to have mastered data analysis and interpretation. They seem able to shape organizational decision-making by leveraging advanced analytics, anticipate trends and risks, mentor others in analytical thinking, and ensure data-driven strategies are consistently applied across the organization."
        },
        "Business Intelligence (BI) and Reporting Tools": {
            "Minimally Competent": "The individual seems able to use BI tools for routine reporting and basic analysis. They seem able to generate standard reports, filter data, and identify simple trends, but it looks like they may require guidance for advanced features or complex datasets.",
            "Partially Competent": "The individual seems to have limited skill in using BI or reporting tools. They seem able to access basic dashboards or reports, but it looks like they struggle to manipulate data, generate insights, or create meaningful visualizations independently.",
            "Effectively Competent": "The individual seems skilled at using BI and reporting tools. They seem able to design reports and dashboards, analyse data from multiple sources, and present insights that support operational or strategic decision-making.",
            "Highly Competent": "The individual seems highly skilled in BI and reporting. They seem able to integrate data from diverse systems, create advanced visualizations, perform predictive or trend analyses, and deliver actionable insights to influence business outcomes.",
            "Mastery Competent": "The individual seems to have mastered BI and reporting tools. They seem able to define reporting standards, drive data-driven decision-making across the organization, mentor others in tool usage and analysis, and use insights strategically to guide long-term business direction."
        },
        "Financial Modelling": {
            "Minimally Competent": "The individual seems able to build basic financial models for familiar scenarios. They seem able to perform simple calculations, analyses straightforward assumptions, and provide preliminary insights, but it looks like they would require guidance for complex or dynamic situations.",
            "Partially Competent": "The individual seems to have limited skill in financial modelling. They seem able to follow pre-built templates, but it looks like they would struggle to create or adapt models independently and seem likes they may have difficulty interpreting outputs.",
            "Effectively Competent": "The individual seems skilled at creating and using financial models. They seem able to design models for scenario analysis, evaluate risks, forecast financial outcomes, and generate insights that support informed business decisions.",
            "Highly Competent": "The individual seems highly skilled in financial modelling. They seem able to develop sophisticated models that integrate multiple variables, perform sensitivity analyses, and provide strategic recommendations for complex business decisions.",
            "Mastery Competent": "The individual seems to have mastered financial modelling. They seem able to lead the design of enterprise-level models, guide organizational decision-making through scenario planning and predictive analysis, and seem able to mentor others in modelling best practices, and ensure models drive strategic and financial outcomes."
        },
        "Financial Performance Reporting": {
            "Minimally Competent": "The individual seems able to prepare routine financial reports. They seem able to calculate key metrics, highlight basic trends, and provide preliminary analysis, but looks like they would need guidance to identify deeper insights or complex variances.",
            "Partially Competent": "The individual seems to have limited skill in financial performance reporting. They seem able to compile basic financial data but struggle to interpret results, identify key metrics, or communicate insights clearly.",
            "Effectively Competent": "The individual seems skilled at preparing and analysing financial performance reports. They seem able to interpret trends, assess deviations from budgets or forecasts, and communicate findings in a way that informs operational and strategic decisions.",
            "Highly Competent": "The individual seems highly skilled in financial performance reporting. They seem to integrate data from multiple sources, perform comprehensive variance and trend analyses, and provide actionable insights that influence business strategy and operational improvements.",
            "Mastery Competent": "The individual seems to have mastered financial performance reporting. They seem to be able to establish reporting standards and frameworks, ensure timely and accurate reporting across the organization, mentor others, and use reporting to drive strategic decision-making and long-term business performance."
        },
        "IoT Integration": {
            "Minimally Competent": "The individual seems able to support simple IoT integration tasks. They seem able to configure devices, connect sensors, and manage basic data capture, but it looks like they may need guidance to ensure interoperability and security in more complex systems.",
            "Partially Competent": "The individual seems to have limited knowledge of IoT integration. They seem aware of IoT concepts and can follow instructions to connect basic devices but seem to struggle to understand data flows, system interactions, or practical applications.",
            "Effectively Competent": "The individual seems skilled at IoT integration. They seem able to design and implement solutions that connect multiple devices and platforms, ensure data flows are accurate and secure, and provide meaningful insights for operational improvement.",
            "Highly Competent": "The individual seems highly skilled in IoT integration. They seem able to develop complex IoT ecosystems, integrate data across platforms, apply analytics to generate predictive insights, and ensure systems are scalable, secure, and aligned with business needs.",
            "Mastery Competent": "The individual seems to have mastered IoT integration. They seem able to lead enterprise-level IoT strategies, define standards and frameworks for integration, mentor others in IoT solutioning, and use IoT ecosystems to drive digital transformation and strategic advantage."
        },
        "Cybersecurity Protocols in Telecom Environments": {
            "Minimally Competent": "The individual seems able to apply basic cybersecurity protocols in telecom settings. They seem able to follow established security procedures, monitor for simple risks, and respond to routine threats, but it looks like they would require guidance for complex incidents or evolving risks.",
            "Partially Competent": "The individual seems to have limited awareness of cybersecurity in telecom environments. They seem able to understand basic concepts like passwords, firewalls, or data protection but it looks like they struggle to apply protocols in real-world telecom systems.",
            "Effectively Competent": "The individual seems skilled at implementing cybersecurity protocols in telecom environments. They seem able to manage access controls, monitor networks for vulnerabilities, apply encryption, and conduct incident response effectively.",
            "Highly Competent": "The individual seems highly skilled in telecom cybersecurity. They seem able to design and implement advanced security architectures, conduct risk assessments, respond to complex threats, and ensure compliance with industry standards and regulations.",
            "Mastery Competent": "The individual seems to have mastered cybersecurity in telecom environments. They seem able to shape organizational security strategy, establish frameworks and policies, lead incident response teams, mentor others, and ensure that telecom infrastructure is resilient against emerging cyber threats."
        }
    }


def get_general_definitions():
    return {
        "Predictive Maintenance": "The ability to anticipate equipment failures and maintenance needs by analysing data and using advanced monitoring techniques.",
        "Trouble Shooting": "The ability to identify, diagnose, and resolve technical or mechanical problems in systems, machinery, or processes quickly and systematically.",
        "Value Add Management": "The ability to identify, create, and enhance activities, processes, or initiatives that contribute measurable value to the organization.",
        "Business Acumen": "The ability to understand and apply knowledge of business operations, industry trends, financial principles, and strategic drivers to make informed decisions that contribute to organizational success.",
        "Decision Quality": "The ability to make sound, timely, and well-informed decisions based on critical thinking, data analysis, and a clear understanding of the situation.",
        "Conceptual Thinking": "The ability to rely on one’s intelligence in understanding complex situations or problems by identifying patterns, relationships, and underlying principles.",
        "Managing Uncertainty": "The ability to remain effective and focused when faced with unclear, unpredictable, or rapidly changing situations.",
        "Innovation Enablement": "The ability to create and sustain an environment that actively encourages innovative ideas, creative problem-solving, and continuous improvement.",
        "Strategic Agility": "The ability to anticipate and respond quickly to changing business environments, market trends, and emerging opportunities.",
        "Root Cause Analysis (RCA)": "The ability to systematically identify the underlying causes of problems or incidents to prevent recurrence and improve processes, systems, or outcomes.",
        "Instrumentation and Control Systems": "The ability to design, operate, monitor, and maintain instrumentation and control systems to ensure accurate measurement, efficient process control, and safe operation of equipment and processes.",
        "Project Engineering": "The ability to plan, design, coordinate, and oversee engineering projects to ensure they are completed safely, on time, within budget, and meet technical specifications.",
        "Lean Manufacturing / Six Sigma": "The ability to apply Lean and Six Sigma principles to improve processes, reduce waste, enhance efficiency, and ensure consistent quality in products or services.",
        "Technical Documentation and Reporting": "The ability to create, maintain, and communicate accurate, clear, and comprehensive technical documents and reports that support operational, engineering, and project activities.",
        "Data Analysis and Interpretation": "The ability to collect, organize, analyse, and interpret data to generate meaningful insights that support informed decision-making, problem-solving, and strategic planning.",
        "Business Intelligence (BI) and Reporting Tools": "The ability to use business intelligence and reporting tools to collect, analyse, visualize, and present data that supports informed decision-making and strategic planning.",
        "Financial Modelling": "The ability to create structured financial models to analyse business scenarios, forecast outcomes, evaluate risks, and support strategic decision-making.",
        "Financial Performance Reporting": "The ability to prepare, analyse, and communicate financial performance reports that provide accurate insights into organizational performance and support strategic and operational decision-making.",
        "IoT Integration": "The ability to design, implement, and manage the integration of Internet of Things (IoT) devices, systems, and data streams to optimize operations, enhance decision-making, and support digital transformation initiatives.",
        "Cybersecurity Protocols in Telecom Environments": "The ability to design, implement, and manage cybersecurity measures and protocols that protect telecom infrastructure, networks, and data from threats, breaches, and vulnerabilities."
    }


def get_tier(percent):
    if percent <= 25:
        return "Poorly Competent"
    elif 26 <= percent <= 54:
        return "Minimally Competent"
    elif 55 <= percent <= 70:
        return "Effectively Competent"
    elif 71 <= percent <= 89:
        return "Highly Competent"
    else:
        return "Mastery Competent"


def aggregate_scores(df, user_name):
    if 'user_id' not in df.columns:
        return {}

    subset = df[df['user_id'] == user_name]
    competencies = get_competencies()
    results = {}

    MAX_SCORE_PER_COMPETENCY = 15  # 3 raters × 5 max rating

    for comp in competencies:
        if comp in subset.columns:
            scores = subset[comp].dropna().tolist()
            if len(scores) == 3:
                total = sum(scores)
                percent = round((total / MAX_SCORE_PER_COMPETENCY) * 100, 2)
                tier = get_tier(percent)
                results[comp] = (tier, percent)
            else:
                results[comp] = ("Insufficient Data", None)
        else:
            results[comp] = ("Not Rated", None)

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