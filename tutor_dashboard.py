"""
tutor_dashboard.py — Tutor home dashboard (TutorLink v3)
Uses new tl-card classes, Syne headings, and improved layout.
"""

import streamlit as st
import datetime
from auth import get_current_user
from database import (
    get_bookings_for_tutor, get_tutor_profile,
    get_feedback_for_tutor, get_unread_count
)
from app import tl_header, section, stars_html, nav_to


def render():
    user     = get_current_user()
    profile  = get_tutor_profile(user["id"])
    bookings = get_bookings_for_tutor(user["id"])
    reviews  = get_feedback_for_tutor(user["id"])
    unread   = get_unread_count(user["id"])
    today    = datetime.date.today()

    tl_header("👨‍🏫", f"Welcome, {user['full_name'].split()[0]}!",
              "Manage sessions, availability, and help students grow.")

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
            if st.button("View →", key="tdash_notifs"):
                nav_to("notifications")

    # Profile incomplete
    if not profile or not profile.get("bio"):
        st.warning("⚠️ Profile incomplete — students can't discover you yet.")
        if st.button("👤 Complete Profile"):
            nav_to("tutor_profile")
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Session reminders ──────────────────────────────────────────────────────
    for b in (b for b in bookings if b["status"] == "accepted"):
        try:
            dt   = datetime.datetime.strptime(b.get("scheduled_date", ""), "%Y-%m-%d").date()
            days = (dt - today).days
            if days == 0:
                cls, lbl, col = "reminder-today",    "⏰ TODAY",    "var(--danger)"
            elif days == 1:
                cls, lbl, col = "reminder-tomorrow", "⏰ TOMORROW", "var(--warning)"
            else:
                continue
            st.markdown(f"""
            <div class="{cls}">
              <span style="color:{col};font-weight:700;">{lbl}</span>
              <span style="color:var(--text);margin-left:0.6rem;font-size:0.88rem;">
                Session with <b>{b.get('student_name', 'N/A')}</b>
                · {b.get('scheduled_date', 'N/A')} at {b.get('start_time', 'N/A')}
              </span>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    # ── Stats ─────────────────────────────────────────────────────────────────
    pending_list   = [b for b in bookings if b["status"] == "pending"]
    accepted_list  = [b for b in bookings if b["status"] == "accepted"]
    completed_list = [b for b in bookings if b["status"] == "completed"]
    avg_rating     = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("🔔 Requests",  len(pending_list))
    with c2: st.metric("✅ Active",    len(accepted_list))
    with c3: st.metric("🎓 Done",      len(completed_list))
    with c4: st.metric("⭐ Rating",    f"{avg_rating:.1f}/5" if reviews else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        section("🔔 New Booking Requests")
        if pending_list:
            for b in pending_list[:5]:
                st.markdown(f"""
                <div class="tl-card">
                  <div style="display:flex;justify-content:space-between;
                              align-items:flex-start;flex-wrap:wrap;gap:0.4rem;">
                    <div>
                      <div style="font-weight:700;color:var(--text);">
                        � Pending Request
                      </div>
                      <div style="color:var(--text-muted);font-size:0.82rem;margin-top:0.2rem;">
                        🎓 {b.get('student_name', 'N/A')} &nbsp;·&nbsp; 📅 {b.get('scheduled_date', 'N/A')}
                        &nbsp;·&nbsp; 🕐 {b.get('start_time', 'N/A')}
                      </div>
                    </div>
                    <span class="badge badge-pending">Pending</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            if st.button("📋 Manage All Requests", use_container_width=True, key="tdash_reqs"):
                nav_to("booking_requests")
        else:
            st.markdown("""
            <div class="tl-card" style="text-align:center;padding:1.8rem;">
              <div style="font-size:1.8rem;">📭</div>
              <div style="color:var(--text-muted);font-size:0.88rem;margin-top:0.4rem;">No pending requests.</div>
            </div>
            """, unsafe_allow_html=True)

        section("📅 Upcoming Confirmed Sessions")
        if accepted_list:
            for b in accepted_list[:4]:
                st.markdown(f"""
                <div class="tl-card">
                  <div style="display:flex;justify-content:space-between;
                              align-items:center;flex-wrap:wrap;gap:0.4rem;">
                    <div>
                      <div style="font-weight:700;color:var(--text);">
                        � Confirmed Session
                      </div>
                      <div style="color:var(--text-muted);font-size:0.82rem;">
                        🎓 {b.get('student_name', 'N/A')} · 📅 {b.get('scheduled_date', 'N/A')} · 🕐 {b.get('start_time', 'N/A')}
                      </div>
                    </div>
                    <span class="badge badge-accepted">Confirmed</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:var(--text-dim);font-size:0.83rem;'>No confirmed sessions yet.</div>",
                        unsafe_allow_html=True)

    with col_right:
        section("⚡ Quick Actions")
        actions = [
            ("📋 Booking Requests",    "booking_requests"),
            ("🗓️ Manage Availability", "manage_availability"),
            ("👤 Edit Profile",        "tutor_profile"),
            ("📅 Upcoming Sessions",   "upcoming_sessions"),
            ("⭐ Reviews",             "reviews"),
        ]
        for lbl, pg in actions:
            if st.button(lbl, use_container_width=True, key=f"qa_{pg}"):
                nav_to(pg)

        if profile:
            st.markdown("<br>", unsafe_allow_html=True)
            section("👤 Profile Snapshot")
            rating = profile.get("rating") or 0
            st.markdown(f"""
            <div class="tl-card" style="text-align:center;">
              <div class="avatar-ring" style="margin:0 auto 0.6rem;">👨‍🏫</div>
              <div style="font-family:'Syne',sans-serif;font-weight:700;color:var(--text);">
                {user['full_name']}
              </div>
              <div style="color:var(--primary);font-size:0.8rem;margin:3px 0;">
                {profile.get('specialization') or 'Coach'}
              </div>
              <div>{stars_html(rating)}
                <span style="color:var(--text-dim);font-size:0.72rem;"> {rating:.1f}</span>
              </div>
              <div style="color:var(--text-dim);font-size:0.78rem;margin-top:0.4rem;">
                {profile.get('experience_years') or 0} yrs · ₹{profile.get('hourly_rate') or 0}/hr
              </div>
            </div>
            """, unsafe_allow_html=True)

        if reviews:
            st.markdown("<br>", unsafe_allow_html=True)
            section("⭐ Latest Reviews")
            for r in reviews[:3]:
                st.markdown(f"""
                <div class="tl-card" style="padding:1rem 1.2rem;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-weight:600;color:var(--text);font-size:0.88rem;">
                      {r['student_name']}
                    </div>
                    <div>{stars_html(r['rating'])}</div>
                  </div>
                  <div style="color:var(--text-muted);font-size:0.8rem;margin-top:0.3rem;">
                    {r.get('comment') or '—'}
                  </div>
                </div>
                """, unsafe_allow_html=True)
