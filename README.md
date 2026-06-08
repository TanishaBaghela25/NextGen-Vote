# SmartVote — AI Powered Face Recognition Voting System

A modern, secure online voting system with AI face recognition, Aadhaar+EPIC verification, OTP authentication, MySQL database, and a glassmorphism dark UI.

---

## Setup Instructions

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


## Voting Flow

1. **Register** → Enter Aadhaar (12-digit) + EPIC ID + Mobile + Face Capture
2. **Login** → Enter Aadhaar + EPIC ID → OTP sent to mobile
3. **OTP Verify** → Enter 6-digit OTP
4. **Face Verify** → Webcam scans and matches face
5. **Vote** → Select party → Confirm
6. **Done** → Vote recorded, duplicate blocked forever

---

## Security Features

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

## Databases

| Table | Contents |
|---|---|
| `voters` | Aadhaar, EPIC, mobile, email, name, DOB, state |
| `votes` | Aadhaar + party + timestamp (unique per Aadhaar) |
| `admins` | Username + SHA-256 hashed password |

---
## Troubleshooting

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

