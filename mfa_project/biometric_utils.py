import cv2
import face_recognition
import numpy as np
from pymongo import MongoClient
import time

client = MongoClient("mongodb+srv://tejasreekokkanti20:Dhanama123@506tp.evuyp7x.mongodb.net/?retryWrites=true&w=majority&appName=506TP")
db = client["mfa_db"]
users = db["users"]

def capture_face(username):
    """Captures face image for biometric authentication"""
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Error: Could not access webcam.")
        return False
    
    start_time = time.time()
    while time.time() - start_time < 30:  # 30-second timeout
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if face_locations:
            face_encoding = face_recognition.face_encodings(rgb_frame)[0]
            users.update_one({"username": username}, {"$set": {"face_encoding": face_encoding.tolist()}})
            print("Face registered successfully!")
            video_capture.release()
            cv2.destroyAllWindows()
            return True
        
        cv2.imshow("Face Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return False

def verify_face(username):
    """Verifies user face using stored face encoding"""
    user = users.find_one({"username": username})
    if not user or "face_encoding" not in user:
        return False
    
    stored_encoding = np.array(user["face_encoding"])

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Error: Could not access webcam.")
        return False
    
    start_time = time.time()
    while time.time() - start_time < 30:  # 30-second timeout
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if face_locations:
            current_encoding = face_recognition.face_encodings(rgb_frame)[0]
            match = face_recognition.compare_faces([stored_encoding], current_encoding)[0]
            video_capture.release()
            cv2.destroyAllWindows()
            return match
        
        cv2.imshow("Face Verification", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    video_capture.release()
    cv2.destroyAllWindows()
    return False