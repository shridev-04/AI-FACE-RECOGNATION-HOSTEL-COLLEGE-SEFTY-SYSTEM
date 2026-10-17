import os
import cv2
import numpy as np

# डेटाबेस और अननोन फ़ोल्डर का रास्ता
DATASET_DIR = "student_database"
UNKNOWN_DIR = "unknown_captures"

if not os.path.exists(UNKNOWN_DIR):
  os.makedirs(UNKNOWN_DIR)

print("🧠 Loading Skin-Protected Student Database...")
known_histograms = {}

if os.path.exists(DATASET_DIR):
  for student_name in os.listdir(DATASET_DIR):
    student_path = os.path.join(DATASET_DIR, student_name)
    if os.path.isdir(student_path):
      known_histograms[student_name] = []
      for img_name in os.listdir(student_path):
        img_path = os.path.join(student_path, img_name)
        img = cv2.imread(img_path)
        if img is not None:
          hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
          hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
          cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
          known_histograms[student_name].append(hist)

print(
    f"✅ Database loaded successfully! Total students:"
    f" {list(known_histograms.keys())}\n"
)
print(
    "🎥 Starting Skin-Guarded Hostel Gatekeeper... Press 'q' to exit."
)

cap = cv2.VideoCapture(0)
unknown_count = 0
unknown_streak_counter = {}

# डिटेक्टर्स
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
profile_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_profileface.xml"
)

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

while True:
  ret, frame = cap.read()
  if not ret:
    print("Camera error!")
    break

  # लाइटिंग फिक्स
  lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
  l_f, a_f, b_f = cv2.split(lab_frame)
  cl_f = clahe.apply(l_f)
  limg_f = cv2.merge((cl_f, a_f, b_f))
  enhanced_frame = cv2.cvtColor(limg_f, cv2.COLOR_LAB2BGR)
  gray_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2GRAY)

  # चेहरे ढूंढना (फ्रंट और साइड)
  faces_front = face_cascade.detectMultiScale(
      gray_frame, scaleFactor=1.08, minNeighbors=4, minSize=(30, 30)
  )
  faces_left = profile_cascade.detectMultiScale(
      gray_frame, scaleFactor=1.08, minNeighbors=4, minSize=(30, 30)
  )

  flipped_gray = cv2.flip(gray_frame, 1)
  faces_right_flipped = profile_cascade.detectMultiScale(
      flipped_gray, scaleFactor=1.08, minNeighbors=4, minSize=(30, 30)
  )

  faces = []
  if len(faces_front) > 0:
    faces.extend(faces_front)
  if len(faces_left) > 0:
    faces.extend(faces_left)

  frame_width = gray_frame.shape[1]
  for rx, ry, rw, rh in faces_right_flipped:
    original_x = frame_width - (rx + rw)
    faces.append((original_x, ry, rw, rh))

  for x, y, w, h in faces:
    # 1. सख्त आस्पेक्ट रेशियो (फालतू लंबी या चौड़ी चीज़ों को भगाने के लिए)
    aspect_ratio = w / float(h)
    if aspect_ratio < 0.7 or aspect_ratio > 1.3:
      continue

    # पैडिंग
    h_pad = int(h * 0.1)
    w_pad = int(w * 0.1)
    y1 = max(0, y - h_pad)
    y2 = min(frame.shape[0], y + h + h_pad)
    x1 = max(0, x - w_pad)
    x2 = min(frame.shape[1], x + w + w_pad)

    face_roi = enhanced_frame[y1:y2, x1:x2]

    try:
      # 🛡️ 2. SKIN TONE FILTER (असली जादू यहाँ है!)
      # यह चेक करेगा कि डिटेक्ट हुए हिस्से में कम से कम 15% इंसानी त्वचा (Skin) है या नहीं।
      # अगर दीवार, हाथ, या कोई अन्य वस्तु होगी, तो स्किन नहीं मिलेगी और यह उसे तुरंत खारिज कर देगा।
      hsv_roi_for_skin = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
      lower_skin = np.array([0, 20, 70], dtype=np.uint8)
      upper_skin = np.array([20, 250, 255], dtype=np.uint8)
      skin_mask = cv2.inRange(hsv_roi_for_skin, lower_skin, upper_skin)
      skin_pixel_count = cv2.countNonZero(skin_mask)
      total_pixels = face_roi.shape[0] * face_roi.shape[1]

      if (
          total_pixels > 0
          and (skin_pixel_count / float(total_pixels)) < 0.12
      ):
        continue  # दीवार या खाली जगह है, इसे चेहरा मत मानो!

      # अगर त्वचा मिल गई, तो अब नॉर्मل मैचिंग करेंगे
      hsv_live = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
      hist_live = cv2.calcHist([hsv_live], [0, 1], None, [50, 60], [0, 180, 0, 256])
      cv2.normalize(hist_live, hist_live, 0, 1, cv2.NORM_MINMAX)

      matched_name = "UNKNOWN"
      box_color = (0, 0, 255)
      highest_score = 0.0

      for student_name, hist_list in known_histograms.items():
        for stored_hist in hist_list:
          score = cv2.compareHist(stored_hist, hist_live, cv2.HISTCMP_CORREL)
          if score > highest_score:
            highest_score = score

        if highest_score > 0.42:
          matched_name = student_name
          box_color = (0, 255, 0)
          break

      face_key = f"{x}_{y}"

      if matched_name == "UNKNOWN":
        if face_key not in unknown_streak_counter:
          unknown_streak_counter[face_key] = 0
        unknown_streak_counter[face_key] += 1

        if unknown_streak_counter[face_key] > 6:
          unknown_count += 1
          unknown_img_path = os.path.join(
              UNKNOWN_DIR, f"clean_unknown_{unknown_count}.jpg"
          )
          cv2.imwrite(unknown_img_path, face_roi)
          box_color = (0, 0, 255)
          display_text = f"ALERT! UNKNOWN ({highest_score:.2f})"
        else:
          box_color = (0, 255, 255)
          display_text = f"Checking... ({highest_score:.2f})"
      else:
        if face_key in unknown_streak_counter:
          del unknown_streak_counter[face_key]
        display_text = f"{matched_name} ({highest_score:.2f})"

      # स्क्रीन पर दिखाना
      cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
      cv2.putText(
          frame,
          display_text,
          (x, y - 10),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.6,
          box_color,
          2,
      )
    except Exception as e:
      pass

  cv2.imshow("Skin-Protected Hostel Gatekeeper", frame)

  if cv2.waitKey(1) & 0xFF == ord("q"):
    break

cap.release()
cv2.destroyAllWindows()