"""
upcoming_sessions.py — Tutor views confirmed and completed sessions
"""

import streamlit as st
import datetime
from auth import get_current_user
from database import (
    get_bookings_for_tutor, update_booking_status,
    create_notification
)


def render():
    user = get_current_user()

    if st.button("← Back to Dashboard", key="back_upcoming"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="tl-header">
        <h1>📅 Upcoming Sessions</h1>
        <p>All your confirmed sessions and session history.</p>
    </div>
    """, unsafe_allow_html=True)

    bookings  = get_bookings_for_tutor(user["id"])
    accepted  = [b for b in bookings if b["status"] == "accepted"]
    completed = [b for b in bookings if b["status"] == "completed"]

    # ── Stats ──
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📅 Upcoming",     len(accepted))
    with c2: st.metric("🎓 Completed",    len(completed))
    with c3: st.metric("👥 Unique Students", len({b["student_id"] for b in bookings}))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Reminder Banners ──
    today = datetime.date.today()
    for b in accepted:
        try:
            session_dt = datetime.datetime.strptime(b.get("scheduled_date", ""), "%Y-%m-%d").date()
            days_away  = (session_dt - today).days
            if days_away == 0:
                label, color, border, tc = "TODAY", "rgba(248,113,113,0.15)", "rgba(248,113,113,0.4)", "var(--danger)"
            elif days_away == 1:
                label, color, border, tc = "TOMORROW", "rgba(251,191,36,0.12)", "rgba(251,191,36,0.35)", "var(--warning)"
            else:
                continue
            st.markdown(f"""
            <div style="background:{color}; border:1px solid {border}; border-radius:12px;
                        padding:0.85rem 1.4rem; margin-bottom:0.6rem; display:flex; align-items:center; gap:1rem;">
                <span style="color:{tc}; font-weight:700; font-size:0.9rem;">⏰ {label}</span>
                <span style="color:var(--text); font-size:0.9rem;">
                    Session with <b>{b.get('student_name', 'N/A')}</b>
                    &nbsp;|&nbsp; 🕐 {b.get('start_time', 'N/A')}
                </span>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    # ── Confirmed / Upcoming Sessions ──
    st.markdown("### ✅ Confirmed Upcoming Sessions")
    if not accepted:
        st.markdown("""
        <div class="tl-card" style="text-align:center; padding:2rem;">
            <div style="font-size:2rem;">📭</div>
            <div style="color:var(--text-muted);">No upcoming confirmed sessions.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for b in accepted:
            with st.container():
                st.markdown(f"""
                <div class="tl-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
                        <div>
                            <div style="font-size:1.05rem; font-weight:700; color:var(--text);">
                                � Session Details
                            </div>
                            <div style="color:var(--text-muted); font-size:0.85rem; margin-top:0.3rem;">
                                🎓 <b style="color:var(--primary);">{b['student_name']}</b>
                                &nbsp;|&nbsp; 📅 {b.get('scheduled_date', 'N/A')}
                                &nbsp;|&nbsp; 🕐 {b.get('start_time', 'N/A')}
                            </div>

                        </div>
                        <span class="badge badge-accepted">CONFIRMED</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_col1, _ = st.columns([1, 3])
                with btn_col1:
                    if st.button("✅ Mark Completed", key=f"done_{b['id']}"):
                        update_booking_status(b["id"], "completed")
                        create_notification(
                            user_id=b["student_id"],
                            title="Session Completed 🎓",
                            message=f"Your session with {user['full_name']} on {b.get('scheduled_date', 'N/A')} has been marked as completed.",
                            notif_type="success"
                        )
                        st.success("Session marked as completed!")
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    # ── Session History ──
    if completed:
        st.markdown("### 🎓 Session History")
        for b in completed:
            st.markdown(f"""
            <div class="tl-card" style="padding:1rem 1.5rem; opacity:0.85;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                    <div>
                        <div style="font-weight:700; color:var(--text);">Session History</div>
                        <div style="color:var(--text-muted); font-size:0.82rem;">
                            🎓 {b.get('student_name', 'N/A')} &nbsp;|&nbsp; 📅 {b.get('scheduled_date', 'N/A')}
                        </div>
                    </div>
                    <span class="badge badge-completed">COMPLETED</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
