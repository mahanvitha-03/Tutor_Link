"""
manage_availability.py — Tutor manually sets available time slots

FEATURES:
  - Date picker + start/end time inputs (mandatory)
  - Overlap validation
  - List of existing slots with delete option
  - Slots shown on Browse Tutors page for students to book
"""

import streamlit as st
import datetime
from auth import get_current_user
from database import (
    add_availability_slot, get_slots_for_tutor, delete_availability_slot
)


def render():
    user = get_current_user()

    # ── Back navigation ──
    if st.button("← Back to Dashboard", key="back_avail"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="tl-header">
        <h1>🗓️ Manage Availability</h1>
        <p>Add time slots so students can book sessions with you.</p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_list = st.columns([1, 1])

    # ─────────────────────────
    # LEFT: Add New Slot Form
    # ─────────────────────────
    with col_form:
        st.markdown("### ➕ Add a New Time Slot")
        st.markdown("""
        <div style="background:rgba(108,99,255,0.07); border:1px solid var(--border);
                    border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
            <div style="font-size:0.85rem; color:var(--text-muted);">
                ℹ️ All fields are <b>mandatory</b>. Students will only see your available (unbooked) future slots.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Date (mandatory) ──
        slot_date = st.date_input(
            "📅 Date *",
            min_value=datetime.date.today(),
            value=datetime.date.today() + datetime.timedelta(days=1),
            key="new_slot_date"
        )

        # ── Time pickers (mandatory) ──
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            start_hour = st.selectbox(
                "⏰ Start Time * (hour)",
                [f"{h:02d}" for h in range(6, 23)],
                index=3,  # default 09:00
                key="start_hour"
            )
            start_min = st.selectbox("Start (min)", ["00", "15", "30", "45"], key="start_min")
        with t_col2:
            end_hour = st.selectbox(
                "⏰ End Time * (hour)",
                [f"{h:02d}" for h in range(6, 23)],
                index=4,  # default 10:00
                key="end_hour"
            )
            end_min = st.selectbox("End (min)", ["00", "15", "30", "45"], key="end_min")

        start_time = f"{start_hour}:{start_min}"
        end_time   = f"{end_hour}:{end_min}"

        # ── Duration preview ──
        try:
            st_dt = datetime.datetime.strptime(start_time, "%H:%M")
            et_dt = datetime.datetime.strptime(end_time,   "%H:%M")
            duration_mins = int((et_dt - st_dt).total_seconds() / 60)
            if duration_mins > 0:
                st.markdown(f"<div style='color:var(--success); font-size:0.85rem;'>⏱ Duration: {duration_mins} minutes</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:var(--danger); font-size:0.85rem;'>⚠️ End time must be after start time</div>",
                            unsafe_allow_html=True)
        except Exception:
            pass

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("✅ Add Slot", use_container_width=True, key="add_slot_btn"):
            # ── Mandatory validation ──
            errors = []
            if not slot_date:
                errors.append("Date is required.")
            if start_time >= end_time:
                errors.append("End time must be after start time.")

            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                result = add_availability_slot(
                    tutor_id=user["id"],
                    slot_date=str(slot_date),
                    start_time=start_time,
                    end_time=end_time
                )
                if result == "overlap":
                    st.warning("⚠️ This slot overlaps with an existing slot on the same date. Please choose a different time.")
                elif result is None:
                    st.error("❌ Invalid time range. End time must be after start time.")
                else:
                    st.success(f"✅ Slot added: {slot_date} | {start_time} – {end_time}")
                    st.rerun()

    # ─────────────────────────
    # RIGHT: Existing Slots
    # ─────────────────────────
    with col_list:
        st.markdown("### 📋 Your Slots")

        all_slots = get_slots_for_tutor(user["id"])
        upcoming  = [s for s in all_slots if s["slot_date"] >= str(datetime.date.today())]
        past      = [s for s in all_slots if s["slot_date"] < str(datetime.date.today())]

        # ── Stats ──
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("📆 Total", len(all_slots))
        with s2:
            st.metric("✅ Available", sum(1 for s in upcoming if not s["is_booked"]))
        with s3:
            st.metric("🔒 Booked", sum(1 for s in all_slots if s["is_booked"]))

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Upcoming Slots ──
        if upcoming:
            st.markdown("**📅 Upcoming Slots**")
            for slot in upcoming:
                is_booked = slot["is_booked"]
                status_badge = (
                    '<span class="badge badge-accepted">AVAILABLE</span>'
                    if not is_booked else
                    '<span class="badge badge-pending">BOOKED</span>'
                )
                st.markdown(f"""
                <div class="tl-card" style="padding:1rem 1.2rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                        <div>
                            <div style="font-weight:700; color:var(--text);">📅 {slot['slot_date']}</div>
                            <div style="color:var(--text-muted); font-size:0.85rem;">
                                ⏰ {slot['start_time']} – {slot['end_time']}
                            </div>
                        </div>
                        {status_badge}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if not is_booked:
                    if st.button("🗑️ Delete", key=f"del_slot_{slot['id']}", help="Remove this slot"):
                        deleted = delete_availability_slot(slot["id"], user["id"])
                        if deleted:
                            st.success("Slot deleted.")
                            st.rerun()
                        else:
                            st.error("Could not delete slot.")
        else:
            st.markdown("""
            <div class="tl-card" style="text-align:center; padding:2rem;">
                <div style="font-size:2rem;">📭</div>
                <div style="color:var(--text-muted);">No upcoming slots. Add one on the left!</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Past Slots (collapsed) ──
        if past:
            with st.expander(f"📂 Past Slots ({len(past)})"):
                for slot in past:
                    st.markdown(f"""
                    <div style="padding:0.5rem 0; border-bottom:1px solid var(--border); font-size:0.85rem; color:var(--text-muted);">
                        📅 {slot['slot_date']} &nbsp; ⏰ {slot['start_time']}–{slot['end_time']}
                        &nbsp; {'🔒 Booked' if slot['is_booked'] else '✅ Was available'}
                    </div>
                    """, unsafe_allow_html=True)
