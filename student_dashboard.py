"""
student_dashboard.py — Student home dashboard (TutorLink v3)
• Session-reminder banners (today / tomorrow)
• Payment status chips
• 5-column stat row
• Featured tutors grid with "Book" shortcut
"""

import streamlit as st
import datetime
from auth import get_current_user
from database import (
    get_bookings_for_student, get_progress_entries,
    get_all_tutors, get_unread_count
)
from app import tl_header, section, badge, stars_html


def render():
    user     = get_current_user()
    bookings = get_bookings_for_student(user["id"])
    progress = get_progress_entries(user["id"])
    tutors   = get_all_tutors()
    unread   = get_unread_count(user["id"])
    today    = datetime.date.today()

    tl_header("👋", f"Welcome back, {user['full_name'].split()[0]}!",
              "Your learning dashboard — sessions, progress, and tutors.")

    # ── Notification banner ────────────────────────────────────────────────────
    if unread > 0:
        col_n, col_nb = st.columns([4, 1])
        with col_n:
            st.markdown(f"""
            <div style="background:var(--primary-glow);border:1px solid var(--border-s);
                        border-radius:10px;padding:0.75rem 1.2rem;display:flex;
                        align-items:center;gap:0.75rem;">
              <span style="font-size:1.3rem;">🔔</span>
              <span style="color:var(--text);font-weight:600;">
                {unread} unread notification{'s' if unread > 1 else ''}
              </span>
            </div>
            """, unsafe_allow_html=True)
        with col_nb:
            if st.button("View →", key="dash_notifs"):
                st.session_state["page"] = "notifications"
                st.rerun()

    # ── Reminder banners ───────────────────────────────────────────────────────
    for b in (b for b in bookings if b["status"] == "accepted"):
        try:
            dt = datetime.datetime.strptime(b.get("scheduled_date", ""), "%Y-%m-%d").date()
            days = (dt - today).days
            if days == 0:
                cls, lbl, col = "reminder-today",    "⏰ TODAY",    "var(--danger)"
            elif days == 1:
                cls, lbl, col = "reminder-tomorrow", "⏰ TOMORROW", "var(--warning)"
            else:
                continue
            st.markdown(f"""
            <div class="{cls}">
              <span style="color:{col};font-weight:700;font-size:0.88rem;">{lbl}</span>
              <span style="color:var(--text);font-size:0.88rem;margin-left:0.6rem;">
                Session with <b>{b.get('tutor_name', 'N/A')}</b> at {b.get('start_time', 'N/A')}
              </span>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    # ── Stats ─────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("⏳ Pending",   sum(1 for b in bookings if b["status"] == "pending"))
    with c2: st.metric("✅ Confirmed", sum(1 for b in bookings if b["status"] == "accepted"))
    with c3: st.metric("🎓 Completed", sum(1 for b in bookings if b["status"] == "completed"))
    with c4: st.metric("📊 Progress",  len(progress))

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    # ── Upcoming sessions ──────────────────────────────────────────────────────
    with col_left:
        section("📅 Upcoming Sessions")
        upcoming = [b for b in bookings if b["status"] == "accepted"]
        if upcoming:
            for b in upcoming[:4]:
                st.markdown(f"""
                <div class="tl-card">
                  <div style="display:flex;justify-content:space-between;
                              align-items:flex-start;flex-wrap:wrap;gap:0.4rem;">
                    <div>
                      <div style="font-weight:700;color:var(--text);font-size:0.95rem;">
                        � Confirmed Session
                      </div>
                      <div style="color:var(--text-muted);font-size:0.82rem;margin-top:0.2rem;">
                        👨‍🏫 {b.get('tutor_name', 'N/A')} &nbsp;·&nbsp; 📅 {b.get('scheduled_date', 'N/A')}
                        &nbsp;·&nbsp; 🕐 {b.get('start_time', 'N/A')}
                      </div>
                    </div>
                    <span class="badge badge-accepted">Confirmed</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tl-card" style="text-align:center;padding:2.5rem;">
              <div style="font-size:2rem;margin-bottom:0.5rem;">📭</div>
              <div style="color:var(--text-muted);">No upcoming sessions yet.</div>
              <div style="color:var(--primary);font-size:0.83rem;margin-top:0.3rem;">
                Browse tutors to book your first session!
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Quick actions + progress ───────────────────────────────────────────────
    with col_right:
        section("⚡ Quick Actions")
        for lbl, pg in [
            ("🔍 Browse Tutors",     "browse_tutors"),
            ("📈 Log Progress",      "progress"),
            ("📋 My Sessions",       "my_sessions"),
            ("🔔 Notifications",     "notifications"),
        ]:
            if st.button(lbl, use_container_width=True, key=f"qa_{pg}"):
                st.session_state["page"] = pg
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        section("📈 Recent Progress")
        if progress:
            for e in progress[:3]:
                score = e["score"]
                col   = "var(--success)" if score >= 7 else "var(--warning)" if score >= 4 else "var(--danger)"
                st.markdown(f"""
                <div style="margin-bottom:0.7rem;">
                  <div style="display:flex;justify-content:space-between;
                              font-size:0.83rem;color:var(--text);margin-bottom:3px;">
                    <span>{e['skill_area']}</span>
                    <span style="color:{col};font-weight:700;">{score}/10</span>
                  </div>
                  <div class="prog-bar-wrap">
                    <div class="prog-bar" style="background:{col};width:{score*10}%;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:var(--text-dim);font-size:0.83rem;'>"
                        "No progress logged yet.</div>", unsafe_allow_html=True)

    # ── Featured tutors ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section("🌟 Featured Tutors")
    featured = [t for t in tutors if t.get("bio")][:3]
    if featured:
        cols = st.columns(len(featured))
        for i, t in enumerate(featured):
            with cols[i]:
                rating  = t.get("rating") or 0
                reviews = t.get("total_reviews") or 0
                skills  = t.get("skills") or "—"
                st.markdown(f"""
                <div class="tl-card" style="text-align:center;padding:1.4rem 1rem;">
                  <div class="avatar-ring" style="margin:0 auto 0.6rem;">👨‍🏫</div>
                  <div style="font-family:'Syne',sans-serif;font-weight:700;
                              color:var(--text);font-size:0.95rem;">{t['full_name']}</div>
                  <div style="color:var(--primary);font-size:0.77rem;margin-top:2px;">
                    {t.get('specialization') or 'Coach'}
                  </div>
                  <div style="margin:0.35rem 0;">{stars_html(rating)}
                    <span style="color:var(--text-dim);font-size:0.72rem;"> {rating:.1f} ({reviews})</span>
                  </div>
                  <div style="color:var(--text-dim);font-size:0.73rem;">{skills[:60]}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Book →", key=f"feat_{t['id']}", use_container_width=True):
                    st.session_state["page"] = "browse_tutors"
                    st.rerun()
    else:
        st.info("Tutors will appear here once they complete their profiles.")
