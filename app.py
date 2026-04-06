"""
app.py — TutorLink v3 entry point
Run with: streamlit run app.py

What's new vs v2:
  • Completely redesigned CSS — editorial/magazine aesthetic, Syne + DM Sans fonts
  • Animated hero on the login page
  • Active-page highlight in sidebar
  • Smooth page transitions via CSS animation
  • Centralized theme engine with zero colour duplication
  • Smart recommendation widgets injected from app-level
"""

import streamlit as st
from database import init_db, update_user_theme, get_unread_count
from auth import is_logged_in, get_current_user, login_user, register_user, set_session, logout

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TutorLink",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()


# ══════════════════════════════════════════════════════════════════════════════
# THEME ENGINE
# ══════════════════════════════════════════════════════════════════════════════

_DARK = dict(
    bg="#0C0C18", surface="#13132A", surface2="#1A1A35", surface3="#20204A",
    text="#EEEEFF", text_muted="#8080AA", text_dim="#505078",
    border="rgba(120,100,255,0.18)", border_strong="rgba(120,100,255,0.45)",
    primary="#7C6FFF", primary_dark="#5C50DD", primary_glow="rgba(124,111,255,0.25)",
    accent="#36D9C8", warning="#FBBC04", danger="#FF6B7A", success="#2DD4BF",
    card="#181830", card_hover="#1E1E40",
    input_bg="#1A1A35", scrollbar="#7C6FFF",
    sidebar="#111126",
    gradient_start="#7C6FFF", gradient_end="#36D9C8",
)

_LIGHT = dict(
    bg="#F5F5FF", surface="#FFFFFF", surface2="#EEEEFF", surface3="#E4E4F8",
    text="#18183A", text_muted="#5A5A80", text_dim="#9090B8",
    border="rgba(100,80,220,0.15)", border_strong="rgba(100,80,220,0.4)",
    primary="#6050EE", primary_dark="#4838CC", primary_glow="rgba(96,80,238,0.18)",
    accent="#0AB5A6", warning="#D97706", danger="#DC2626", success="#0D9488",
    card="#FFFFFF", card_hover="#F0F0FF",
    input_bg="#F0F0FF", scrollbar="#6050EE",
    sidebar="#FAFAFF",
    gradient_start="#6050EE", gradient_end="#0AB5A6",
)


def _get_theme() -> str:
    return st.session_state.get("theme_override", "dark")


def _palette() -> dict:
    return _DARK if _get_theme() == "dark" else _LIGHT


def inject_css():
    p = _palette()
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

/* ── Design tokens ── */
:root {{
  --bg:          {p['bg']};
  --surface:     {p['surface']};
  --surface2:    {p['surface2']};
  --surface3:    {p['surface3']};
  --text:        {p['text']};
  --text-muted:  {p['text_muted']};
  --text-dim:    {p['text_dim']};
  --border:      {p['border']};
  --border-s:    {p['border_strong']};
  --primary:     {p['primary']};
  --primary-dk:  {p['primary_dark']};
  --primary-glow:{p['primary_glow']};
  --accent:      {p['accent']};
  --warning:     {p['warning']};
  --danger:      {p['danger']};
  --success:     {p['success']};
  --card:        {p['card']};
  --card-hover:  {p['card_hover']};
  --input-bg:    {p['input_bg']};
  --sidebar:     {p['sidebar']};
  --grad-a:      {p['gradient_start']};
  --grad-b:      {p['gradient_end']};
  --radius:      14px;
  --radius-sm:   8px;
  --shadow:      0 4px 24px rgba(0,0,0,0.12);
  --shadow-lg:   0 12px 48px rgba(0,0,0,0.18);
}}

/* ── Base ── */
html, body, .stApp {{
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}}

