"""
browse_tutors.py — Browse & book tutors  (TutorLink v3)

Smart features:
  • subject_match_tutors() sorts tutors by subject relevance
  • Recommended Slots widget (scored by hour popularity + time-of-day)
  • "Next Available" one-click slot highlight
  • Timeline-style slot cards instead of plain dropdown
  • Tutor cards with avatar ring, inline rating, and skill chips
"""

import streamlit as st
import datetime
from auth import get_current_user
from database import (
    get_all_tutors, create_booking, get_slots_for_tutor,
    create_notification, ALL_SUBJECTS,
    subject_match_tutors, get_recommended_slots, get_next_available_slot,
)
from app import render_back_button, tl_header, section, badge, stars_html


# ── Helper ─────────────────────────────────────────────────────────────────────
def _skill_chips(skills_str: str, limit: int = 5) -> str:
    if not skills_str:
        return ""
    chips = ""
    for s in skills_str.split(",")[:limit]:
        s = s.strip()
        if s:
            chips += (
                f'<span style="display:inline-block;background:var(--surface2);'
                f'border:1px solid var(--border);border-radius:999px;'
                f'padding:1px 9px;font-size:0.72rem;color:var(--text-muted);margin:2px;">'
                f'{s}</span>'
            )
    return chips


def render():
    user = get_current_user()
    render_back_button("← Dashboard", "dashboard")
    tl_header("🔍", "Browse Tutors",
              "Find the right expert — smart slot recommendations included.")

    # ── Search + filters ──────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 1])
    with fc1:
        search = st.text_input("", placeholder="🔎  Search by name, skill or subject…",
                               label_visibility="collapsed", key="bt_search")
    with fc2:
        all_tutors_raw = get_all_tutors()
        specs = ["All Specializations"] + sorted({
            t.get("specialization") or "General"
            for t in all_tutors_raw if t.get("specialization")
        })
        spec_filter = st.selectbox("", specs, label_visibility="collapsed", key="bt_spec")
    with fc3:
        subject_filter = st.selectbox("", ["All Subjects"] + ALL_SUBJECTS,
                                      label_visibility="collapsed", key="bt_subj")
    with fc4:
        sort_by = st.selectbox("", ["⭐ Rating", "💰 Rate ↑", "🕐 Experience"],
                               label_visibility="collapsed", key="bt_sort")

    # Smart: sort by subject match first
    tutors = subject_match_tutors(
        subject_filter if subject_filter != "All Subjects" else ""
    )

    # Then apply text search
    if search:
        s = search.lower()
        tutors = [t for t in tutors if
                  s in (t.get("full_name") or "").lower() or
                  s in (t.get("skills") or "").lower() or
                  s in (t.get("specialization") or "").lower()]
    if spec_filter != "All Specializations":
        tutors = [t for t in tutors if t.get("specialization") == spec_filter]

    # Secondary sort
    if sort_by == "💰 Rate ↑":
        tutors.sort(key=lambda t: t.get("hourly_rate") or 0)
    elif sort_by == "🕐 Experience":
        tutors.sort(key=lambda t: t.get("experience_years") or 0, reverse=True)

    # Subject-match notice
    if subject_filter != "All Subjects":
        st.markdown(
            f'<div class="rec-strip">✦ Results sorted by match for <b>{subject_filter}</b> — '
            f'tutors with this skill appear first.</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f"<div style='color:var(--text-dim);font-size:0.82rem;margin-bottom:1rem;'>"
        f"{len(tutors)} tutor{'s' if len(tutors)!=1 else ''} found</div>",
        unsafe_allow_html=True
    )

    if "booking_tutor_id" not in st.session_state:
        st.session_state["booking_tutor_id"] = None

    for tutor in tutors:
        _render_tutor_card(user, tutor)


