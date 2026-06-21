import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Study Group Finder",
    page_icon="🤝",
    layout="wide"
)

st.title("🤝 Peer Study Group Finder")
st.markdown("Find study partners who match your "
            "subjects, schedule and learning style.")
st.markdown("---")

DATA_FILE = "students.json"

def load_students():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_students(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

SUBJECTS = [
    "Data Structures", "Algorithms", "DBMS",
    "Operating Systems", "Computer Networks",
    "Machine Learning", "Python", "Java",
    "Web Development", "AI", "Mathematics",
    "Statistics", "System Design", "DSA (Competitive)"
]

LEARNING_STYLES = [
    "Visual (diagrams, videos)",
    "Reading/Writing (notes, articles)",
    "Discussion-based (talking through problems)",
    "Practice-based (solving problems together)"
]

TIME_SLOTS = [
    "Early Morning (6-9 AM)",
    "Morning (9-12 PM)",
    "Afternoon (12-4 PM)",
    "Evening (4-8 PM)",
    "Night (8-11 PM)",
    "Late Night (11 PM+)"
]

if 'students' not in st.session_state:
    st.session_state.students = load_students()

# Seed demo data if empty
if not st.session_state.students:
    demo = [
        {'name': 'Ananya Sharma', 'year': '2nd Year',
         'subjects': ['Data Structures', 'Algorithms', 'DSA (Competitive)'],
         'style': 'Practice-based (solving problems together)',
         'time': 'Evening (4-8 PM)', 'goal': 'Crack DSA for placements',
         'bio': 'Prepping for FAANG interviews, love whiteboard problems'},
        {'name': 'Rohan Patel', 'year': '3rd Year',
         'subjects': ['Machine Learning', 'Python', 'Statistics'],
         'style': 'Discussion-based (talking through problems)',
         'time': 'Night (8-11 PM)', 'goal': 'Build ML portfolio',
         'bio': 'Working on Kaggle competitions, want to discuss approaches'},
        {'name': 'Priya Reddy', 'year': '2nd Year',
         'subjects': ['DBMS', 'Operating Systems', 'Computer Networks'],
         'style': 'Visual (diagrams, videos)',
         'time': 'Afternoon (12-4 PM)', 'goal': 'Core CS exam prep',
         'bio': 'Visual learner, like drawing out architectures'},
        {'name': 'Vikram Singh', 'year': '2nd Year',
         'subjects': ['Data Structures', 'Python', 'AI'],
         'style': 'Practice-based (solving problems together)',
         'time': 'Evening (4-8 PM)', 'goal': '365-day coding challenge',
         'bio': 'Building daily ML projects, want accountability partner'},
        {'name': 'Sneha Iyer', 'year': '4th Year',
         'subjects': ['System Design', 'Web Development', 'DBMS'],
         'style': 'Reading/Writing (notes, articles)',
         'time': 'Morning (9-12 PM)', 'goal': 'Interview prep',
         'bio': 'Senior prepping for SDE roles, happy to mentor juniors'},
        {'name': 'Arjun Mehta', 'year': '1st Year',
         'subjects': ['Mathematics', 'Python', 'Data Structures'],
         'style': 'Visual (diagrams, videos)',
         'time': 'Night (8-11 PM)', 'goal': 'Build strong fundamentals',
         'bio': 'New to CS, want patient study partners'},
    ]
    st.session_state.students = demo
    save_students(demo)

def calculate_match_score(student_a, student_b):
    score = 0
    breakdown = {}

    # Subject overlap (most important - 50 points)
    common_subjects = set(student_a['subjects']) & \
        set(student_b['subjects'])
    subject_score = min(
        len(common_subjects) * 15, 50)
    score += subject_score
    breakdown['Subject Match'] = subject_score

    # Time overlap (25 points)
    time_score = 25 if student_a['time'] == \
        student_b['time'] else 0
    score += time_score
    breakdown['Schedule Match'] = time_score

    # Learning style (15 points)
    style_score = 15 if student_a['style'] == \
        student_b['style'] else 5
    score += style_score
    breakdown['Style Match'] = style_score

    # Year proximity (10 points)
    years = ['1st Year', '2nd Year',
             '3rd Year', '4th Year']
    try:
        diff = abs(years.index(student_a['year']) -
                   years.index(student_b['year']))
        year_score = max(10 - diff * 4, 0)
    except:
        year_score = 5
    score += year_score
    breakdown['Year Proximity'] = year_score

    return score, breakdown, common_subjects

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Find Matches",
    "📝 Join / Edit Profile",
    "👥 Browse All Students",
    "📊 Subject Demand"
])

