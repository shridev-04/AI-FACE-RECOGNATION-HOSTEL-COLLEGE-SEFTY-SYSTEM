import os
import cv2
import time

# डेटाबेस फोल्डर
DATASET_DIR = "student_database"
if not os.path.exists(DATASET_DIR):
  os.makedirs(DATASET_DIR)

# OpenCV Cascade Load कर रहे हैं
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

student_name = input("Enter Student Name / ID for Registration: ").strip()
student_path = os.path.join(DATASET_DIR, student_name)

if not os.path.exists(student_path):
  os.makedirs(student_path)

cap = cv2.VideoCapture(0)

# 5 मुख्य एंगल्स
angles = [
    ("1. Look STRAIGHT into the camera", 40),
    ("2. Turn your head slightly LEFT", 40),
    ("3. Turn your head slightly RIGHT", 40),
    ("4. Tilt your head UP", 40),
    ("5. Tilt your head DOWN", 40),
]

print(
    "\n🚀 SMART REGISTRATION STARTED!"
    "\nMake sure your room has good lighting for smooth capture.\n"
)
time.sleep(2)

total_captured = 0

for instruction, target_count in angles:
  print(f"\n👉 ACTION REQUIRED: {instruction}")
  print(f"Get ready... Capturing {target_count} images for this angle...")
  time.sleep(2)

  count = 0
  while count < target_count:
    ret, frame = cap.read()
    if not ret:
      break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # scaleFactor और minNeighbors को थोड़ा लचीلا बनाया है ताकि चेहरा आसानी से पकड़ा जाए
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50)
    )

    for x, y, w, h in faces:
      count += 1
      total_captured += 1
      face_img = frame[y : y + h, x : x + w]

      # फाइल सेव कर रहे हैं
      file_name = os.path.join(student_path, f"img_{total_captured}.jpg")
      cv2.imwrite(file_name, face_img)

      # स्क्रीन पर प्रोग्रेस और बॉक्स दिखाना
      cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
      cv2.putText(
          frame,
          f"{instruction}",
          (20, 40),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.6,
          (0, 255, 255),
          2,
      )
      cv2.putText(
          frame,
          f"Progress: {count}/{target_count}",
          (20, 80),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.6,
          (0, 255, 0),
          2,
      )
      break

    cv2.imshow("Smart Multi-Angle Enrollment", frame)

    if cv2.waitKey(40) & 0xFF == ord("q"):
      break
  else:
    continue
  break

cap.release()
cv2.destroyAllWindows()

print(
    f"\n🎉 SUCCESS! Total {total_captured} facial images saved for"
    f" '{student_name}'!"
)
print(f"📁 Folder Location: {student_path}")