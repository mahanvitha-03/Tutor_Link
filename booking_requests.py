"""
booking_requests.py — Tutor reviews and responds to booking requests
"""

import streamlit as st
from auth import get_current_user
from database import (
    get_bookings_for_tutor, update_booking_status,
    create_notification
)


def render():
    user = get_current_user()

    if st.button("← Back to Dashboard", key="back_booking_req"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="tl-header">
        <h1>📋 Booking Requests</h1>
        <p>Review, accept, or reject student session requests.</p>
    </div>
    """, unsafe_allow_html=True)

    bookings = get_bookings_for_tutor(user["id"])
    pending   = [b for b in bookings if b["status"] == "pending"]
    others    = [b for b in bookings if b["status"] != "pending"]

    # ── Stats ──
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("⏳ Pending",   len(pending))
    with c2: st.metric("✅ Accepted",  sum(1 for b in bookings if b["status"] == "accepted"))
    with c3: st.metric("❌ Rejected",  sum(1 for b in bookings if b["status"] == "rejected"))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pending Requests ──
    st.markdown("### 🔔 Pending Requests")
    if not pending:
        st.markdown("""
        <div class="tl-card" style="text-align:center; padding:2rem;">
            <div style="font-size:2rem;">🎉</div>
            <div style="color:var(--text-muted);">No pending requests — all caught up!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for b in pending:
            st.markdown(f"""
            <div class="tl-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <div style="font-size:1.05rem; font-weight:700; color:var(--text);">
                            � Session Request
                        </div>
                        <div style="color:var(--text-muted); font-size:0.85rem; margin-top:0.3rem;">
                            🎓 <b style="color:var(--primary);">{b.get('student_name', 'N/A')}</b>
                            &nbsp;|&nbsp; 📅 {b.get('scheduled_date', 'N/A')}
                            &nbsp;|&nbsp; 🕐 {b.get('start_time', 'N/A')}
                        </div>
                        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">
                            Received: {b.get('created_at', 'N/A')[:10] if b.get('created_at') else 'N/A'}
                        </div>
                    </div>
                    <span class="badge badge-pending">AWAITING RESPONSE</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Respond to {b['student_name']}'s request"):
                tutor_note = st.text_area(
                    "Message to Student (optional)",
                    placeholder="Note about the session, what to prepare, or reason if rejecting...",
                    key=f"tnote_{b['id']}", height=70
                )
                ac1, ac2, _ = st.columns([1, 1, 2])
                with ac1:
                    if st.button("✅ Accept", key=f"accept_{b['id']}", use_container_width=True):
                        update_booking_status(b["id"], "accepted", tutor_note)
                        create_notification(
                            b["student_id"],
                            "Booking Confirmed",
                            f"Your session with {user['full_name']} on {b.get('scheduled_date', 'N/A')} at {b.get('start_time', 'N/A')} has been confirmed!"
                        )
                        st.success(f"✅ Session with {b.get('student_name', 'N/A')} accepted!")
                        st.rerun()
                with ac2:
                    if st.button("❌ Reject", key=f"reject_{b['id']}", use_container_width=True):
                        update_booking_status(b["id"], "rejected", tutor_note)
                        create_notification(
                            b["student_id"],
                            "Booking Update",
                            f"Your session request with {user['full_name']} on {b.get('scheduled_date', 'N/A')} was not accepted. Reason: {tutor_note or 'No reason provided.'}"
                        )
                        st.warning(f"Session with {b.get('student_name', 'N/A')} rejected.")
                        st.rerun()

    # ── Past Decisions ──
    if others:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📂 Past Decisions")

        status_filter = st.selectbox("Filter by Status", ["All", "accepted", "rejected", "completed"])
        filtered = others if status_filter == "All" else [b for b in others if b["status"] == status_filter]

        for b in filtered:
            st.markdown(f"""
            <div class="tl-card" style="padding:1rem 1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                    <div>
                        <div style="font-weight:700; color:var(--text);">Session Details</div>
                        <div style="color:var(--text-muted); font-size:0.82rem;">
                            🎓 {b.get('student_name', 'N/A')} &nbsp;|&nbsp; 📅 {b.get('scheduled_date', 'N/A')} &nbsp;|&nbsp; 🕐 {b.get('start_time', 'N/A')}
                        </div>
                    </div>
                    <span class="badge badge-{b['status']}">{b['status'].upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