def _render_tutor_card(user, tutor):
    rating   = tutor.get("rating") or 0
    reviews  = tutor.get("total_reviews") or 0
    skills   = tutor.get("skills") or ""
    next_slot = get_next_available_slot(tutor["id"])

    # ── Card HTML ──
    next_slot_html = ""
    if next_slot:
        next_slot_html = (
            f'<div style="margin-top:0.5rem;">'
            f'<span class="badge badge-accepted">⚡ Next Available</span>'
            f'<span style="color:var(--text-muted);font-size:0.8rem;margin-left:8px;">'
            f'{next_slot["slot_date"]} · {next_slot["start_time"]}–{next_slot["end_time"]}'
            f'</span></div>'
        )

    st.markdown(f"""
    <div class="tl-card">
      <div style="display:flex;gap:1.2rem;align-items:flex-start;">
        <div class="avatar-ring">👨‍🏫</div>
        <div style="flex:1;min-width:0;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.4rem;">
            <div>
              <div style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:700;
                          color:var(--text);">{tutor['full_name']}</div>
              <div style="color:var(--primary);font-size:0.82rem;margin-top:2px;">
                {tutor.get('specialization') or 'Personal Development Coach'}
              </div>
            </div>
            <div style="text-align:right;flex-shrink:0;">
              <div>{stars_html(rating)}</div>
              <div style="color:var(--text-dim);font-size:0.73rem;">{rating:.1f}/5 · {reviews} reviews</div>
            </div>
          </div>
          <div style="color:var(--text-muted);font-size:0.85rem;margin:0.6rem 0;line-height:1.55;">
            {(tutor.get('bio') or 'No bio provided yet.')[:220]}
          </div>
          <div style="display:flex;gap:1.25rem;flex-wrap:wrap;font-size:0.8rem;color:var(--text-dim);">
            <span>⏳ {tutor.get('experience_years') or 0} yrs</span>
            <span style="color:var(--success);font-weight:600;">₹{tutor.get('hourly_rate') or 0}/hr</span>
          </div>
          <div style="margin-top:0.5rem;">{_skill_chips(skills)}</div>
          {next_slot_html}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_book, col_quick, _ = st.columns([1.3, 1.5, 4])
    with col_book:
        if st.button("📅 Book Session", key=f"book_{tutor['id']}"):
            if st.session_state["booking_tutor_id"] == tutor["id"]:
                st.session_state["booking_tutor_id"] = None
            else:
                st.session_state["booking_tutor_id"] = tutor["id"]

    with col_quick:
        if next_slot and st.button("⚡ Book Next Slot", key=f"quick_{tutor['id']}"):
            # Pre-select the next slot in the booking form
            st.session_state["booking_tutor_id"] = tutor["id"]
            st.session_state[f"preselect_slot_{tutor['id']}"] = next_slot["id"]

    if st.session_state.get("booking_tutor_id") == tutor["id"]:
        _render_booking_form(user, tutor)

    st.markdown("<div style='margin-bottom:0.4rem;'></div>", unsafe_allow_html=True)


def _render_booking_form(user, tutor):
    available_slots  = get_slots_for_tutor(tutor["id"])
    recommended_slots = get_recommended_slots(tutor["id"], limit=3)
    rec_ids = {s["id"] for s in recommended_slots}

    preselect = st.session_state.pop(f"preselect_slot_{tutor['id']}", None)

    st.markdown(f"""
    <div style="background:rgba(124,111,255,0.06);border:1px solid var(--border);
                border-radius:14px;padding:1.5rem 1.75rem;margin:0.5rem 0 1rem;">
      <div style="font-family:'Syne',sans-serif;font-weight:700;color:var(--primary);
                  margin-bottom:1.2rem;font-size:1rem;">
        Book a Session with {tutor['full_name']}
      </div>
    """, unsafe_allow_html=True)

    # ── Recommended slot banner ────────────────────────────────────────────────
    if recommended_slots:
        rec = recommended_slots[0]
        st.markdown(f"""
        <div class="rec-strip">
          ✦ <b>Recommended:</b>&nbsp; 📅 {rec['slot_date']}
          &nbsp; 🕐 {rec['start_time']}–{rec['end_time']}
          &nbsp;·&nbsp; Popular time slot
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Slot picker ────────────────────────────────────────────────────────────
    if available_slots:
        section("🗓️ Select a Time Slot")

        def _slot_label(s):
            marker = " ✦ Recommended" if s["id"] in rec_ids else ""
            return f"📅 {s['slot_date']}  🕐 {s['start_time']} – {s['end_time']}{marker}"

        default_idx = 0
        if preselect:
            ids = [s["id"] for s in available_slots]
            if preselect in ids:
                default_idx = ids.index(preselect)

        chosen_idx = st.selectbox(
            "Available slots",
            range(len(available_slots)),
            format_func=lambda i: _slot_label(available_slots[i]),
            index=default_idx,
            key=f"slot_sel_{tutor['id']}",
            label_visibility="collapsed"
        )
        selected_slot = available_slots[chosen_idx]
        session_date_str = selected_slot["slot_date"]
        session_time_str = f"{selected_slot['start_time']} – {selected_slot['end_time']}"

        # Slot confirmation chip
        is_rec = selected_slot["id"] in rec_ids
        rec_txt = ' <span class="badge badge-rec">✦ Recommended</span>' if is_rec else ""
        st.markdown(f"""
        <div style="background:rgba(45,212,191,0.08);border:1px solid rgba(45,212,191,0.25);
                    border-radius:8px;padding:0.55rem 1rem;font-size:0.83rem;margin-bottom:0.8rem;">
          ✅ <b>Selected:</b> {session_date_str} &nbsp;·&nbsp; {session_time_str} {rec_txt}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback: manual entry
        st.markdown("""
        <div style="background:rgba(251,188,4,0.09);border:1px solid rgba(251,188,4,0.3);
                    border-radius:8px;padding:0.6rem 1rem;font-size:0.83rem;margin-bottom:0.8rem;">
          ⚠️ No availability slots set yet — enter a preferred date and time.
        </div>
        """, unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            session_date = st.date_input("Date *", min_value=datetime.date.today(),
                                         key=f"fb_date_{tutor['id']}")
            session_date_str = str(session_date)
        with b2:
            session_time_str = st.selectbox("Preferred Time *", [
                "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
                "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM"
            ], key=f"fb_time_{tutor['id']}")
        selected_slot = None

    # ── Subject + Topic ────────────────────────────────────────────────────────
    sa, sb = st.columns(2)
    with sa:
        subject = st.selectbox("Subject *", ALL_SUBJECTS, key=f"subj_{tutor['id']}")
    with sb:
        topic = st.text_input("Specific Goal", placeholder="e.g. Prepare for TCS interview",
                              key=f"topic_{tutor['id']}")

    # ── Note ──────────────────────────────────────────────────────────────────
    note = st.text_area("Additional Notes", placeholder="Anything to mention…",
                        key=f"note_{tutor['id']}", height=68)

    # ── Booking summary ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;
                padding:0.75rem 1.1rem;font-size:0.82rem;color:var(--text-muted);margin:0.5rem 0 0.75rem;">
      <b style="color:var(--text);">📋 Booking Summary</b><br>
      Subject: <b style="color:var(--text);">{subject}</b> &nbsp;·&nbsp;
      Tutor: <b style="color:var(--text);">{tutor['full_name']}</b> &nbsp;·&nbsp;
      ₹{tutor.get('hourly_rate') or 0}/hr &nbsp;·&nbsp;
      <span style="color:var(--warning);">Status: Pending until tutor accepts</span>
    </div>
    """, unsafe_allow_html=True)

    bc1, bc2 = st.columns(2)
    with bc1:
        if st.button("✅ Confirm Booking", key=f"confirm_{tutor['id']}",
                     use_container_width=True):
            errors = []
            if not subject:         errors.append("Subject is required.")
            if not session_date_str: errors.append("Date is required.")
            if not session_time_str: errors.append("Time is required.")

            for e in errors:
                st.error(f"❌ {e}")

            if not errors:
                bid = create_booking(
                    student_id      = user["id"],
                    tutor_id        = tutor["id"],
                    slot_id         = selected_slot["id"] if selected_slot else None,
                    scheduled_date  = session_date_str,
                    start_time      = session_time_str,
                    end_time        = session_time_str,  # 1-hour session assumed
                )
                if bid:
                    create_notification(user["id"], "Booking Sent",
                        f"Your session with {tutor['full_name']} on {session_date_str} "
                        f"at {session_time_str} is pending confirmation.")
                    create_notification(tutor["id"], "New Booking Request",
                        f"{user['full_name']} requested a {subject} session on "
                        f"{session_date_str} at {session_time_str}.")
                    st.success("🎉 Booking request sent! Awaiting tutor confirmation.")
                    st.balloons()
                    st.session_state["booking_tutor_id"] = None
                    st.rerun()
                else:
                    st.error("Something went wrong. Please try again.")
    with bc2:
        if st.button("✕ Cancel", key=f"cancel_{tutor['id']}", use_container_width=True):
            st.session_state["booking_tutor_id"] = None
            st.rerun()