# Tab 1 — Find Matches
with tab1:
    st.markdown("### 🔍 Find Your Study Matches")

    if not st.session_state.students:
        st.info("No students registered yet!")
    else:
        names = [s['name'] for s in
                 st.session_state.students]
        selected_name = st.selectbox(
            "Select your profile:", names)

        me = next(
            s for s in st.session_state.students
            if s['name'] == selected_name)

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### 👤 Your Profile")
            st.markdown(f"**{me['name']}** ({me['year']})")
            st.markdown(f"📚 {', '.join(me['subjects'])}")
            st.markdown(f"🎯 {me['style']}")
            st.markdown(f"⏰ {me['time']}")
            st.markdown(f"💭 {me['goal']}")
            st.caption(me['bio'])

        with col2:
            others = [
                s for s in st.session_state.students
                if s['name'] != selected_name
            ]
            matches = []
            for other in others:
                score, breakdown, common = \
                    calculate_match_score(me, other)
                matches.append({
                    'student': other,
                    'score': score,
                    'breakdown': breakdown,
                    'common': common
                })
            matches.sort(
                key=lambda x: x['score'],
                reverse=True)

            st.markdown("#### 🎯 Best Matches")
            for m in matches[:5]:
                s = m['student']
                pct = min(m['score'], 100)
                color = '#2ecc71' if pct >= 70 \
                    else '#f39c12' if pct >= 40 \
                    else '#95a5a6'

                with st.expander(
                    f"{'🟢' if pct>=70 else '🟡' if pct>=40 else '⚪'} "
                    f"{s['name']} — {pct}% match"
                ):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Year:** {s['year']}")
                        st.markdown(
                            f"**Common subjects:** "
                            f"{', '.join(m['common']) if m['common'] else 'None'}")
                        st.markdown(f"**Style:** {s['style']}")
                        st.markdown(f"**Time:** {s['time']}")
                    with col_b:
                        fig = go.Figure(go.Bar(
                            x=list(m['breakdown'].values()),
                            y=list(m['breakdown'].keys()),
                            orientation='h',
                            marker_color=color
                        ))
                        fig.update_layout(
                            height=200,
                            margin=dict(l=0,r=0,t=10,b=10),
                            template='plotly_white')
                        st.plotly_chart(
                            fig, use_container_width=True)
                    st.caption(f"💭 {s['goal']} — {s['bio']}")

# Tab 2 — Join/Edit
with tab2:
    st.markdown("### 📝 Create or Update Your Profile")

    with st.form("profile_form"):
        name = st.text_input("Full Name:")
        year = st.selectbox(
            "Year:", ['1st Year', '2nd Year',
                      '3rd Year', '4th Year'])
        subjects = st.multiselect(
            "Subjects you want to study:", SUBJECTS)
        style = st.selectbox(
            "Preferred learning style:", LEARNING_STYLES)
        time_slot = st.selectbox(
            "Preferred study time:", TIME_SLOTS)
        goal = st.text_input(
            "Your study goal:",
            placeholder="e.g. Crack DSA for placements")
        bio = st.text_area(
            "Short bio:",
            placeholder="Tell potential study partners about yourself")

        submitted = st.form_submit_button(
            "✅ Save Profile", type="primary")

        if submitted:
            if name.strip() and subjects:
                existing = next(
                    (s for s in st.session_state.students
                     if s['name'] == name), None)
                profile = {
                    'name': name, 'year': year,
                    'subjects': subjects, 'style': style,
                    'time': time_slot, 'goal': goal,
                    'bio': bio
                }
                if existing:
                    idx = st.session_state.students.index(existing)
                    st.session_state.students[idx] = profile
                    st.success("✅ Profile updated!")
                else:
                    st.session_state.students.append(profile)
                    st.success("✅ Profile created!")
                save_students(st.session_state.students)
            else:
                st.warning(
                    "Please enter your name and "
                    "select at least one subject.")

# Tab 3 — Browse
with tab3:
    st.markdown("### 👥 All Registered Students")

    filter_subject = st.selectbox(
        "Filter by subject:",
        ["All"] + SUBJECTS)

    filtered = st.session_state.students
    if filter_subject != "All":
        filtered = [
            s for s in filtered
            if filter_subject in s['subjects']]

    st.markdown(f"**{len(filtered)} students found**")

    for s in filtered:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"**{s['name']}** ({s['year']})")
            st.caption(', '.join(s['subjects']))
        with col2:
            st.markdown(f"⏰ {s['time']}")
            st.caption(s['goal'])
        with col3:
            st.markdown(f"🎯 {s['style'][:15]}...")

# Tab 4 — Subject Demand
with tab4:
    st.markdown("### 📊 Most In-Demand Subjects")

    all_subjects = []
    for s in st.session_state.students:
        all_subjects.extend(s['subjects'])

    if all_subjects:
        demand = pd.Series(all_subjects).value_counts()
        fig = px.bar(
            x=demand.values, y=demand.index,
            orientation='h',
            title='Students Interested per Subject',
            color=demand.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            year_dist = pd.Series(
                [s['year'] for s in st.session_state.students]
            ).value_counts()
            fig2 = px.pie(
                values=year_dist.values,
                names=year_dist.index,
                title='Students by Year')
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            time_dist = pd.Series(
                [s['time'] for s in st.session_state.students]
            ).value_counts()
            fig3 = px.pie(
                values=time_dist.values,
                names=time_dist.index,
                title='Preferred Study Times')
            st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "Peer Study Group Finder | "
    "Match-score based on subjects, time and style"
)