"""
video_chat.py — Simple video chat page using Jitsi Meet embed
"""

import datetime
import urllib.parse

import streamlit as st
import streamlit.components.v1 as components
from auth import get_current_user
from database import get_bookings_for_student, get_bookings_for_tutor


def _build_room_name(user, session):
    if session:
        return f"tutorlink-session-{session['id']}"
    return f"tutorlink-{user['role']}-{user['id']}-{datetime.date.today().strftime('%Y%m%d')}"


def _find_next_session(user):
    if user["role"] == "student":
        bookings = get_bookings_for_student(user["id"])
        partner_key = "tutor_name"
    else:
        bookings = get_bookings_for_tutor(user["id"])
        partner_key = "student_name"

    upcoming = [b for b in bookings if b.get("status") == "accepted"]
    def sort_key(b):
        try:
            date_part = datetime.datetime.strptime(b.get("scheduled_date", ""), "%Y-%m-%d").date()
        except Exception:
            date_part = datetime.date.max
        return (date_part, b.get("start_time", ""))

    upcoming.sort(key=sort_key)
    return upcoming[0] if upcoming else None


def render():
    user = get_current_user()

    if st.button("← Back to Dashboard", key="back_video_chat"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown(
        """
        <div class="tl-header">
            <h1>🎥 Video Chat</h1>
            <p>Start or join a live tutoring session with video and audio.</p>
        </div>
        """, unsafe_allow_html=True
    )

    session = _find_next_session(user)
    suggested_room = _build_room_name(user, session)

    if session:
        partner = session.get("student_name") if user["role"] == "tutor" else session.get("tutor_name")
        st.info(
            f"Suggested room for your next confirmed session with {partner} on "
            f"{session.get('scheduled_date', 'N/A')} at {session.get('start_time', 'N/A')}."
        )
    else:
        st.info(
            "No confirmed session was detected. Enter a room name below to create a new video call. "
            "Share the same room name with your partner to join together."
        )

    if "video_room" not in st.session_state:
        st.session_state["video_room"] = suggested_room

    room_name = st.text_input(
        "Meeting room name",
        value=st.session_state["video_room"],
        help="Use the same room name for the tutor and student to join the same call.",
        key="video_room"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    room_name = room_name.strip() or suggested_room
    join_link = f"https://meet.jit.si/{urllib.parse.quote(room_name)}"

    st.markdown(
        f"**Meeting room:** `{room_name}`<br>"
        f"**Open link:** [Join video call]({join_link})",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='color:var(--text-muted); font-size:0.9rem;'>"
                "Allow camera and microphone access when prompted. "
                "If you want, open the same room on a second device or share the link with your tutor/student."
                "</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔗 Open in New Tab", key="open_new_tab"):
            st.markdown(f'<script>window.open("{join_link}", "_blank");</script>', unsafe_allow_html=True)
    with col2:
        if st.button("📋 Copy Room Link", key="copy_link"):
            st.code(join_link, language=None)

    st.markdown("<br>", unsafe_allow_html=True)

    if room_name:
        iframe_html = f"""
        <iframe
            src="{join_link}#config.prejoinPageEnabled=false&userInfo.displayName={urllib.parse.quote(user['full_name'])}"
            allow="camera; microphone; fullscreen; display-capture; autoplay; encrypted-media"
            referrerpolicy="no-referrer-when-downgrade"
            style="width:100%; height:720px; border:0; border-radius:14px; overflow:hidden;"
        ></iframe>
        """
        components.html(iframe_html, height=740)

