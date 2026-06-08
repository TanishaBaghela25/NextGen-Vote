# 🗳️ SmartVote — AI Powered Face Recognition Voting System

A modern, secure online voting system with AI face recognition, Aadhaar+EPIC verification, OTP authentication, MySQL database, and a glassmorphism dark UI.

---

## 📁 Project Structure

```
SmartVotingSystem/
│
├── app.py                    ← Main Flask application
├── add_faces.py              ← Offline face registration script
├── database.sql              ← MySQL setup script
├── requirements.txt          ← Python dependencies
│
├── data/
│   ├── names.pkl             ← Face label data (auto-created)
│   └── faces_data.pkl        ← Face vector data (auto-created)
│
├── static/
│   └── css/
│       └── style.css         ← Global glassmorphism CSS
│
└── templates/
    ├── index.html            ← Home page
    ├── register.html         ← Voter registration
    ├── user_login.html       ← Login page
    ├── otp.html              ← OTP verification
    ├── face_verify.html      ← Face scan page
    ├── vote.html             ← Cast vote page
    ├── success.html          ← Vote submitted
    ├── already_voted.html    ← Duplicate vote block
    ├── about.html            ← About page
    ├── contact.html          ← Contact / Support
    ├── admin_login.html      ← Admin login
    ├── admin_dashboard.html  ← Admin main dashboard
    ├── admin_voters.html     ← All registered voters
    ├── results.html          ← Live election results
    ├── admin_change_password.html
    └── admin_add.html
```

---

## ⚙️ Setup Instructions

### Step 1 — Install Python 3.10+
```bash
python --version
```

### Step 2 — Create Virtual Environment
```bash
cd SmartVotingSystem
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Setup MySQL Database

Open MySQL Workbench or terminal and run:
```sql
SOURCE database.sql;
```
Or copy-paste the content of `database.sql` into MySQL.

### Step 5 — Configure Database Password

Open `app.py` and update line ~12:
```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",  # ← Change this
        database="smart_voting_db"
    )
```

### Step 6 — Run the Application
```bash
python app.py
```

Open browser: **http://127.0.0.1:5000**

---

## 🔐 Default Admin Login
- **Username:** `admin`
- **Password:** `Admin@123`

> ⚠️ Change this immediately after first login via Admin → Change Password

---

## 🗳️ Voting Flow

1. **Register** → Enter Aadhaar (12-digit) + EPIC ID + Mobile + Face Capture
2. **Login** → Enter Aadhaar + EPIC ID → OTP sent to mobile
3. **OTP Verify** → Enter 6-digit OTP
4. **Face Verify** → Webcam scans and matches face
5. **Vote** → Select party → Confirm
6. **Done** → Vote recorded, duplicate blocked forever

---

## 🛡️ Security Features

| Feature | Description |
|---|---|
| Aadhaar Uniqueness | No two voters with same Aadhaar |
| EPIC ID Uniqueness | No two voters with same voter card |
| Face Duplicacy Check | KNN distance < 3000 for new registration |
| Face Match Threshold | KNN distance < 4500 for login verification |
| SHA-256 Passwords | All admin passwords hashed |
| Session Security | OTP + face verification state in Flask session |
| Vote Once | DB-level UNIQUE constraint on votes.aadhaar |

---

## 📊 Databases

| Table | Contents |
|---|---|
| `voters` | Aadhaar, EPIC, mobile, email, name, DOB, state |
| `votes` | Aadhaar + party + timestamp (unique per Aadhaar) |
| `admins` | Username + SHA-256 hashed password |

---

## 🌐 Routes Reference

| URL | Purpose |
|---|---|
| `/` | Home page |
| `/register` | Voter registration |
| `/user_login` | Voter login |
| `/verify_otp` | OTP check |
| `/face_verify_page` | Face scan UI |
| `/face_verify` | Face verify API (POST) |
| `/vote` | Voting page |
| `/submit_vote` | Submit vote (POST) |
| `/about` | About page |
| `/contact` | Contact page |
| `/admin_login` | Admin login |
| `/admin_dashboard` | Admin dashboard |
| `/admin_voters` | All voters list |
| `/admin_results` | Live results |
| `/admin_change_password` | Update admin creds |
| `/admin_add` | Add new admin |
| `/admin_logout` | Logout admin |

---

## 🔧 Troubleshooting

**Camera not working?**
- Allow browser camera permissions
- Try Chrome or Firefox

**Face not matching?**
- Ensure good lighting
- Face the camera directly
- Re-register if needed (delete data/*.pkl first)

**MySQL connection error?**
- Check password in app.py
- Ensure MySQL service is running
- Run `database.sql` to create tables

**OTP not showing?**
- OTP is shown on screen for demo purposes
- In production: integrate Twilio/MSG91 SMS API

---

## 📞 Support
- Helpline: 1800-111-VOTE
- Email: support@smartvote.in
- WhatsApp: +91 98765 43210
