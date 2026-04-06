"""
reviews.py — Tutor views all student reviews and ratings

ENHANCEMENTS:
  - Back button
  - CSS variables for theme compatibility
"""

import streamlit as st
from auth import get_current_user
from database import get_feedback_for_tutor, get_tutor_profile


def render():
    user    = get_current_user()
    reviews = get_feedback_for_tutor(user["id"])

    if st.button("← Back to Dashboard", key="back_reviews"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="tl-header">
        <h1>⭐ My Reviews</h1>
        <p>See what students say about your sessions.</p>
    </div>
    """, unsafe_allow_html=True)

    if not reviews:
        st.markdown("""
        <div class="tl-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem;">⭐</div>
            <div style="font-size:1.1rem; color:var(--text); margin:1rem 0;">No reviews yet</div>
            <div style="color:var(--text-muted);">Reviews appear after students submit feedback on completed sessions.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    avg_rating    = sum(r["rating"] for r in reviews) / len(reviews)
    rating_counts = {i: sum(1 for r in reviews if r["rating"] == i) for i in range(1, 6)}

    col_summary, col_dist = st.columns([1, 2])
    with col_summary:
        st.markdown(f"""
        <div class="tl-card" style="text-align:center; padding:2rem;">
            <div style="font-size:3.5rem; font-weight:800; color:var(--warning);">{avg_rating:.1f}</div>
            <div style="color:var(--warning); font-size:1.3rem; margin:0.25rem 0;">
                {'⭐' * int(avg_rating)}{'☆' * (5-int(avg_rating))}
            </div>
            <div style="color:var(--text-muted); font-size:0.85rem;">{len(reviews)} total reviews</div>
        </div>
        """, unsafe_allow_html=True)

    with col_dist:
        st.markdown("**Rating Distribution**")
        for stars in range(5, 0, -1):
            count = rating_counts.get(stars, 0)
            pct   = (count / len(reviews) * 100) if reviews else 0
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.5rem;">
                <div style="color:var(--warning); min-width:60px; font-size:0.85rem;">{'⭐' * stars}</div>
                <div style="flex:1; background:rgba(255,255,255,0.07); border-radius:999px; height:8px; overflow:hidden;">
                    <div style="background:var(--warning); width:{pct}%; height:100%; border-radius:999px;"></div>
                </div>
                <div style="min-width:30px; color:var(--text-muted); font-size:0.8rem; text-align:right;">{count}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💬 All Reviews")
    for r in reviews:
        stars = r["rating"]
        st.markdown(f"""
        <div class="tl-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <div style="font-size:1.5rem;">👤</div>
                    <div>
                        <div style="font-weight:700; color:var(--text);">{r['student_name']}</div>
                        <div style="color:var(--text-muted); font-size:0.75rem;">{r['created_at'][:10]}</div>
                    </div>
                </div>
                <div style="color:var(--warning); font-size:1.1rem;">
                    {'⭐' * stars}{'☆' * (5-stars)}
                </div>
            </div>
            {f'<div style="color:var(--text-muted); font-size:0.875rem; margin-top:0.75rem; line-height:1.6; border-left:3px solid var(--border); padding-left:1rem;">{r["comment"]}</div>' if r.get("comment") else '<div style="color:var(--text-muted); font-size:0.8rem; margin-top:0.5rem; font-style:italic;">No written review.</div>'}
        </div>
        """, unsafe_allow_html=True)
