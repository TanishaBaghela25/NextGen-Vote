"""
add_faces.py — Offline Face Registration Script
Run this if you want to register faces directly via webcam (without browser)
Usage: python add_faces.py
"""

import cv2
import pickle
import numpy as np
import os

# ── Paths ──────────────────────────────────────────
DATA_DIR = 'data'
NAMES_PATH = os.path.join(DATA_DIR, 'names.pkl')
FACES_PATH = os.path.join(DATA_DIR, 'faces_data.pkl')

os.makedirs(DATA_DIR, exist_ok=True)

# ── Face Detector ───────────────────────────────────
facedetect = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def add_face(aadhaar_number: str, num_frames: int = 100):
    """Capture face data for a voter identified by their Aadhaar number."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    face_data   = []
    frame_count = 0

    print(f"\n[INFO] Starting face capture for Aadhaar: {aadhaar_number}")
    print(f"[INFO] Will capture {num_frames} frames. Press Q to quit early.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Cannot read from camera")
            break

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=8,
            minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            crop_img  = frame[y:y+h, x:x+w]
            resized   = cv2.resize(crop_img, (50, 50))
            face_vec  = resized.flatten()

            if frame_count < num_frames:
                face_data.append(face_vec)
                frame_count += 1

            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 212, 255), 2)
            cv2.putText(frame, f'Captured: {frame_count}/{num_frames}',
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 212, 255), 2)

        # Progress bar on frame
        progress = int((frame_count / num_frames) * frame.shape[1])
        cv2.rectangle(frame, (0, frame.shape[0]-20), (progress, frame.shape[0]),
                      (0, 255, 136), -1)
        cv2.putText(frame, f'Progress: {frame_count}/{num_frames}',
                    (10, frame.shape[0]-25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 1)

        cv2.imshow('Face Registration — Press Q to quit', frame)

        if frame_count >= num_frames:
            print(f"[SUCCESS] Captured {num_frames} frames!")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Capture stopped early.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(face_data) == 0:
        print("[ERROR] No face data captured. Make sure your face is visible.")
        return False

    face_array = np.array(face_data)
    labels     = [aadhaar_number] * len(face_data)

    # Load existing data
    if os.path.exists(FACES_PATH) and os.path.exists(NAMES_PATH):
        with open(FACES_PATH, 'rb') as f:
            existing_faces = pickle.load(f)
        with open(NAMES_PATH, 'rb') as f:
            existing_names = pickle.load(f)

        # Check face duplicacy
        from sklearn.neighbors import KNeighborsClassifier
        if len(existing_faces) >= 1:
            knn = KNeighborsClassifier(n_neighbors=1)
            knn.fit(existing_faces, existing_names)
            test_vec = face_array[0].reshape(1, -1)
            dist, _  = knn.kneighbors(test_vec)
            if dist[0][0] < 3000:
                print(f"[ERROR] Face already registered with another account! (distance: {dist[0][0]:.0f})")
                return False

        new_faces = np.vstack([existing_faces, face_array])
        new_names = list(existing_names) + labels
    else:
        new_faces = face_array
        new_names = labels

    # Save
    with open(FACES_PATH, 'wb') as f:
        pickle.dump(new_faces, f)
    with open(NAMES_PATH, 'wb') as f:
        pickle.dump(new_names, f)

    print(f"[SUCCESS] Face registered for Aadhaar: {aadhaar_number}")
    print(f"[INFO] Total face records in database: {len(new_names)}")
    return True


if __name__ == '__main__':
    print("=" * 50)
    print("  SmartVote — Offline Face Registration")
    print("=" * 50)
    aadhaar = input("\nEnter 12-digit Aadhaar number: ").strip()

    if not aadhaar.isdigit() or len(aadhaar) != 12:
        print("[ERROR] Invalid Aadhaar number. Must be exactly 12 digits.")
    else:
        add_face(aadhaar, num_frames=100)
