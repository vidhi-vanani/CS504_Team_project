import cv2
import face_recognition
import numpy as np
import time
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://tejasreekokkanti20:Dhanama123@506tp.evuyp7x.mongodb.net/?retryWrites=true&w=majority&appName=506TP")
db = client["mfa_db"]
users = db["users"]

# -----------------------------
# Face Registration (Capture + Save to DB)
# -----------------------------
def register_face(username):
    """Captures and stores user's face encoding in MongoDB"""
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("[ERROR] Could not access webcam.")
        return False

    print("[INFO] Please position your face. Press 'q' to capture.")

    start_time = time.time()
    while time.time() - start_time < 30:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to capture frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            face_encoding = face_recognition.face_encodings(rgb_frame)[0]
            users.update_one(
                {"username": username},
                {"$set": {"face_encoding": face_encoding.tolist()}},
                upsert=True
            )
            print("[SUCCESS] Face registered for:", username)
            video_capture.release()
            cv2.destroyAllWindows()
            return True

        cv2.imshow("Register Face", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return False

# -----------------------------
# Face Verification
# -----------------------------
def verify_face(username):
    """Verifies the user's face against stored encoding in DB"""
    user = users.find_one({"username": username})
    if not user or "face_encoding" not in user:
        print("[ERROR] No stored face found for user:", username)
        return False

    stored_encoding = np.array(user["face_encoding"])

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("[ERROR] Could not access webcam.")
        return False

    print("[INFO] Face verification started. Press 'q' to cancel.")

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
                print("[SUCCESS] Face verified for:", username)
                video_capture.release()
                cv2.destroyAllWindows()
                return True

        cv2.imshow("Verify Face", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    print("[FAILURE] Face verification failed.")
    video_capture.release()
    cv2.destroyAllWindows()
    return False