/* ── Page fade-in ── */
.main .block-container {{
  animation: fadein 0.35s ease;
  padding-top: 1.5rem !important;
}}
@keyframes fadein {{
  from {{ opacity: 0; transform: translateY(6px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: var(--sidebar) !important;
  border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
[data-testid="stSidebar"] .stButton > button {{
  background: transparent !important;
  border: 1px solid var(--border) !important;
  color: var(--text-muted) !important;
  box-shadow: none !important;
  text-align: left !important;
  justify-content: flex-start !important;
  font-weight: 500 !important;
  transition: all 0.15s !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  background: var(--primary-glow) !important;
  border-color: var(--border-s) !important;
  color: var(--text) !important;
  transform: none !important;
}}
/* Active nav item */
[data-testid="stSidebar"] .nav-active .stButton > button {{
  background: linear-gradient(135deg, var(--primary), var(--primary-dk)) !important;
  border-color: transparent !important;
  color: white !important;
  box-shadow: 0 4px 16px var(--primary-glow) !important;
}}

/* ── Primary button ── */
.stButton > button {{
  background: linear-gradient(135deg, var(--primary), var(--primary-dk)) !important;
  color: white !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  padding: 0.55rem 1.4rem !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.9rem !important;
  transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1) !important;
  box-shadow: 0 3px 12px var(--primary-glow) !important;
  letter-spacing: 0.01em !important;
}}
.stButton > button:hover {{
  transform: translateY(-2px) scale(1.01) !important;
  box-shadow: 0 8px 24px var(--primary-glow) !important;
}}
.stButton > button:active {{
  transform: translateY(0) scale(0.99) !important;
}}

/* ── Form inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stMultiSelect > div > div {{
  background: var(--input-bg) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px var(--primary-glow) !important;
  outline: none !important;
}}
label, .stMarkdown p {{ color: var(--text-muted) !important; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  background: var(--surface2) !important;
  border-radius: var(--radius) !important;
  padding: 4px !important;
  gap: 4px !important;
  border: 1px solid var(--border) !important;
}}
.stTabs [data-baseweb="tab"] {{
  border-radius: var(--radius-sm) !important;
  color: var(--text-muted) !important;
  font-weight: 600 !important;
  font-family: 'DM Sans', sans-serif !important;
  padding: 0.4rem 1rem !important;
}}
.stTabs [aria-selected="true"] {{
  background: linear-gradient(135deg,var(--primary),var(--primary-dk)) !important;
  color: white !important;
  box-shadow: 0 3px 12px var(--primary-glow) !important;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1rem 1.2rem !important;
  transition: border-color 0.2s, transform 0.2s !important;
}}
[data-testid="stMetric"]:hover {{
  border-color: var(--border-s) !important;
  transform: translateY(-1px) !important;
}}
[data-testid="stMetricValue"] {{ color: var(--text) !important; font-family: 'Syne', sans-serif !important; }}
[data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; font-size: 0.8rem !important; }}

/* ── Cards ── */
.tl-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  margin-bottom: 0.9rem;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}}
.tl-card::after {{
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--primary-glow) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}}
.tl-card:hover {{
  border-color: var(--border-s);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}}
.tl-card:hover::after {{ opacity: 0.4; }}

/* Recommended card — glowing outline */
.tl-card-recommended {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 1px var(--accent), 0 8px 32px rgba(54,217,200,0.15) !important;
}}

/* ── Page header ── */
.tl-header {{
  background: linear-gradient(140deg, var(--surface) 0%, var(--surface3) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem 2.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}}
.tl-header::before {{
  content: '';
  position: absolute;
  top: -80px; right: -80px;
  width: 280px; height: 280px;
  background: radial-gradient(circle, var(--primary-glow) 0%, transparent 70%);
  border-radius: 50%;
}}
.tl-header::after {{
  content: '';
  position: absolute;
  bottom: -60px; left: 30%;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(54,217,200,0.08) 0%, transparent 70%);
  border-radius: 50%;
}}
.tl-header h1 {{
  font-family: 'Syne', sans-serif !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
  color: var(--text) !important;
  margin: 0 !important;
  letter-spacing: -0.02em !important;
  position: relative; z-index: 1;
}}
.tl-header p {{
  color: var(--text-muted) !important;
  margin-top: 0.4rem !important;
  font-size: 0.95rem !important;
  position: relative; z-index: 1;
}}

