import face_recognition
import cv2
import numpy as np
import os

KNOWN_FACES_DIR = "known_faces"  # Folder containing images of authorized users

def load_known_faces():
    """
    Load known faces and their encodings from the known_faces directory.
    """
    known_encodings = []
    known_names = []

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(KNOWN_FACES_DIR, filename)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                # Remove file extension to get username
                known_names.append(os.path.splitext(filename)[0])
    return known_encodings, known_names

def verify_face(username):
    """
    Capture an image from the webcam and verify if the face matches the known face of the username.
    Returns True if verified, False otherwise.
    """
    known_encodings, known_names = load_known_faces()
    if username not in known_names:
        print(f"[ERROR] No known face data found for user: {username}")
        return False

    user_index = known_names.index(username)
    user_encoding = known_encodings[user_index]

    # Initialize webcam
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("[ERROR] Could not open webcam")
        return False

    print("Please position your face in front of the webcam. Press 'q' to quit.")

    verified = False

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to capture frame")
            break

        # Resize frame to speed up processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]  # BGR to RGB

        # Find all faces and face encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding in face_encodings:
            # Compare face to the known user face encoding
            matches = face_recognition.compare_faces([user_encoding], face_encoding, tolerance=0.5)
            if True in matches:
                print("[INFO] Face verified!")
                verified = True
                break

        # Display the frame
        cv2.imshow('Face Verification', frame)

        if verified:
            break

        # Quit if user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release webcam and close window
    video_capture.release()
    cv2.destroyAllWindows()

    return verified
