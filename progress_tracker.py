"""
progress_tracker.py — Student personal development & learning progress tracker

ENHANCEMENTS:
  - Expanded skill areas include programming & CS subjects
  - Back button
  - CSS variables used throughout
"""

import streamlit as st
import datetime
from collections import defaultdict
from auth import get_current_user
from database import add_progress_entry, get_progress_entries

SKILL_AREAS = [
    # Soft skills
    "Public Speaking", "Confidence", "Communication",
    "Body Language", "Active Listening", "Emotional Intelligence",
    "Leadership", "Time Management", "Networking",
    "Interview Skills", "Presentation Skills", "Assertiveness",
    # Programming & CS (new)
    "C Programming", "C++", "Java", "Python", "JavaScript",
    "Data Structures", "Algorithms", "Web Development",
    "Database Management", "Problem Solving",
]


def render():
    user = get_current_user()

    if st.button("← Back to Dashboard", key="back_progress"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="tl-header">
        <h1>📈 Progress Tracker</h1>
        <p>Log and visualize your learning journey across all subjects.</p>
    </div>
    """, unsafe_allow_html=True)

    entries = get_progress_entries(user["id"])

    col_form, col_chart = st.columns([1, 2])

    # ── Log New Entry ──
    with col_form:
        st.markdown("### ✏️ Log Today's Progress")

        skill = st.selectbox("Skill / Subject Area", SKILL_AREAS, key="prog_skill")
        score = st.slider("Self-Rating (1=Struggling · 10=Excellent)", 1, 10, 5, key="prog_score")

        color = "var(--success)" if score >= 7 else "var(--warning)" if score >= 4 else "var(--danger)"
        emoji = "😊" if score >= 7 else "😐" if score >= 4 else "😔"
        st.markdown(f"""
        <div style="text-align:center; margin:0.5rem 0;">
            <span style="font-size:2rem;">{emoji}</span>
            <div style="background:rgba(255,255,255,0.07); border-radius:999px; height:8px; margin-top:0.5rem; overflow:hidden;">
                <div style="background:{color}; width:{score*10}%; height:100%; border-radius:999px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        note = st.text_area(
            "Reflection / Note",
            placeholder="What did you practice today? What went well?",
            height=80, key="prog_note"
        )
        entry_date = st.date_input("Date", value=datetime.date.today(), key="prog_date")

        if st.button("📝 Save Entry", use_container_width=True):
            add_progress_entry(
                student_id=user["id"],
                skill_area=skill,
                score=score,
                note=note,
                entry_date=str(entry_date)
            )
            st.success("✅ Progress logged!")
            st.rerun()

    # ── Progress Visualization ──
    with col_chart:
        st.markdown("### 📊 Your Progress Overview")
        if not entries:
            st.markdown("""
            <div class="tl-card" style="text-align:center; padding:3rem;">
                <div style="font-size:2.5rem;">📭</div>
                <div style="color:var(--text-muted);">No entries yet. Start logging your progress!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            skill_data = defaultdict(list)
            for e in entries:
                skill_data[e["skill_area"]].append(e["score"])
            avg_scores = {k: sum(v) / len(v) for k, v in skill_data.items()}
            sorted_skills = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)

            st.markdown("**Average Scores by Skill / Subject**")
            for skill_name, avg in sorted_skills:
                bar_color = "var(--success)" if avg >= 7 else "var(--warning)" if avg >= 4 else "var(--danger)"
                st.markdown(f"""
                <div style="margin-bottom:0.75rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:3px;">
                        <span style="color:var(--text);">{skill_name}</span>
                        <span style="color:{bar_color}; font-weight:700;">{avg:.1f}/10</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.07); border-radius:999px; height:8px; overflow:hidden;">
                        <div style="background:{bar_color}; width:{avg*10}%; height:100%; border-radius:999px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Recent Entries ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Recent Entries")
    if entries:
        for entry in entries[:10]:
            score = entry["score"]
            col = "var(--success)" if score >= 7 else "var(--warning)" if score >= 4 else "var(--danger)"
            em  = "😊" if score >= 7 else "😐" if score >= 4 else "😔"
            st.markdown(f"""
            <div class="tl-card" style="padding:1rem 1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                    <div>
                        <span style="font-weight:700; color:var(--text);">{entry['skill_area']}</span>
                        <span style="color:var(--text-muted); font-size:0.8rem; margin-left:0.75rem;">📅 {entry['entry_date']}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span>{em}</span>
                        <span style="font-size:1.2rem; font-weight:800; color:{col};">{score}</span>
                        <span style="color:var(--text-muted); font-size:0.75rem;">/10</span>
                    </div>
                </div>
                {f'<div style="color:var(--text-muted); font-size:0.85rem; margin-top:0.4rem;">💬 {entry["note"]}</div>' if entry.get("note") else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No entries to show yet.")