/* ── Badges ── */
.badge {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-family: 'DM Sans', sans-serif;
}}
.badge-pending   {{ background:rgba(251,188,4,0.15);   color:var(--warning); border:1px solid rgba(251,188,4,0.3); }}
.badge-accepted  {{ background:rgba(45,212,191,0.15);  color:var(--success); border:1px solid rgba(45,212,191,0.3); }}
.badge-rejected  {{ background:rgba(255,107,122,0.15); color:var(--danger);  border:1px solid rgba(255,107,122,0.3); }}
.badge-completed {{ background:rgba(124,111,255,0.15); color:var(--primary); border:1px solid rgba(124,111,255,0.3); }}
.badge-pay-pend  {{ background:rgba(251,188,4,0.12);   color:var(--warning); border:1px solid rgba(251,188,4,0.25); }}
.badge-paid      {{ background:rgba(45,212,191,0.12);  color:var(--success); border:1px solid rgba(45,212,191,0.25); }}
.badge-rec       {{ background:rgba(54,217,200,0.15);  color:var(--accent);  border:1px solid rgba(54,217,200,0.4); }}

/* ── Recommend strip ── */
.rec-strip {{
  background: linear-gradient(90deg, rgba(54,217,200,0.08), rgba(124,111,255,0.08));
  border: 1px solid rgba(54,217,200,0.25);
  border-radius: var(--radius-sm);
  padding: 0.5rem 1rem;
  font-size: 0.82rem;
  color: var(--accent);
  margin-bottom: 0.6rem;
}}

/* ── Notification cards ── */
.notif-card {{
  background: var(--card);
  border-left: 4px solid var(--primary);
  border-radius: var(--radius-sm);
  padding: 0.85rem 1.2rem;
  margin-bottom: 0.55rem;
  font-size: 0.87rem;
  transition: border-color 0.2s;
}}
.notif-unread   {{ border-left-color: var(--accent); background: rgba(54,217,200,0.05); }}
.notif-success  {{ border-left-color: var(--success); }}
.notif-warning  {{ border-left-color: var(--warning); }}
.notif-reminder {{ border-left-color: var(--danger); }}

/* ── Reminder banner ── */
.reminder-today    {{ background:rgba(255,107,122,0.1); border:1px solid rgba(255,107,122,0.3); border-radius:var(--radius-sm); padding:0.8rem 1.2rem; margin-bottom:0.6rem; }}
.reminder-tomorrow {{ background:rgba(251,188,4,0.08);  border:1px solid rgba(251,188,4,0.25);  border-radius:var(--radius-sm); padding:0.8rem 1.2rem; margin-bottom:0.6rem; }}

/* ── Section heading ── */
.tl-section {{
  font-family: 'Syne', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
  margin: 1.4rem 0 0.75rem;
}}

/* ── Slot timeline pill ── */
.slot-pill {{
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.3rem 0.9rem;
  font-size: 0.8rem; color: var(--text);
  transition: border-color 0.15s, background 0.15s;
}}
.slot-pill:hover {{
  border-color: var(--border-s);
  background: var(--surface3);
}}
.slot-pill-free   {{ border-color: rgba(45,212,191,0.4);  color: var(--success); }}
.slot-pill-booked {{ border-color: rgba(255,107,122,0.35); color: var(--danger); text-decoration: line-through; opacity: 0.7; }}

/* ── Progress bar ── */
.prog-bar-wrap {{ background: var(--surface2); border-radius: 999px; height: 7px; overflow: hidden; }}
.prog-bar      {{ height: 100%; border-radius: 999px; transition: width 0.6s cubic-bezier(0.34,1.56,0.64,1); }}

/* ── Global misc ── */
hr {{ border-color: var(--border) !important; margin: 1.2rem 0 !important; }}
.stExpander {{ border-color: var(--border) !important; border-radius: var(--radius) !important; }}
details summary {{ color: var(--text) !important; font-weight: 600 !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--primary); border-radius: 3px; }}

