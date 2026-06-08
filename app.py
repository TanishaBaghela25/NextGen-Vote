from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import mysql.connector
import cv2
import pickle
import numpy as np
import base64
import random
import os
import hashlib
import json
from sklearn.neighbors import KNeighborsClassifier
from datetime import datetime

app = Flask(__name__)
app.secret_key = "SmartVoting@SecretKey2024#XYZ"


os.makedirs('data', exist_ok=True)
# ─────────────────────────────────────────
#  DB CONNECTION
# ─────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="new_password",   # ← change this
        database="online_voting"
    )

# ─────────────────────────────────────────
#  FACE HELPERS
# ─────────────────────────────────────────
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def decode_image(b64_string):
    encoded = b64_string.split(',')[1]
    arr = np.frombuffer(base64.b64decode(encoded), np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def detect_face(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=8, minSize=(80, 80)
    )
    return faces

def extract_face_vector(img, x, y, w, h):
    crop = img[y:y+h, x:x+w]
    resized = cv2.resize(crop, (50, 50))
    return resized.flatten()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_face_model():
    names_path = 'data/names.pkl'
    faces_path = 'data/faces_data.pkl'
    if not os.path.exists(names_path) or not os.path.exists(faces_path):
        return None, None
    with open(names_path, 'rb') as f:
        LABELS = pickle.load(f)
    with open(faces_path, 'rb') as f:
        FACES = pickle.load(f)
    return LABELS, FACES

# ─────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────
@app.route('/')
def home():
    lang = session.get('lang', 'en')
    return render_template('index.html', lang=lang)

@app.route('/set_language', methods=['POST'])
def set_language():
    lang = request.form.get('lang', 'en')
    session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html', lang=session.get('lang', 'en'))

@app.route('/contact')
def contact():
    return render_template('contact.html', lang=session.get('lang', 'en'))

# ─────────────────────────────────────────
#  USER REGISTER
# ─────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        aadhaar     = request.form.get('aadhaar', '').strip()
        epic_id     = request.form.get('epic_id', '').strip().upper()
        mobile      = request.form.get('mobile', '').strip()
        email       = request.form.get('email', '').strip()
        full_name   = request.form.get('full_name', '').strip()
        dob         = request.form.get('dob', '').strip()
        gender      = request.form.get('gender', '').strip()
        state       = request.form.get('state', '').strip()

        # Validation
        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return jsonify({"status": "error", "message": "Invalid Aadhaar number (12 digits required)"})
        if len(epic_id) < 6:
            return jsonify({"status": "error", "message": "Invalid EPIC/Voter ID"})
        if len(mobile) != 10 or not mobile.isdigit():
            return jsonify({"status": "error", "message": "Invalid mobile number"})

        db = get_db()
        cursor = db.cursor()

        # Check duplicate Aadhaar
        cursor.execute("SELECT id FROM voters WHERE aadhaar = %s", (aadhaar,))
        if cursor.fetchone():
            db.close()
            return jsonify({"status": "error", "message": "Aadhaar already registered"})

        # Check duplicate EPIC
        cursor.execute("SELECT id FROM voters WHERE epic_id = %s", (epic_id,))
        if cursor.fetchone():
            db.close()
            return jsonify({"status": "error", "message": "EPIC ID already registered"})

        session['reg_data'] = {
            'aadhaar': aadhaar, 'epic_id': epic_id, 'mobile': mobile,
            'email': email, 'full_name': full_name, 'dob': dob,
            'gender': gender, 'state': state
        }
        db.close()
        return jsonify({"status": "success", "message": "Proceed to face capture"})

    return render_template('register.html', lang=session.get('lang', 'en'))

@app.route('/save_face_register', methods=['POST'])
def save_face_register():
    if 'reg_data' not in session:
        return jsonify({"status": "error", "message": "Session expired"})

    data = request.json
    image_b64 = data.get('image')
    img = decode_image(image_b64)
    faces = detect_face(img)

    if len(faces) == 0:
        return jsonify({"status": "error", "message": "No face detected, try again"})
    if len(faces) > 1:
        return jsonify({"status": "error", "message": "Multiple faces detected"})

    x, y, w, h = faces[0]
    face_vec = extract_face_vector(img, x, y, w, h)

    # Check face duplicacy against existing pkl data
    LABELS, FACES = load_face_model()
    if LABELS is not None and FACES is not None:
        knn = KNeighborsClassifier(n_neighbors=1)
        knn.fit(FACES, LABELS)
        dist, _ = knn.kneighbors(face_vec.reshape(1, -1))
        if dist[0][0] < 3000:
            return jsonify({"status": "error", "message": "Face already registered with another account"})

    # Capture multiple frames (simulate 100 frames from 1 good frame)
    face_vectors = [face_vec + np.random.normal(0, 5, face_vec.shape).astype(np.float32)
                    for _ in range(100)]
    face_vectors[0] = face_vec  # Keep original

    reg = session['reg_data']
    aadhaar = reg['aadhaar']

    # Save/append pkl
    names_path = 'data/names.pkl'
    faces_path = 'data/faces_data.pkl'

    if os.path.exists(faces_path) and os.path.exists(names_path):
        with open(faces_path, 'rb') as f:
            existing_faces = pickle.load(f)
        with open(names_path, 'rb') as f:
            existing_names = pickle.load(f)
        new_faces = np.vstack([existing_faces, np.array(face_vectors)])
        new_names = list(existing_names) + [aadhaar] * 100
    else:
        new_faces = np.array(face_vectors)
        new_names = [aadhaar] * 100

    with open(faces_path, 'wb') as f:
        pickle.dump(new_faces, f)
    with open(names_path, 'wb') as f:
        pickle.dump(new_names, f)

    # Save to DB
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO voters (aadhaar, epic_id, mobile, email, full_name, dob, gender, state, registered_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (reg['aadhaar'], reg['epic_id'], reg['mobile'], reg['email'],
          reg['full_name'], reg['dob'], reg['gender'], reg['state'],
          datetime.now()))
    db.commit()
    db.close()
    session.pop('reg_data', None)
    return jsonify({"status": "success", "message": "Registration complete!"})

# ─────────────────────────────────────────
#  USER LOGIN → OTP → FACE → VOTE
# ─────────────────────────────────────────
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        aadhaar = request.form.get('aadhaar', '').strip()
        epic_id = request.form.get('epic_id', '').strip().upper()

        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return render_template('user_login.html',
                                   error="Invalid Aadhaar number",
                                   lang=session.get('lang', 'en'))

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM voters WHERE aadhaar=%s AND epic_id=%s",
                       (aadhaar, epic_id))
        voter = cursor.fetchone()

        if not voter:
            db.close()
            return render_template('user_login.html',
                                   error="Aadhaar or EPIC ID not found",
                                   lang=session.get('lang', 'en'))

        # Check already voted
        cursor.execute("SELECT id FROM votes WHERE aadhaar=%s", (aadhaar,))
        if cursor.fetchone():
            db.close()
            return render_template('user_login.html',
                                   error="You have already voted",
                                   lang=session.get('lang', 'en'))

        db.close()
        otp = str(random.randint(100000, 999999))
        session['otp'] = otp
        session['login_aadhaar'] = aadhaar
        session['voter_name'] = voter['full_name']
        # In production: send OTP via SMS/email
        return render_template('otp.html', otp=otp,
                               mobile=voter['mobile'][-4:],
                               lang=session.get('lang', 'en'))

    return render_template('user_login.html', lang=session.get('lang', 'en'))

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form.get('otp', '').strip()
    if user_otp == session.get('otp'):
        session['otp_verified'] = True
        return redirect(url_for('face_verify_page'))
    return render_template('otp.html',
                           otp=session.get('otp'),
                           mobile="XXXX",
                           error="Invalid OTP. Try again.",
                           lang=session.get('lang', 'en'))

