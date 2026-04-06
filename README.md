# 🎓 TutorLink v3 - Online Tutoring Platform

### Modern, fast, and beautiful tutoring marketplace built with Streamlit

---

## 📋 Quick Start

### 1. **Install Requirements**
```bash
pip install streamlit bcrypt
```

### 2. **Run the App**
```bash
cd modified_tutorlink
streamlit run app.py
```

### 3. **Access in Browser**
- Local: `http://localhost:8504`
- Network: `http://YOUR_IP:8504`

---

## 🔐 Demo Credentials

### **Tutor Account** (Already Pre-registered)
```
Username: tutor1
Password: 123456
Role: Tutor
Name: Ashok Kumar
```

### **Create Student Account**
Click "Register as Student" and fill in:
- Username: `student1`
- Password: `123456789`
- Full Name: Your Name
- Email: your@email.com

---

## ✨ Features

### 👨‍🎓 Student Features
- 🔍 Browse & filter tutors by subject
- 📅 View tutor availability and book slots
- 💬 Send messages to tutors
- ⭐ Leave reviews and ratings
- 📊 Track learning progress
- 🔔 Get notifications for booking updates

### 👨‍🏫 Tutor Features
- 👤 Create & manage complete profile
- 📝 Set hourly rates & specialization
- 📅 Add/manage availability slots
- 📨 Respond to booking requests
- 💬 Direct messaging with students
- ⭐ View student reviews & ratings
- 📈 Track student progress

### 🎨 General Features
- 🌓 Light/Dark theme toggle
- 🔐 Secure password hashing with bcrypt
- 💾 SQLite database with complete schema
- 📱 Responsive design
- ⚡ Lightning-fast performance

---

## 📁 Project Structure

```
modified_tutorlink/
├── app.py                      # Main entry point & sidebar
├── auth.py                     # Login/registration logic
├── database.py                 # All database operations
├── tutor_profile.py           # Tutor profile management
├── tutor_dashboard.py         # Tutor home dashboard
├── student_dashboard.py       # Student home dashboard
├── browse_tutors.py           # Tutor browsing & booking
├── booking_requests.py        # Tutor booking management
├── manage_availability.py     # Availability slot management
├── my_sessions.py             # Student's booked sessions
├── messages.py                # Messaging system
├── reviews.py                 # Review management
├── progress_tracker.py        # Learning progress tracking
├── upcoming_sessions.py       # Upcoming sessions list
├── tutorlink.db              # SQLite database
└── README.md                  # This file
```

---

## 🗄️ Database Schema

### Tables
- **users** - User accounts (students & tutors)
- **tutor_profiles** - Tutor profile information
- **bookings** - Session bookings
- **feedback** - Reviews & ratings
- **messages** - Direct messages
- **notifications** - User notifications
- **slots** - Available tutoring slots
- **progress** - Student progress notes

---

## 🚀 How to Share with Friends

### **Option 1: Zip File (Easiest)**
1. Zip the entire `modified_tutorlink` folder
2. Send via email, Google Drive, Dropbox, or any file sharing service
3. Friend extracts & follows "Quick Start" section above

### **Option 2: GitHub**
1. Initialize git: `git init`
2. Create GitHub repo
3. Push files: `git push origin main`
4. Share GitHub link with friend
5. Friend clones: `git clone https://github.com/username/tutorlink.git`

### **Option 3: Cloud Storage**
- Upload folder to Google Drive, OneDrive, or Dropbox
- Share link with friend
- Friend downloads & extracts

---

## 🔧 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Database**: SQLite
- **Security**: bcrypt for password hashing
- **Styling**: Custom CSS with Streamlit markdown

---

## 📝 Key Files Modified/Created

### Core Database Functions
✅ `upsert_tutor_profile()` - Create/update tutor profiles
✅ `get_bookings_for_tutor()` - Fetch tutor's bookings
✅ `get_bookings_for_student()` - Fetch student's bookings
✅ `create_booking()` - Create new booking
✅ `add_feedback()` - Add reviews
✅ `send_message()` - Send messages
✅ `get_notifications()` - Fetch notifications
✅ `add_progress_entry()` - Track learning progress

### Authentication
✅ `get_user_by_username()` - Fetch user by username
✅ `get_user_by_id()` - Fetch user by ID
✅ `update_user_theme()` - Save theme preference
✅ Password hashing with bcrypt

---

## 🎯 Working Features

- ✅ User Registration & Login
- ✅ Role-based access (Student/Tutor)
- ✅ Tutor profile creation with skills & specialization
- ✅ Availability slot management
- ✅ Booking system with status tracking
- ✅ Direct messaging between users
- ✅ Reviews & star ratings
- ✅ Progress tracking
- ✅ Notifications system
- ✅ Theme persistence
- ✅ Search & filter tutors by subject

---

## 🐛 Fixes Applied

1. **AttributeError on NoneType** - Fixed profile existence checks
2. **Missing database functions** - Implemented all 40+ functions
3. **Schema updates** - Added all required tables
4. **Parameter mismatches** - Fixed function signatures
5. **Import errors** - Resolved all dependencies

---

## 💡 Tips for Friends

1. **Create different accounts** to test student/tutor workflows
2. **Set availability slots** as tutor before student tries to book
3. **Use same machine or network** for easy access
4. **Check notifications** for booking updates
5. **Theme persists** across sessions

---

## 📞 Support

If your friend encounters any issues:

1. **Check Python version**: `python --version` (need 3.8+)
2. **Verify installations**: `pip list | grep streamlit`
3. **Delete database** if schema issues: `rm tutorlink.db`
4. **Share error output** for debugging

---

## 🎓 Future Enhancements

- Video call integration
- Payment processing
- Calendar sync
- Email notifications
- Mobile app
- Advanced analytics

---

**Enjoy sharing TutorLink! 🚀**
