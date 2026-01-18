#!/usr/bin/env python3
import cv2, time, threading, requests, numpy as np
from ultralytics import YOLO
from collections import defaultdict

# ================= CONFIG =================
CAMERA_URL = "rtsp://admin:Tung1234@192.168.1.4:554/cam/realmonitor?channel=1&subtype=0"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

YOLO_MODEL = "yolov8n.pt"    # hoặc yolov8s.pt
CONF_THRESHOLD = 0.3
PIXEL_COUNT_THRESHOLD = 100
SENSITIVITY = 1.2
SEND_COOLDOWN = 6
SHOW_WINDOWS = True

LIVE_WIDTH = 640
LIVE_HEIGHT = 360

COLOR_RANGES = {
    "red": [((0,50,50),(8,255,255)), ((170,50,50),(180,255,255))],
    "green": [((35,50,50),(85,255,255))],
    "yellow": [((18,50,50),(35,255,255))],
    "blue": [((90,50,50),(130,255,255))],
    "purple": [((125,50,50),(150,255,255))],
    "pink": [((145,50,50),(170,255,255))],
    "orange": [((10,50,50),(18,255,255))],
    "cyan": [((80,50,50),(90,255,255))],
    "white": [((0,0,200),(180,40,255))]
}

# ================= HELPERS =================
def send_telegram_photo(image_bgr, caption="Phát hiện lũ lụt - Flood detection"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    _, jpg = cv2.imencode(".jpg", image_bgr)
    try:
        r = requests.post(url, files={"photo": jpg.tobytes()},
                          data={"chat_id": CHAT_ID, "caption": caption}, timeout=8)
        return r.status_code == 200
    except:
        return False

def get_color_masks(bgr_roi):
    hsv = cv2.cvtColor(bgr_roi, cv2.COLOR_BGR2HSV)
    masks = {}
    for color, ranges in COLOR_RANGES.items():
        mask = None
        for low, high in ranges:
            m = cv2.inRange(hsv, np.array(low), np.array(high))
            mask = m if mask is None else (mask | m)
        masks[color] = mask
    return masks

# ================= LOAD YOLO =================
print("Loading YOLO:", YOLO_MODEL)
model = YOLO(YOLO_MODEL)
inference_lock = threading.Lock()

# ================= CAMERA WORKER =================
class CameraWorker(threading.Thread):
    def __init__(self, url):
        super().__init__(daemon=True)
        self.url = url
        self.cap = None
        self.stop_flag = threading.Event()
        self.last_sent = defaultdict(lambda: 0)
        self.alert_text = ""
        self.latest_frame = None

    def open_capture(self):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, LIVE_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, LIVE_HEIGHT)
        return self.cap.isOpened()

    def run(self):
        while not self.stop_flag.is_set():
            if not self.cap or not self.cap.isOpened():
                if not self.open_capture():
                    time.sleep(1)
                    continue

            ret, frame = self.cap.read()
            if not ret:
                self.cap = None
                continue

            frame_resized = cv2.resize(frame, (LIVE_WIDTH, LIVE_HEIGHT))
            display_frame = frame_resized.copy()
            h, w = display_frame.shape[:2]

            with inference_lock:
                results = model(frame_resized, verbose=False, imgsz=640)
            res = results[0]

            detected_colors = []

            for box in res.boxes:
                try:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                except:
                    continue
                if cls_id != 32 or conf < CONF_THRESHOLD:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1 = max(0,x1), max(0,y1)
                x2, y2 = min(w-1,x2), min(h-1,y2)
                obj = frame_resized[y1:y2, x1:x2]
                if obj.size==0: continue

                masks = get_color_masks(obj)
                for color, mask in masks.items():
                    px = int(mask.sum()/255)
                    threshold = max(PIXEL_COUNT_THRESHOLD, 0.01*(x2-x1)*(y2-y1)/SENSITIVITY)
                    if px >= threshold:
                        detected_colors.append(color)
                        cv2.rectangle(display_frame,(x1,y1),(x2,y2),(0,255,0),2)
                        cv2.putText(display_frame,f"{color} ({px})",(x1,y1-5),
                                    cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)

                        now = time.time()
                        if now - self.last_sent[color] > SEND_COOLDOWN:
                            self.last_sent[color]=now
                            send_telegram_photo(obj, f"[Camera] Detect {color} ball")
                            self.alert_text = "PHAT HIEN LU LUT - Flood detection"

            if self.alert_text:
                cv2.putText(display_frame, self.alert_text, (10,30),
                            cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)

            self.latest_frame = display_frame

        if self.cap:
            self.cap.release()

    def stop(self):
        self.stop_flag.set()

# ================= MAIN =================
def main():
    worker = CameraWorker(CAMERA_URL)
    worker.start()
    print("Running... Press Q to quit.")
    try:
        while True:
            if worker.latest_frame is not None and SHOW_WINDOWS:
                cv2.imshow("Camera LiveView", worker.latest_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                time.sleep(0.05)
    except KeyboardInterrupt:
        print("Stopping...")
    worker.stop()
    cv2.destroyAllWindows()

if __name__=="__main__":
    main()