@app.route('/face_verify_page')
def face_verify_page():
    if not session.get('otp_verified'):
        return redirect(url_for('user_login'))
    return render_template('face_verify.html', lang=session.get('lang', 'en'))

@app.route('/face_verify', methods=['POST'])
def face_verify():
    if not session.get('otp_verified'):
        return jsonify({"status": "error", "message": "Unauthorized"})

    try:
        image_b64 = request.json.get('image')
        img = decode_image(image_b64)
        faces = detect_face(img)

        if len(faces) == 0:
            return jsonify({"status": "failed", "message": "No face detected"})

        LABELS, FACES = load_face_model()
        if LABELS is None:
            return jsonify({"status": "failed", "message": "No face data found"})

        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(FACES, LABELS)

        for (x, y, w, h) in faces:
            face_vec = extract_face_vector(img, x, y, w, h)
            output = knn.predict(face_vec.reshape(1, -1))
            dist, _ = knn.kneighbors(face_vec.reshape(1, -1))
            min_dist = dist[0][0]

            aadhaar = session.get('login_aadhaar')
            print(f"Predicted: {output[0]}, Expected: {aadhaar}, Dist: {min_dist}")

            if output[0] == aadhaar and min_dist < 4500:
                session['face_verified'] = True
                return jsonify({"status": "success",
                                "message": "Face verified successfully"})
            else:
                return jsonify({"status": "failed",
                                "message": "Face not matching records"})

        return jsonify({"status": "failed", "message": "Verification failed"})

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})

