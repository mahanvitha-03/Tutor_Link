"""
account_settings.py — Shared Account Settings page
Accessible to BOTH student and tutor accounts.

Any changes made here (full name, email, mobile) are written directly to
the `users` table and are immediately visible across every session because
get_current_user() always fetches a fresh row from the DB.
"""

import streamlit as st
from auth import get_current_user, verify_password, hash_password
from database import update_user_info, update_user_theme, get_connection


def _update_password(user_id: int, old_pass: str, new_pass: str) -> tuple[bool, str]:
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT password FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return False, "User not found."
        if not verify_password(old_pass, row["password"]):
            return False, "Current password is incorrect."
        if len(new_pass) < 6:
            return False, "New password must be at least 6 characters."
        hashed = hash_password(new_pass)
        conn2 = get_connection()
        conn2.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        conn2.commit()
        conn2.close()
        return True, "Password updated successfully."
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return False, str(e)


def render():
    from app import tl_header, section

    user = get_current_user()

    if st.button("← Back to Dashboard", key="back_account"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    tl_header(
        "⚙️", "Account Settings",
        "Changes are saved to the database and reflected everywhere — "
        "tutor cards, dashboards, messages, and all other accounts instantly."
    )

    st.info(
        "ℹ️ **Global sync**: Because all data is stored in a shared SQLite database, "
        "any profile update you make here is immediately visible to every other user "
        "(students see updated tutor names, tutors see updated student names, etc.).",
        icon="🔄"
    )

    tab_profile, tab_password = st.tabs(["👤 Profile Info", "🔐 Change Password"])

    # ── Tab 1: Profile Info ────────────────────────────────────────────────────
    with tab_profile:
        st.markdown("<br>", unsafe_allow_html=True)
        section("Personal Information")
        st.caption(
            "Updating your name or contact details here will update it across the entire "
            "platform — your name will appear correctly to tutors, students, and in all "
            "session listings immediately."
        )

        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input(
                "Full Name *",
                value=user.get("full_name", ""),
                placeholder="Your full name",
                key="acc_full_name"
            )
        with c2:
            new_email = st.text_input(
                "Email Address",
                value=user.get("email", ""),
                placeholder="you@email.com",
                key="acc_email"
            )

        new_mobile = st.text_input(
            "Mobile Number",
            value=user.get("mobile_number", ""),
            placeholder="+91 9876543210",
            key="acc_mobile"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        section("Display Preferences")
        current_theme = st.session_state.get("theme_override", user.get("theme", "dark"))
        new_theme = st.radio(
            "Theme",
            ["dark", "light"],
            index=0 if current_theme == "dark" else 1,
            format_func=lambda x: "🌙 Dark Mode" if x == "dark" else "☀️ Light Mode",
            horizontal=True,
            key="acc_theme"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save All Changes", use_container_width=True, key="save_account"):
            errors = []
            if not new_name.strip():
                errors.append("Full name cannot be empty.")
            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                # Update name / email / mobile in users table (global)
                ok = update_user_info(user["id"], new_name.strip(), new_email.strip(), new_mobile.strip())
                # Update theme
                update_user_theme(user["id"], new_theme)
                st.session_state["theme_override"] = new_theme
                # Also keep session full_name in sync
                st.session_state["full_name"] = new_name.strip()

                if ok:
                    st.success(
                        "✅ Profile saved! Your name and contact details are now updated "
                        "across the entire platform — all other users will see the changes "
                        "immediately."
                    )
                    st.rerun()
                else:
                    st.error("❌ Failed to save changes. Please try again.")

    # ── Tab 2: Change Password ─────────────────────────────────────────────────
    with tab_password:
        st.markdown("<br>", unsafe_allow_html=True)
        section("Update Password")

        old_pass = st.text_input("Current Password", type="password", key="acc_old_pass")
        c3, c4 = st.columns(2)
        with c3:
            new_pass = st.text_input("New Password", type="password",
                                     placeholder="Min. 6 characters", key="acc_new_pass")
        with c4:
            new_pass2 = st.text_input("Confirm New Password", type="password",
                                      placeholder="Repeat new password", key="acc_new_pass2")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔐 Update Password", use_container_width=True, key="save_password"):
            if not old_pass or not new_pass or not new_pass2:
                st.error("❌ Please fill in all password fields.")
            elif new_pass != new_pass2:
                st.error("❌ New passwords do not match.")
            else:
                ok, msg = _update_password(user["id"], old_pass, new_pass)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
