"""
tutor_profile.py — Tutor creates/edits their profile

ENHANCEMENTS:
  - Expanded ALL_SUBJECTS list (programming languages + CS)
  - Expanded ALL_SPECIALIZATIONS
  - Back button
"""

import streamlit as st
from auth import get_current_user
from database import get_tutor_profile, upsert_tutor_profile, ALL_SUBJECTS, ALL_SPECIALIZATIONS


def render():
    user = get_current_user()
    existing = get_tutor_profile(user["id"])

    if st.button("← Back to Dashboard", key="back_profile"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="tl-header">
        <h1>👤 My Profile</h1>
        <p>Complete your profile so students can discover and book you.</p>
    </div>
    """, unsafe_allow_html=True)

    col_preview, col_form = st.columns([1, 2])

    with col_preview:
        st.markdown("### 👁️ Profile Preview")
        name      = user["full_name"]
        mobile    = user.get("mobile_number", "—")
        spec      = existing.get("specialization", "Your Specialization") if existing else "Your Specialization"
        bio_prev  = existing.get("bio", "Your bio will appear here...") if existing else "Your bio will appear here..."
        skills_prev = existing.get("skills", "skill1, skill2") if existing else "skill1, skill2"
        exp       = existing.get("experience", 0) if existing else 0
        rate      = existing.get("hourly_rate", 0) if existing else 0
        rating    = existing.get("rating", 0) if existing else 0

        st.markdown(f"""
        <div class="tl-card" style="text-align:center;">
            <div style="font-size:3.5rem; margin-bottom:0.5rem;">👨‍🏫</div>
            <div style="font-size:1.3rem; font-weight:800; color:var(--text);">{name}</div>
            <div style="color:var(--primary); font-size:0.9rem; margin:0.25rem 0;">{spec}</div>
            <div style="color:var(--text-muted); font-size:0.85rem; margin:0.25rem 0;">📱 {mobile}</div>
            <div style="color:var(--warning); font-size:0.85rem; margin:0.25rem 0;">
                {'⭐' * int(rating)}{'☆' * (5-int(rating))} {rating:.1f}
            </div>
            <hr>
            <div style="color:var(--text-muted); font-size:0.85rem; text-align:left; line-height:1.6;">
                {bio_prev[:150]}{'...' if len(bio_prev) > 150 else ''}
            </div>
            <hr>
            <div style="font-size:0.8rem; color:var(--text-muted); text-align:left; display:grid; gap:0.3rem;">
                <div>🏷️ {skills_prev[:60]}{'...' if len(skills_prev) > 60 else ''}</div>
                <div>⏳ {exp} years experience</div>
                <div>💰 ₹{rate}/hr</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("### ✏️ Edit Profile Details")

        bio = st.text_area(
            "Bio / About Me *",
            value=existing.get("bio", "") if existing else "",
            placeholder="Tell students about your background, teaching style, and expertise...",
            height=120
        )

        specialization = st.selectbox(
            "Specialization",
            ALL_SPECIALIZATIONS,
            index=ALL_SPECIALIZATIONS.index(existing["specialization"])
                  if existing and existing.get("specialization") in ALL_SPECIALIZATIONS else 0
        )

        st.markdown("**Skills / Subjects (select all that apply)** *")
        default_skills = [s.strip() for s in ((existing or {}).get("skills") or "").split(",") if s.strip()]
        selected_skills = st.multiselect(
            "Skills",
            ALL_SUBJECTS,
            default=[s for s in default_skills if s in ALL_SUBJECTS],
            label_visibility="collapsed"
        )

        custom_skills = st.text_input(
            "Additional custom skills (comma-separated)",
            value=", ".join([s for s in default_skills if s not in ALL_SUBJECTS]),
            placeholder="e.g. Rust, Flutter, Stage Presence"
        )

        c1, c2 = st.columns(2)
        with c1:
            experience_years = st.number_input(
                "Years of Experience",
                min_value=0, max_value=50,
                value=existing.get("experience", 0) if existing else 0
            )
        with c2:
            hourly_rate = st.number_input(
                "Hourly Rate (₹)",
                min_value=0.0, max_value=10000.0, step=50.0,
                value=float(existing.get("hourly_rate", 0)) if existing else 0.0
            )

        all_skills = selected_skills.copy()
        if custom_skills:
            extra = [s.strip() for s in custom_skills.split(",") if s.strip()]
            all_skills.extend(extra)
        skills_str = ", ".join(all_skills)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Profile", use_container_width=True):
            errors = []
            if not bio.strip():
                errors.append("Please write a bio.")
            if not all_skills:
                errors.append("Please select or enter at least one skill/subject.")

            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                upsert_tutor_profile(
                    user_id=user["id"],
                    bio=bio,
                    skills=skills_str,
                    specialization=specialization,
                    experience=experience_years,
                    hourly_rate=hourly_rate,
                )
                st.success("✅ Profile saved! Students can now discover you.")
                st.rerun()