@app.route('/vote')
def vote():
    if not session.get('face_verified'):
        return redirect(url_for('user_login'))
    return render_template('vote.html',
                           voter_name=session.get('voter_name', 'Voter'),
                           lang=session.get('lang', 'en'))

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if not session.get('face_verified'):
        return redirect(url_for('user_login'))

    party = request.form.get('party')
    aadhaar = session.get('login_aadhaar')
    if not party or not aadhaar:
        return redirect(url_for('vote'))

    db = get_db()
    cursor = db.cursor()

    # Double-check not already voted
    cursor.execute("SELECT id FROM votes WHERE aadhaar=%s", (aadhaar,))
    if cursor.fetchone():
        db.close()
        session.clear()
        return render_template('already_voted.html', lang=session.get('lang', 'en'))

    cursor.execute("""
        INSERT INTO votes (aadhaar, party, voted_at)
        VALUES (%s, %s, %s)
    """, (aadhaar, party, datetime.now()))
    db.commit()
    db.close()

    voter_name = session.get('voter_name', 'Voter')
    session.clear()
    return render_template('success.html', voter_name=voter_name, party=party,
                           lang='en')

# ─────────────────────────────────────────
#  ADMIN
# ─────────────────────────────────────────
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        hashed   = hash_password(password)

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s",
                       (username, hashed))
        admin = cursor.fetchone()
        db.close()

        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_id'] = admin['id']
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error="Invalid credentials")

    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM voters")
    total_voters = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM votes")
    total_votes = cursor.fetchone()['total']

    cursor.execute("""
        SELECT party, COUNT(*) as count
        FROM votes GROUP BY party ORDER BY count DESC
    """)
    results = cursor.fetchall()

    cursor.execute("""
        SELECT v.full_name, v.aadhaar, v.epic_id, v.mobile, v.state, v.registered_at
        FROM voters v ORDER BY v.registered_at DESC LIMIT 20
    """)
    recent_voters = cursor.fetchall()

    cursor.execute("""
        SELECT vt.aadhaar, vt.party, vt.voted_at, v.full_name
        FROM votes vt LEFT JOIN voters v ON vt.aadhaar=v.aadhaar
        ORDER BY vt.voted_at DESC LIMIT 20
    """)
    recent_votes = cursor.fetchall()
    db.close()

    labels = [r['party'] for r in results]
    counts = [r['count'] for r in results]

    return render_template('admin_dashboard.html',
                           total_voters=total_voters,
                           total_votes=total_votes,
                           results=results,
                           recent_voters=recent_voters,
                           recent_votes=recent_votes,
                           labels=json.dumps(labels),
                           counts=json.dumps(counts),
                           admin_user=session.get('admin_username'))

@app.route('/admin_results')
def admin_results():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT party, COUNT(*) as count FROM votes GROUP BY party ORDER BY count DESC")
    results = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as total FROM votes")
    total = cursor.fetchone()['total']
    db.close()
    labels = [r['party'] for r in results]
    counts = [r['count'] for r in results]
    return render_template('results.html',
                           results=results, total=total,
                           labels=json.dumps(labels),
                           counts=json.dumps(counts))

@app.route('/admin_voters')
def admin_voters():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM voters ORDER BY registered_at DESC")
    voters = cursor.fetchall()
    db.close()
    return render_template('admin_voters.html', voters=voters)

@app.route('/admin_change_password', methods=['GET', 'POST'])
def admin_change_password():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        old_pw      = hash_password(request.form.get('old_password', ''))
        new_password= request.form.get('new_password', '')
        confirm_pw  = request.form.get('confirm_password', '')
        new_usr     = request.form.get('new_username', '').strip()
        if new_password != confirm_pw:
            return render_template('admin_change_password.html', error="Passwords do not match")
        new_pw = hash_password(new_password)
        admin_id = session.get('admin_id')

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM admins WHERE id=%s AND password=%s",
                       (admin_id, old_pw))
        if not cursor.fetchone():
            db.close()
            return render_template('admin_change_password.html',
                                   error="Old password incorrect")
        cursor.execute("UPDATE admins SET username=%s, password=%s WHERE id=%s",
                       (new_usr, new_pw, admin_id))
        db.commit()
        db.close()
        session['admin_username'] = new_usr
        return render_template('admin_change_password.html',
                               success="Credentials updated successfully!")

    return render_template('admin_change_password.html')

@app.route('/admin_add', methods=['GET', 'POST'])
def admin_add():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = hash_password(request.form.get('password', ''))
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO admins (username, password) VALUES (%s,%s)",
                           (username, password))
            db.commit()
            db.close()
            return render_template('admin_add.html', success="New admin added!")
        except:
            db.close()
            return render_template('admin_add.html', error="Username already exists")
    return render_template('admin_add.html')

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
