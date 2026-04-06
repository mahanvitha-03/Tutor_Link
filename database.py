import sqlite3
from datetime import date

DB_PATH = "tutorlink.db"

# ─────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────
ALL_SUBJECTS = [
    "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "Go", "Rust",
    "Data Structures", "Algorithms", "Web Development", "Mobile Development",
    "Machine Learning", "Data Science", "Database Design", "DevOps",
    "Cloud Computing", "Cybersecurity", "Game Development", "Mathematics",
    "Physics", "Chemistry", "Biology", "English", "History", "Economics"
]

ALL_SPECIALIZATIONS = [
    "Programming", "Web Development", "Data Science", "Mobile Development",
    "Cybersecurity", "Cloud Infrastructure", "Game Development", "AI/ML",
    "Database Administration", "System Design", "Mathematics", "Science",
    "Language Arts", "Social Studies", "Test Prep", "Career Coaching"
]

# ─────────────────────────────────────────
# DB CONNECTION
# ─────────────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ─────────────────────────────────────────
# INIT DB
# ─────────────────────────────────────────
def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        full_name TEXT,
        email TEXT,
        theme TEXT DEFAULT 'light',
        mobile_number TEXT DEFAULT ''
    )
    """)

    # Migrate: add mobile_number column if it doesn't exist yet
    try:
        c.execute("ALTER TABLE users ADD COLUMN mobile_number TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass  # Column already exists

    c.execute("""
    CREATE TABLE IF NOT EXISTS tutor_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        bio TEXT,
        skills TEXT,
        specialization TEXT,
        experience INTEGER,
        hourly_rate REAL DEFAULT 0,
        rating REAL DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tutor_id INTEGER,
        slot_date TEXT,
        start_time TEXT,
        end_time TEXT,
        is_booked INTEGER DEFAULT 0,
        FOREIGN KEY(tutor_id) REFERENCES users(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        tutor_id INTEGER,
        slot_id INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        scheduled_date TEXT,
        start_time TEXT,
        end_time TEXT,
        FOREIGN KEY(student_id) REFERENCES users(id),
        FOREIGN KEY(tutor_id) REFERENCES users(id),
        FOREIGN KEY(slot_id) REFERENCES slots(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER,
        tutor_id INTEGER,
        student_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TEXT,
        FOREIGN KEY(booking_id) REFERENCES bookings(id),
        FOREIGN KEY(tutor_id) REFERENCES users(id),
        FOREIGN KEY(student_id) REFERENCES users(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        recipient_id INTEGER,
        message TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(sender_id) REFERENCES users(id),
        FOREIGN KEY(recipient_id) REFERENCES users(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        title TEXT DEFAULT '',
        message TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Migrate: add title column if it doesn't exist yet
    try:
        c.execute("ALTER TABLE notifications ADD COLUMN title TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass  # Column already exists

    c.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER,
        tutor_id INTEGER,
        student_id INTEGER,
        progress_note TEXT,
        created_at TEXT,
        FOREIGN KEY(booking_id) REFERENCES bookings(id),
        FOREIGN KEY(tutor_id) REFERENCES users(id),
        FOREIGN KEY(student_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# USER CREATION
# ─────────────────────────────────────────
def create_user(username, password, role, name, email, mobile_number=""):
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users VALUES(NULL,?,?,?,?,?,?,?)",
                  (username, password, role, name, email, "light", mobile_number))
        conn.commit()
        uid = c.lastrowid
        conn.close()
        return uid
    except:
        conn.close()
        return None

# ─────────────────────────────────────────
# REGISTER TUTOR (FIXED)
# ─────────────────────────────────────────
def register_tutor(username, password, name, email, mobile_number=""):
    uid = create_user(username, password, "tutor", name, email, mobile_number)

    if not uid:
        return None

    # ✅ auto create profile
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO tutor_profiles (user_id,bio,skills,specialization,experience)
    VALUES(?,?,?,?,?)
    """, (uid, "", "", "", 0))
    conn.commit()
    conn.close()

    return uid


# ─────────────────────────────────────────
# UPDATE USER INFO (shared — works for both tutor & student)
# ─────────────────────────────────────────
def update_user_info(user_id, full_name, email, mobile_number):
    """Update core user fields. Changes are immediately visible to all
    sessions because get_current_user() always fetches fresh from DB."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        UPDATE users
        SET full_name=?, email=?, mobile_number=?
        WHERE id=?
        """, (full_name, email, mobile_number, user_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET USER BY USERNAME
# ─────────────────────────────────────────
def get_user_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    except:
        conn.close()
        return None

# ─────────────────────────────────────────
# GET USER BY ID
# ─────────────────────────────────────────
def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    except:
        conn.close()
        return None

# ─────────────────────────────────────────
# UPDATE PROFILE
# ─────────────────────────────────────────
def update_profile(uid, bio, skills, spec, exp):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    UPDATE tutor_profiles
    SET bio=?, skills=?, specialization=?, experience=?
    WHERE user_id=?
    """, (bio, skills, spec, exp, uid))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# ADD SLOT
# ─────────────────────────────────────────
def add_slot(tutor_id, date_, start, end):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    INSERT INTO slots (tutor_id,slot_date,start_time,end_time)
    VALUES(?,?,?,?)
    """, (tutor_id, date_, start, end))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# GET TUTORS (FIXED)
# ─────────────────────────────────────────
def get_tutors():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    SELECT u.id, u.full_name, tp.skills, tp.specialization, tp.experience
    FROM users u
    JOIN tutor_profiles tp ON u.id = tp.user_id
    WHERE u.role='tutor' AND tp.skills != ''
    """)

    rows = c.fetchall()
    conn.close()

    return [dict(r) for r in rows]

# ─────────────────────────────────────────
# FILTER BY SUBJECT
# ─────────────────────────────────────────
def get_tutors_by_subject(subject):
    tutors = get_tutors()

    if subject == "All":
        return tutors

    result = []
    subject = subject.lower()

    for t in tutors:
        if subject in t["skills"].lower():
            result.append(t)

    return result

# ─────────────────────────────────────────
# UPDATE USER THEME
# ─────────────────────────────────────────
def update_user_theme(user_id, theme):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET UNREAD COUNT
# ─────────────────────────────────────────
def get_unread_count(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) as count FROM messages WHERE recipient_id = ? AND is_read = 0", (user_id,))
        result = c.fetchone()
        conn.close()
        return result["count"] if result else 0
    except:
        conn.close()
        return 0

# ─────────────────────────────────────────
# GET TUTOR PROFILE
# ─────────────────────────────────────────
def get_tutor_profile(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM tutor_profiles WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    except:
        conn.close()
        return None

# ─────────────────────────────────────────
# UPSERT TUTOR PROFILE
# ─────────────────────────────────────────
def upsert_tutor_profile(user_id, bio, skills, specialization, experience, hourly_rate=0):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM tutor_profiles WHERE user_id = ?", (user_id,))
        if c.fetchone():
            c.execute("""
            UPDATE tutor_profiles
            SET bio=?, skills=?, specialization=?, experience=?, hourly_rate=?
            WHERE user_id=?
            """, (bio, skills, specialization, experience, hourly_rate, user_id))
        else:
            c.execute("""
            INSERT INTO tutor_profiles (user_id,bio,skills,specialization,experience,hourly_rate)
            VALUES(?,?,?,?,?,?)
            """, (user_id, bio, skills, specialization, experience, hourly_rate))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET BOOKINGS FOR TUTOR
# ─────────────────────────────────────────
def get_bookings_for_tutor(tutor_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT b.*, u.full_name as student_name
        FROM bookings b
        JOIN users u ON b.student_id = u.id
        WHERE b.tutor_id = ?
        ORDER BY b.created_at DESC
        """, (tutor_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# GET BOOKINGS FOR STUDENT
# ─────────────────────────────────────────
def get_bookings_for_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT b.*, u.full_name as tutor_name
        FROM bookings b
        JOIN users u ON b.tutor_id = u.id
        WHERE b.student_id = ?
        ORDER BY b.created_at DESC
        """, (student_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# CREATE BOOKING
# ─────────────────────────────────────────
def create_booking(student_id, tutor_id, slot_id, scheduled_date, start_time, end_time):
    conn = get_connection()
    c = conn.cursor()
    try:
        from datetime import datetime
        c.execute("""
        INSERT INTO bookings (student_id, tutor_id, slot_id, scheduled_date, start_time, end_time, created_at)
        VALUES(?,?,?,?,?,?,?)
        """, (student_id, tutor_id, slot_id, scheduled_date, start_time, end_time, datetime.now().isoformat()))
        conn.commit()
        booking_id = c.lastrowid
        conn.close()
        return booking_id
    except:
        conn.close()
        return None

# ─────────────────────────────────────────
# UPDATE BOOKING STATUS
# ─────────────────────────────────────────
def update_booking_status(booking_id, status, note=None):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET FEEDBACK FOR TUTOR
# ─────────────────────────────────────────
def get_feedback_for_tutor(tutor_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT f.*, u.full_name as student_name
        FROM feedback f
        JOIN users u ON f.student_id = u.id
        WHERE f.tutor_id = ?
        ORDER BY f.created_at DESC
        """, (tutor_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# GET FEEDBACK FOR BOOKING
# ─────────────────────────────────────────
def get_feedback_for_booking(booking_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM feedback WHERE booking_id = ?", (booking_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    except:
        conn.close()
        return None

# ─────────────────────────────────────────
# ADD FEEDBACK
# ─────────────────────────────────────────
def add_feedback(booking_id, tutor_id, student_id, rating, comment):
    conn = get_connection()
    c = conn.cursor()
    try:
        from datetime import datetime
        c.execute("""
        INSERT INTO feedback (booking_id, tutor_id, student_id, rating, comment, created_at)
        VALUES(?,?,?,?,?,?)
        """, (booking_id, tutor_id, student_id, rating, comment, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# SEND MESSAGE
# ─────────────────────────────────────────
def send_message(sender_id, recipient_id, message):
    conn = get_connection()
    c = conn.cursor()
    try:
        from datetime import datetime
        c.execute("""
        INSERT INTO messages (sender_id, recipient_id, message, created_at)
        VALUES(?,?,?,?)
        """, (sender_id, recipient_id, message, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET MESSAGES
# ─────────────────────────────────────────
def get_messages(user1_id, user2_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT * FROM messages
        WHERE (sender_id = ? AND recipient_id = ?) OR (sender_id = ? AND recipient_id = ?)
        ORDER BY created_at ASC
        """, (user1_id, user2_id, user2_id, user1_id))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# GET CONVERSATION PARTNERS
# ─────────────────────────────────────────
def get_conversation_partners(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT DISTINCT
            CASE 
                WHEN sender_id = ? THEN recipient_id
                ELSE sender_id
            END as partner_id,
            u.full_name,
            u.id
        FROM messages m
        JOIN users u ON u.id = CASE 
            WHEN sender_id = ? THEN recipient_id
            ELSE sender_id
        END
        WHERE sender_id = ? OR recipient_id = ?
        ORDER BY m.created_at DESC
        """, (user_id, user_id, user_id, user_id))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# CREATE NOTIFICATION
# ─────────────────────────────────────────
def create_notification(user_id, notif_type, message, title=""):
    conn = get_connection()
    c = conn.cursor()
    try:
        from datetime import datetime
        c.execute("""
        INSERT INTO notifications (user_id, type, title, message, created_at)
        VALUES(?,?,?,?,?)
        """, (user_id, notif_type, title or notif_type.capitalize(), message, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET NOTIFICATIONS
# ─────────────────────────────────────────
def get_notifications(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT id, user_id, type AS notif_type,
               COALESCE(title, type, 'Notification') AS title,
               message, is_read, created_at
        FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
        """, (user_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# MARK NOTIFICATION READ
# ─────────────────────────────────────────
def mark_notification_read(notification_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# MARK ALL NOTIFICATIONS READ
# ─────────────────────────────────────────
def mark_all_notifications_read(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET ALL TUTORS
# ─────────────────────────────────────────
def get_all_tutors():
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT u.id, u.full_name, tp.bio, tp.skills, tp.specialization,
               tp.experience, tp.hourly_rate, tp.rating
        FROM users u
        JOIN tutor_profiles tp ON u.id = tp.user_id
        WHERE u.role = 'tutor'
        ORDER BY tp.rating DESC
        """)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# SUBJECT MATCH TUTORS
# ─────────────────────────────────────────
def subject_match_tutors(subject):
    tutors = get_all_tutors()
    if subject == "All":
        return tutors
    
    result = []
    subject_lower = subject.lower()
    for t in tutors:
        if t["skills"] and subject_lower in t["skills"].lower():
            result.append(t)
    return result

# ─────────────────────────────────────────
# GET SLOTS FOR TUTOR
# ─────────────────────────────────────────
def get_slots_for_tutor(tutor_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        SELECT * FROM slots
        WHERE tutor_id = ? AND is_booked = 0
        ORDER BY slot_date, start_time
        """, (tutor_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# ADD AVAILABILITY SLOT
# ─────────────────────────────────────────
def add_availability_slot(tutor_id, slot_date, start_time, end_time):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
        INSERT INTO slots (tutor_id, slot_date, start_time, end_time, is_booked)
        VALUES(?,?,?,?,?)
        """, (tutor_id, slot_date, start_time, end_time, 0))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# DELETE AVAILABILITY SLOT
# ─────────────────────────────────────────
def delete_availability_slot(slot_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM slots WHERE id = ?", (slot_id,))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET RECOMMENDED SLOTS
# ─────────────────────────────────────────
def get_recommended_slots(tutor_id, limit=5):
    return get_slots_for_tutor(tutor_id)[:limit]

# ─────────────────────────────────────────
# GET NEXT AVAILABLE SLOT
# ─────────────────────────────────────────
def get_next_available_slot(tutor_id):
    slots = get_slots_for_tutor(tutor_id)
    return slots[0] if slots else None

# ─────────────────────────────────────────
# ADD PROGRESS ENTRY
# ─────────────────────────────────────────
def add_progress_entry(booking_id, tutor_id, student_id, progress_note):
    conn = get_connection()
    c = conn.cursor()
    try:
        from datetime import datetime
        c.execute("""
        INSERT INTO progress (booking_id, tutor_id, student_id, progress_note, created_at)
        VALUES(?,?,?,?,?)
        """, (booking_id, tutor_id, student_id, progress_note, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# ─────────────────────────────────────────
# GET PROGRESS ENTRIES
# ─────────────────────────────────────────
def get_progress_entries(student_id=None, tutor_id=None, booking_id=None):
    conn = get_connection()
    c = conn.cursor()
    try:
        query = "SELECT * FROM progress WHERE 1=1"
        params = []
        
        if student_id:
            query += " AND student_id = ?"
            params.append(student_id)
        if tutor_id:
            query += " AND tutor_id = ?"
            params.append(tutor_id)
        if booking_id:
            query += " AND booking_id = ?"
            params.append(booking_id)
        
        query += " ORDER BY created_at DESC"
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except:
        conn.close()
        return []

# ─────────────────────────────────────────
# TEST FLOW
# ─────────────────────────────────────────
def test():
    init_db()

    # register tutor
    tid = register_tutor("tutor1", "123", "Ashok", "ashok@gmail.com")

    # update profile
    update_profile(tid,
                   "Expert Java Trainer",
                   "Java, Data Structures",
                   "Programming",
                   3)

    # add slot
    add_slot(tid, str(date.today()), "10:00", "11:00")

    # student view
    student_view("Java")

# RUN
if __name__ == "__main__":
    test()