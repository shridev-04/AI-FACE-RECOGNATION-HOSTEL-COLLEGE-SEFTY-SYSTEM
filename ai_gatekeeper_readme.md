# 🛡️ Distributed Enterprise AI Gatekeeper System

An edge-optimized, multi-node facial recognition and intrusion tracking system engineered for multi-floor facilities (hostels, corporate offices, high-security zones) using IP camera networks and distributed CPU processing.

---

## 📌 System Architecture & Key Concepts

```
                  +-----------------------------------+
                  |  30 Wired IP Cameras (PoE Powered) |
                  +-----------------+-----------------+
                                    |
                                    v
                     +--------------+--------------+
                     |    PoE Network Switch      |
                     +--------------+--------------+
                                    |
        +---------------------------+---------------------------+
        | (LAN RTSP Streams)        |                           |
        v                           v                           v
+-------+-------+           +-------+-------+           +-------+-------+
|  CPU Node 1   |           |  CPU Node 2   |           |  CPU Node 3   |
| (10 Cameras)  |           | (10 Cameras)  |           | (10 Cameras)  |
+-------+-------+           +-------+-------+           +-------+-------+
        |                           |                           |
        +---------------------------+---------------------------+
                                    |
            (Async RAM Cache Sync via Local Network / Master Node)
                                    |
                                    v
                     +--------------+--------------+
                     | Master Database Repository  |
                     |  - Permanent Student Logs   |
                     |  - Temporary Visitor Logs   |
                     |  - Intruder Path Registry   |
                     +-----------------------------+
```

### 1. Tiered Storage Architecture
* **Permanent Database (`student_database/`):** Permanent student/employee face profiles, stored long-term.
* **Temporary Visitor Database (`visitor_database/`):** Short-term profiles (e.g., parents, contractors) registered at entry and cleared upon exit.
* **Unknown Intruder Registry (`unknown_captures/`):** Captures unauthorized entries with assigned tracking IDs without spamming redundant logs.

### 2. Low-Latency Distributed Processing
* **Local RAM Caching:** Each CPU node loads the database histograms into local system RAM at startup. Frame verification occurs against RAM in microseconds ($<1\text{ms}$), eliminating LAN bottleneck issues.
* **Background LAN Synchronization:** Event alerts and unknown individual registrations sync asynchronously in the background across nodes to maintain path tracking without interrupting video streams.

---

## 🛠️ Requirements & Installation

### Core Dependencies
* Python 3.8+
* OpenCV (`opencv-python`)
* NumPy (`numpy`)

### Quick Setup

Run the automated dependency installer script:

```bash
python install_dependencies.py
```

---

## 📂 Project Structure

```
.
├── install_dependencies.py   # Automated dependency checker & installer
├── gatekeeper_master.py      # Core recognition engine with anti-false-detection guard
├── student_database/         # Permanent student face directories
│   ├── student_01/
│   └── student_02/
├── visitor_database/         # Temporary visitor face profiles
└── unknown_captures/         # Logged intruder/unknown image captures
```

---

## 🚀 Execution Guide

### 1. Register Profiles
Populate `student_database/` or `visitor_database/` with subfolders named after individuals containing face images from multiple angles.

```
student_database/
└── Shridev/
    ├── img1.jpg
    ├── img2.jpg
    └── img3.jpg
```

### 2. Run Gatekeeper Engine
To launch the core engine:

```bash
python gatekeeper_master.py
```

---

## 🛡️ Multi-Stage Verification Pipeline (Anti-False-Positive Engine)

To prevent misidentifications (e.g., detecting walls, shadows, or hands as faces):

1. **Aspect-Ratio Filtering:** Rejects bounding boxes with non-standard face proportions ($\text{Ratio} \notin [0.7, 1.3]$).
2. **Skin-Tone Verification:** Inspects HSV color space inside bounding boxes. If human skin pixel percentage is $<12\%$, the bounding box is immediately discarded.
3. **CLAHE Enhancement:** Equalizes dynamic lighting changes across indoor and outdoor camera zones.
4. **Temporal Streak Verification:** Requires an unrecognized face to persist across $>6$ consecutive frames before trigger alerts and logging an unknown record.

---

## ⚙️ Configuration File (`config.json` Example)

Deploy this JSON structure on each CPU node to bind specific camera RTSP streams locally:

```json
{
  "cpu_unit_id": "Node_01_Floor_1",
  "master_sync_url": "192.168.1.100",
  "cameras": [
    {"id": "Cam_01_MainGate", "url": "rtsp://admin:pass@192.168.1.101:554/stream1"},
    {"id": "Cam_02_Lobby",    "url": "rtsp://admin:pass@192.168.1.102:554/stream1"}
  ]
}
```