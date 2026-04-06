"""
messages.py — Messaging between students and tutors

ENHANCEMENTS:
  - Back button
  - CSS variables for light/dark theme compatibility
"""

import streamlit as st
from auth import get_current_user
from database import (
    send_message, get_messages, get_conversation_partners,
    get_all_tutors
)


def render():
    user = get_current_user()

    if st.button("← Back to Dashboard", key="back_messages"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="tl-header">
        <h1>💬 Messages</h1>
        <p>Chat with tutors or students to plan sessions and get guidance.</p>
    </div>
    """, unsafe_allow_html=True)

    col_contacts, col_chat = st.columns([1, 2])

    with col_contacts:
        st.markdown("### 👥 Contacts")
        if user["role"] == "student":
            tutors = get_all_tutors()
            contact_list = [{"id": t["id"], "full_name": t["full_name"],
                             "role": "tutor", "username": t["username"]} for t in tutors]
        else:
            contact_list = get_conversation_partners(user["id"])

        if not contact_list:
            st.markdown("<div style='color:var(--text-muted); font-size:0.85rem;'>No contacts yet.</div>",
                        unsafe_allow_html=True)
        else:
            for contact in contact_list:
                icon = "👨‍🏫" if contact.get("role") == "tutor" else "🎓"
                if st.button(f"{icon} {contact['full_name']}", key=f"contact_{contact['id']}",
                             use_container_width=True):
                    st.session_state["chat_with"] = contact["id"]
                    st.session_state["chat_with_name"] = contact["full_name"]
                    st.rerun()

    with col_chat:
        chat_partner_id   = st.session_state.get("chat_with")
        chat_partner_name = st.session_state.get("chat_with_name", "")

        if not chat_partner_id:
            st.markdown("""
            <div class="tl-card" style="text-align:center; padding:4rem;">
                <div style="font-size:3rem; margin-bottom:1rem;">💬</div>
                <div style="color:var(--text-muted);">Select a contact to start chatting</div>
            </div>
            """, unsafe_allow_html=True)
            return

        st.markdown(f"""
        <div style="background:var(--surface); border:1px solid var(--border);
                    border-radius:16px 16px 0 0; padding:1rem 1.5rem;
                    display:flex; align-items:center; gap:0.75rem;">
            <div style="font-size:1.5rem;">💬</div>
            <div>
                <div style="font-weight:700; color:var(--text);">{chat_partner_name}</div>
                <div style="font-size:0.75rem; color:var(--primary);">Conversation</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        messages = get_messages(user["id"], chat_partner_id)
        chat_html = '<div style="background:var(--surface2); border:1px solid var(--border); border-top:none; padding:1.5rem; min-height:350px; max-height:400px; overflow-y:auto;">'

        if not messages:
            chat_html += '<div style="text-align:center; color:var(--text-muted); padding:2rem; font-size:0.9rem;">No messages yet. Say hello! 👋</div>'
        else:
            for msg in messages:
                is_mine = msg["sender_id"] == user["id"]
                if is_mine:
                    bubble = "background:rgba(108,99,255,0.22); margin-left:auto; border-radius:18px 18px 4px 18px;"
                else:
                    bubble = "background:rgba(255,255,255,0.06); margin-right:auto; border-radius:18px 18px 18px 4px;"
                align      = "right" if is_mine else "left"
                name_label = "You" if is_mine else msg["sender_name"]
                time_str   = msg["sent_at"][:16] if msg.get("sent_at") else ""
                chat_html += f"""
                <div style="max-width:75%; {bubble} padding:0.6rem 1rem; margin-bottom:0.75rem;">
                    <div style="font-size:0.7rem; color:var(--text-muted); margin-bottom:2px; text-align:{align};">
                        {name_label} · {time_str}
                    </div>
                    <div style="color:var(--text); font-size:0.875rem; line-height:1.5;">{msg['content']}</div>
                </div>
                """

        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:var(--surface); border:1px solid var(--border); border-top:none;
                    border-radius:0 0 16px 16px; padding:0.75rem 1rem;">
        </div>
        """, unsafe_allow_html=True)

        msg_col, btn_col = st.columns([5, 1])
        with msg_col:
            new_msg = st.text_input("Message", placeholder="Type a message...",
                                    label_visibility="collapsed", key="chat_input")
        with btn_col:
            if st.button("Send →", use_container_width=True):
                if new_msg.strip():
                    send_message(user["id"], chat_partner_id, new_msg.strip())
                    st.rerun()
                else:
                    st.warning("Message can't be empty.")
