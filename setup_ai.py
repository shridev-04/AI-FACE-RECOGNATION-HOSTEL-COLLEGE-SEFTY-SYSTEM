import os
import cv2
import numpy as np

# डेटाबेस फोल्डर जहाँ फोटोज़/डेटा सेव होगा
DATASET_DIR = "student_database"
if not os.path.exists(DATASET_DIR):
  os.makedirs(DATASET_DIR)

# OpenCV का प्री-ट्रेंड Haar Cascade / Face Detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

student_name = input("Enter Student Name / ID: ").strip()
student_path = os.path.join(DATASET_DIR, student_name)

if not os.path.exists(student_path):
  os.makedirs(student_path)

cap = cv2.VideoCapture(0)
count = 0

print("\n📸 Registering Face... Look Straight, Left, and Right into the Camera!")
print("Press 'q' to stop early.\n")

while True:
  ret, frame = cap.read()
  if not ret:
    print("Camera not working!")
    break

  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(
      gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100)
  )

  for x, y, w, h in faces:
    count += 1
    face_img = frame[y : y + h, x : x + w]

    # फोटो सेव की जा रही है (Multi-Angle Captures)
    file_name = os.path.join(student_path, f"{student_name}_{count}.jpg")
    cv2.imwrite(file_name, face_img)

    # स्क्रीन पर चेहरा हाइलाइट करने के लिए
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(
        frame,
        f"Capturing {count}/20",
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
    )

  cv2.imshow("Student Enrollment System", frame)

  # 20 फोटोज़ (अलग-अलग एंगल्स) कैप्चर होने के बाद बंद हो जाएगा
  if count >= 20 or cv2.waitKey(100) & 0xFF == ord("q"):
    break

cap.release()
cv2.destroyAllWindows()

print(
    f"\n🎉 Successfully captured {count} facial angles for '{student_name}'!"
)
print(f"📁 Saved at: {student_path}")