"""
my_sessions.py — Student's session history with reminders
"""

import streamlit as st
import datetime
from auth import get_current_user
from database import (
    get_bookings_for_student, add_feedback,
    get_feedback_for_booking, update_booking_status
)


def render():
    user = get_current_user()

    if st.button("← Back to Dashboard", key="back_my_sessions"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="tl-header">
        <h1>📅 My Sessions</h1>
        <p>View all your bookings and leave feedback.</p>
    </div>
    """, unsafe_allow_html=True)

    bookings = get_bookings_for_student(user["id"])

    if not bookings:
        st.markdown("""
        <div class="tl-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem;">📭</div>
            <div style="font-size:1.2rem; color:var(--text); margin:1rem 0;">No sessions booked yet</div>
            <div style="color:var(--text-muted);">Browse our tutors and book your first session!</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Browse Tutors"):
            st.session_state["page"] = "browse_tutors"
            st.rerun()
        return

    # ── Reminder Banner for sessions today or tomorrow ──
    today = datetime.date.today()
    upcoming_confirmed = [
        b for b in bookings
        if b["status"] == "accepted" and b.get("scheduled_date", "") >= str(today)
    ]
    # Find sessions within next 24 hours
    reminders = []
    for b in upcoming_confirmed:
        try:
            session_dt = datetime.datetime.strptime(b.get("scheduled_date", ""), "%Y-%m-%d").date()
            days_until = (session_dt - today).days
            if days_until <= 1:
                reminders.append((b, days_until))
        except Exception:
            pass

    if reminders:
        for (b, days) in reminders:
            when = "TODAY" if days == 0 else "TOMORROW"
            st.markdown(f"""
            <div style="background:rgba(251,191,36,0.12); border:1px solid rgba(251,191,36,0.35);
                        border-radius:12px; padding:1rem 1.5rem; margin-bottom:1rem;
                        display:flex; align-items:center; gap:1rem;">
                <div style="font-size:1.8rem;">⏰</div>
                <div>
                    <div style="font-weight:700; color:var(--warning);">Upcoming Session — {when}!</div>
                    <div style="color:var(--text-muted); font-size:0.88rem; margin-top:0.25rem;">
                        📅 {b.get('scheduled_date', 'N/A')} at {b.get('start_time', 'N/A')} with <b>{b.get('tutor_name', 'N/A')}</b>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Stats ──
    cols = st.columns(4)
    statuses = ["pending", "accepted", "rejected", "completed"]
    icons    = ["⏳", "✅", "❌", "🎓"]
    for i, (s, ic) in enumerate(zip(statuses, icons)):
        with cols[i]:
            count = sum(1 for b in bookings if b["status"] == s)
            st.metric(f"{ic} {s.title()}", count)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter ──
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "accepted", "rejected", "completed"])
    filtered = bookings if status_filter == "All" else [b for b in bookings if b["status"] == status_filter]

    for booking in filtered:
        status = booking["status"]
        feedback_exists = get_feedback_for_booking(booking["id"])

        with st.expander(
            f"� {booking.get('scheduled_date', 'N/A')}  ·  👨‍🏫 {booking.get('tutor_name', 'N/A')}  ·  🕐 {booking.get('start_time', 'N/A')}",
            expanded=(status == "accepted")
        ):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"""
                <div style="display:grid; gap:0.4rem; font-size:0.9rem;">
                    <div><b>Tutor:</b> <span style="color:var(--primary);">{booking.get('tutor_name', 'N/A')}</span></div>
                    <div><b>Date:</b> {booking.get('scheduled_date', 'N/A')} &nbsp;|&nbsp; <b>Time:</b> {booking.get('start_time', 'N/A')}</div>
                    <div><b>Duration:</b> {booking.get('start_time', 'N/A')} - {booking.get('end_time', 'N/A')}</div>
                </div>"
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="text-align:center; padding:1rem;">
                    <span class="badge badge-{status}">{status.upper()}</span>
                </div>
                """, unsafe_allow_html=True)

            # Mark as completed (student side)
            if status == "accepted":
                if st.button("✅ Mark as Completed", key=f"complete_{booking['id']}"):
                    update_booking_status(booking["id"], "completed")
                    st.success("Session marked as completed!")
                    st.rerun()

            # Feedback
            if status == "completed" and not feedback_exists:
                st.markdown("---")
                st.markdown("**⭐ Leave Feedback**")
                rating  = st.slider("Rating", 1, 5, 4, key=f"rating_{booking['id']}")
                comment = st.text_area("Your Review", placeholder="How was your experience?",
                                       key=f"comment_{booking['id']}", height=70)
                if st.button("Submit Feedback", key=f"submit_fb_{booking['id']}"):
                    add_feedback(
                        booking_id=booking["id"],
                        student_id=user["id"],
                        tutor_id=booking["tutor_id"],
                        rating=rating,
                        comment=comment
                    )
                    st.success("✅ Feedback submitted! Thank you.")
                    st.rerun()

            elif feedback_exists:
                st.markdown(f"""
                <div style="background:rgba(45,212,191,0.1); border:1px solid rgba(45,212,191,0.3);
                            border-radius:8px; padding:0.75rem; margin-top:0.5rem; font-size:0.85rem;">
                    ✅ <b>Feedback submitted:</b> {'⭐' * feedback_exists['rating']} — {feedback_exists['comment'] or ''}
                </div>
                """, unsafe_allow_html=True)