/* ── Back button variant ── */
.back-wrap .stButton > button {{
  background: transparent !important;
  border: 1px solid var(--border) !important;
  color: var(--text-muted) !important;
  box-shadow: none !important;
  font-size: 0.83rem !important;
  padding: 0.3rem 0.8rem !important;
}}
.back-wrap .stButton > button:hover {{
  border-color: var(--border-s) !important;
  color: var(--primary) !important;
  transform: none !important;
}}

/* ── Tutor card avatar ring ── */
.avatar-ring {{
  width: 58px; height: 58px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; flex-shrink: 0;
  box-shadow: 0 4px 16px var(--primary-glow);
}}

/* ── Star rating ── */
.stars {{ color: var(--warning); letter-spacing: 1px; }}

/* ── Hero gradient text ── */
.hero-brand {{
  font-family: 'Syne', sans-serif;
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--grad-a), var(--grad-b));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
  letter-spacing: -0.03em;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def nav_to(page: str):
    st.session_state["prev_page"] = st.session_state.get("page", "dashboard")
    st.session_state["page"] = page
    st.rerun()


def render_back_button(label="← Back", target: str | None = None):
    dest = target or st.session_state.get("prev_page", "dashboard")
    st.markdown('<div class="back-wrap">', unsafe_allow_html=True)
    if st.button(label, key=f"back_{dest}_{label}"):
        st.session_state["page"] = dest
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def tl_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="tl-header">
      <h1>{icon} {title}</h1>
      {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def section(text: str):
    st.markdown(f'<div class="tl-section">{text}</div>', unsafe_allow_html=True)


def badge(label: str, cls: str = "badge-completed"):
    return f'<span class="badge {cls}">{label}</span>'


def stars_html(rating: float) -> str:
    full = int(rating)
    empty = 5 - full
    return f'<span class="stars">{"⭐" * full}{"☆" * empty}</span>'


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    user  = get_current_user()
    theme = _get_theme()
    unread = get_unread_count(user["id"])

    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="text-align:center;padding:1.25rem 0 0.75rem;">
          <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;
                      background:linear-gradient(135deg,var(--grad-a),var(--grad-b));
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                      background-clip:text;">TutorLink</div>
          <div style="font-size:0.7rem;color:var(--text-dim);letter-spacing:1.5px;
                      text-transform:uppercase;margin-top:1px;">Connect · Learn · Grow</div>
        </div>
        """, unsafe_allow_html=True)

        # Theme toggle
        col_t, col_btn = st.columns([3, 1])
        with col_t:
            st.markdown(
                f"<div style='font-size:0.78rem;color:var(--text-dim);padding-top:8px;'>"
                f"{'🌙 Dark' if theme=='dark' else '☀️ Light'} Mode</div>",
                unsafe_allow_html=True
            )
        with col_btn:
            if st.button("☀️" if theme == "dark" else "🌙", key="theme_toggle",
                         help="Toggle theme"):
                new = "light" if theme == "dark" else "dark"
                st.session_state["theme_override"] = new
                update_user_theme(user["id"], new)
                st.rerun()

        # User chip
        role_label = "🎓 Student" if user["role"] == "student" else "👨‍🏫 Tutor"
        st.markdown(f"""
        <div style="background:var(--primary-glow);border:1px solid var(--border-s);
                    border-radius:10px;padding:0.7rem 1rem;margin:0.75rem 0;">
          <div style="font-size:0.72rem;color:var(--text-dim);">Signed in as</div>
          <div style="font-weight:700;color:var(--text);font-size:0.95rem;">{user['full_name']}</div>
          <div style="font-size:0.72rem;color:var(--primary);text-transform:uppercase;
                      letter-spacing:0.5px;margin-top:2px;">{role_label}</div>
        </div>
        """, unsafe_allow_html=True)

        # Notification bell
        bell_label = f"🔔 Notifications {'🔴' if unread else ''}"
        if unread:
            bell_label += f" ({unread})"
        if st.button(bell_label, use_container_width=True, key="nav_notifications"):
            nav_to("notifications")

        st.markdown("<hr>", unsafe_allow_html=True)

        current_page = st.session_state.get("page", "dashboard")

        if user["role"] == "student":
            _student_nav(current_page)
        else:
            _tutor_nav(current_page)

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True, key="logout_btn"):
            logout()
            st.rerun()


def _nav_btn(label: str, page: str, current_page: str):
    """Render a nav button; wraps in active class if current."""
    is_active = current_page == page
    if is_active:
        st.markdown('<div class="nav-active">', unsafe_allow_html=True)
    if st.button(label, use_container_width=True, key=f"nav_{page}"):
        nav_to(page)
    if is_active:
        st.markdown("</div>", unsafe_allow_html=True)


def _student_nav(current_page: str):
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:var(--text-dim);"
                "text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;'>"
                "Student</div>", unsafe_allow_html=True)
    for label, page in [
        ("🏠 Dashboard",         "dashboard"),
        ("🔍 Browse Tutors",     "browse_tutors"),
        ("📅 My Sessions",       "my_sessions"),
        ("📈 Progress Tracker",  "progress"),
        ("💬 Messages",          "messages"),
        ("🎥 Video Chat",        "video_chat"),
        ("⚙️ Account Settings",  "account_settings"),
    ]:
        _nav_btn(label, page, current_page)


def _tutor_nav(current_page: str):
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:var(--text-dim);"
                "text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;'>"
                "Tutor</div>", unsafe_allow_html=True)
    for label, page in [
        ("🏠 Dashboard",          "dashboard"),
        ("👤 My Profile",         "tutor_profile"),
        ("🗓️ Availability",       "manage_availability"),
        ("📋 Booking Requests",   "booking_requests"),
        ("📅 Upcoming Sessions",  "upcoming_sessions"),
        ("⭐ Reviews",            "reviews"),
        ("💬 Messages",           "messages"),
        ("🎥 Video Chat",         "video_chat"),
        ("⚙️ Account Settings",   "account_settings"),
    ]:
        _nav_btn(label, page, current_page)


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE  — redesigned hero
# ══════════════════════════════════════════════════════════════════════════════

def render_auth_page():
    inject_css()
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:3.5rem 0 2.5rem;">
          <div style="font-size:3rem;margin-bottom:0.5rem;">📚</div>
          <div class="hero-brand">TutorLink</div>
          <div style="color:var(--text-muted);margin-top:0.75rem;font-size:0.95rem;
                      letter-spacing:0.02em;">
            Connecting Students with Expert Tutors
          </div>
          <div style="display:flex;justify-content:center;gap:1.5rem;margin-top:1.25rem;
                      font-size:0.82rem;color:var(--text-dim);">
            <span>✦ 1-on-1 Sessions</span>
            <span>✦ Smart Scheduling</span>
            <span>✦ Progress Tracking</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["🔑 Sign In", "✨ Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username", key="li_user")
            password = st.text_input("Password", type="password",
                                     placeholder="Enter your password", key="li_pass")
            if st.button("Sign In →", use_container_width=True, key="login_btn"):
                ok, result = login_user(username, password)
                if ok:
                    set_session(result)
                    st.session_state["theme_override"] = result.get("theme", "dark")
                    st.session_state["page"] = "dashboard"
                    st.rerun()
                else:
                    st.error(f"❌ {result}")

        with tab_reg:
            st.markdown("<br>", unsafe_allow_html=True)
            reg_role  = st.selectbox("I am a…", ["student", "tutor"],
                                     format_func=lambda x: "🎓 Student" if x == "student" else "👨‍🏫 Tutor",
                                     key="rg_role")
            c1, c2 = st.columns(2)
            with c1:
                reg_name = st.text_input("Full Name", placeholder="Your name", key="rg_name")
            with c2:
                reg_email = st.text_input("Email", placeholder="you@email.com", key="rg_email")
            c_mobile = st.columns(1)[0]
            with c_mobile:
                reg_mobile = st.text_input("Mobile Number", placeholder="+91 9876543210", key="rg_mobile")
            reg_user  = st.text_input("Username", placeholder="Pick a username", key="rg_user")
            c3, c4 = st.columns(2)
            with c3:
                reg_pass  = st.text_input("Password", type="password",
                                           placeholder="Min. 6 chars", key="rg_pass")
            with c4:
                reg_pass2 = st.text_input("Confirm Password", type="password",
                                           placeholder="Repeat", key="rg_pass2")

            if st.button("Create Account →", use_container_width=True, key="reg_btn"):
                if reg_pass != reg_pass2:
                    st.error("❌ Passwords do not match.")
                else:
                    ok, result = register_user(reg_user, reg_pass, reg_role, reg_name, reg_email, reg_mobile)
                    if ok:
                        st.success("✅ Account created! Please sign in.")
                    else:
                        st.error(f"❌ {result}")


# ══════════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS PAGE
# ══════════════════════════════════════════════════════════════════════════════

def render_notifications_page():
    from database import get_notifications, mark_notification_read, mark_all_notifications_read
    user = get_current_user()

    render_back_button("← Dashboard", "dashboard")
    tl_header("🔔", "Notifications", "Stay informed about your sessions and bookings.")

    notifs = get_notifications(user["id"])
    if not notifs:
        st.markdown("""
        <div class="tl-card" style="text-align:center;padding:3rem;">
          <div style="font-size:2.5rem;margin-bottom:0.75rem;">🔕</div>
          <div style="color:var(--text-muted);">No notifications yet. You're all caught up!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    unread = [n for n in notifs if not n["is_read"]]
    if unread:
        if st.button(f"✅ Mark all {len(unread)} as read", key="mark_all"):
            mark_all_notifications_read(user["id"])
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    type_meta = {
        "info":     ("ℹ️", ""),
        "success":  ("✅", "notif-success"),
        "warning":  ("⚠️", "notif-warning"),
        "reminder": ("⏰", "notif-reminder"),
    }
    for n in notifs:
        icon, cls = type_meta.get(n["notif_type"], ("🔔", ""))
        unread_cls = "notif-unread" if not n["is_read"] else ""
        new_tag = ('<span style="background:var(--primary);color:white;font-size:0.65rem;'
                   'border-radius:999px;padding:1px 7px;margin-left:8px;vertical-align:middle;">NEW</span>'
                   if not n["is_read"] else "")
        st.markdown(f"""
        <div class="notif-card {cls} {unread_cls}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
            <div style="flex:1;">
              <div style="font-weight:700;color:var(--text);">{icon} {n['title']}{new_tag}</div>
              <div style="color:var(--text-muted);margin-top:0.3rem;line-height:1.5;">{n['message']}</div>
              <div style="font-size:0.73rem;color:var(--text-dim);margin-top:0.35rem;">{n['created_at'][:16]}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if not n["is_read"]:
            if st.button("Mark read", key=f"read_{n['id']}"):
                mark_notification_read(n["id"])
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    if not is_logged_in():
        render_auth_page()
        return

    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"

    inject_css()
    render_sidebar()

    user = get_current_user()
    page = st.session_state.get("page", "dashboard")

    if page == "notifications":
        render_notifications_page()
        return

    if user["role"] == "student":
        if page == "dashboard":      from student_dashboard   import render
        elif page == "browse_tutors":from browse_tutors        import render
        elif page == "my_sessions":  from my_sessions          import render
        elif page == "progress":     from progress_tracker     import render
        elif page == "messages":     from messages             import render
        elif page == "video_chat":    from video_chat          import render
        elif page == "account_settings": from account_settings import render
        else:                        from student_dashboard    import render
    else:
        if page == "dashboard":         from tutor_dashboard     import render
        elif page == "tutor_profile":   from tutor_profile       import render
        elif page == "manage_availability": from manage_availability import render
        elif page == "booking_requests":from booking_requests    import render
        elif page == "upcoming_sessions": from upcoming_sessions  import render
        elif page == "video_chat":      from video_chat         import render
        elif page == "reviews":         from reviews             import render
        elif page == "messages":        from messages            import render
        elif page == "account_settings": from account_settings  import render
        else:                           from tutor_dashboard     import render

    render()


if __name__ == "__main__":
    main()
