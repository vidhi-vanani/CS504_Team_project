import time
import face_recognition
import cv2
import numpy as np
import os
from pymongo import MongoClient

# File-based backup
KNOWN_FACES_DIR = "known_faces"

# MongoDB connection (cloud)
client = MongoClient("mongodb+srv://tejasreekokkanti20:Dhanama123@506tp.evuyp7x.mongodb.net/?retryWrites=true&w=majority&appName=506TP")
db = client["mfa_db"]
users = db["users"]

# -----------------------------
# Register Face
# -----------------------------
def register_face(username):
    """
    Capture face and save encoding to MongoDB.
    Also saves the image in local folder for backup.
    """
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("[ERROR] Could not access webcam.")
        return False

    print("[INFO] Please look at the camera. Press 'q' to register.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to capture frame.")
            break

        cv2.imshow("Register Face", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            if face_locations:
                face_encoding = face_recognition.face_encodings(rgb_frame)[0]
                users.update_one(
                    {"username": username},
                    {"$set": {"face_encoding": face_encoding.tolist()}},
                    upsert=True
                )

                # Save image locally
                os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
                local_path = os.path.join(KNOWN_FACES_DIR, f"{username}.jpg")
                cv2.imwrite(local_path, frame)

                print(f"[SUCCESS] Face registered for {username}")
                video_capture.release()
                cv2.destroyAllWindows()
                return True
            else:
                print("[ERROR] No face detected. Try again.")

    video_capture.release()
    cv2.destroyAllWindows()
    return False

# -----------------------------
# Verify Face
# -----------------------------
def verify_face(username):
    """
    Verify face using stored encoding from MongoDB.
    """
    user = users.find_one({"username": username})
    if not user or "face_encoding" not in user:
        print(f"[ERROR] No face encoding found for {username}")
        return False

    stored_encoding = np.array(user["face_encoding"])

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("[ERROR] Could not access webcam.")
        return False

    print("[INFO] Verifying... Please look at the camera. Press 'q' to quit.")

    match_found = False
    start_time = time.time()
    while time.time() - start_time < 30:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to read frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame)

        for face_encoding in face_encodings:
            match = face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=0.5)[0]
            if match:
                match_found = True
                break

        cv2.imshow("Verify Face", frame)
        if cv2.waitKey(1) & 0xFF == ord("q") or match_found:
            break

    video_capture.release()
    cv2.destroyAllWindows()

    if match_found:
        print(f"[SUCCESS] Face verified for {username}")
    else:
        print(f"[FAILURE] Face verification failed for {username}")
    return match_found
