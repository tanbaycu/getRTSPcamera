# Hệ thống Phát hiện Té ngã (Fall Detection) - SmartSense

**Tác giả:** Tiktok @camerasontung  
**Link tài nguyên gốc:** [Google Drive](https://drive.google.com/drive/folders/13G2yiGRZfSgKodJGPArPn4p8xw0Y6uNo?usp=sharing)

---

## 📂 Cấu trúc thư mục

Thư mục này chứa các mã nguồn và tài liệu hướng dẫn cho hệ thống phát hiện té ngã sử dụng AI (YOLO Pose).

- **`Fall detection.py` / `V12.5_SmartSense.py`**: Mã nguồn chính của chương trình. Sử dụng mô hình AI để nhận diện dáng người và phát hiện hành động ngã.
- **`yolov8n-pose.pt`**: Mô hình AI (YOLO v8 Nano Pose) đã được huấn luyện để nhận diện các điểm khớp xương trên cơ thể người.
- **`events/`**: Thư mục lưu trữ hình ảnh/video khi phát hiện sự kiện ngã.
- **Tài liệu hướng dẫn:**
  - `Hướng dẫn chi tiết telegram.txt/docx`: Cách tạo Bot Telegram và lấy Token/Chat ID để nhận cảnh báo.
  - `Lấy RTSP.txt`: Hướng dẫn cách lấy đường dẫn luồng video (RTSP) từ camera Imou/Dahua.
  - `Điều chỉnh độ nhạy phát hiện ngã.txt`: Hướng dẫn tinh chỉnh các tham số AI.

---

## ⚙️ Hướng dẫn Tinh chỉnh Độ nhạy (Sensitivity)

Để hệ thống hoạt động chính xác với môi trường nhà bạn, bạn có thể cần điều chỉnh các thông số trong file code chính (`Fall detection.py`). Dưới đây là giải thích chi tiết:

### 1. `TORSO_ANGLE_THRESHOLD` (Góc nghiêng cơ thể)

- **Mặc định:** `45` độ.
- **Tác dụng:** Xác định xem người đó đang nghiêng bao nhiêu thì bị coi là ngã.
- **Điều chỉnh:**
  - _Nhạy hơn (Dễ báo ngã):_ Giảm xuống **40**. (Cảnh báo sớm, kể cả khi mới hơi ngả).
  - _Bớt nhạy (Tránh báo sai):_ Tăng lên **50-55**. (Chỉ báo khi ngã hẳn).

### 2. `STATIONARY_SECONDS` (Thời gian nằm im)

- **Mặc định:** `2.2` giây.
- **Tác dụng:** Thời gian người đó phải nằm bất động sau khi ngã để hệ thống xác nhận.
- **Điều chỉnh:**
  - _Nhạy hơn:_ Giảm xuống **1.5 - 2.0** giây.
  - _Bớt nhạy:_ Tăng lên **3.0 - 4.0** giây. (Tránh nhầm với việc cúi xuống nhặt đồ nhanh).

### 3. `STATIONARY_MOVEMENT_PX` (Ngưỡng chuyển động tĩnh)

- **Mặc định:** `35` pixels.
- **Tác dụng:** Mức độ cử động nhỏ cho phép trong khi "nằm im".
- **Điều chỉnh:**
  - _Nhạy hơn:_ Tăng lên **40-50**. (Vẫn coi là ngã dù có cử động nhẹ chân tay).
  - _Bớt nhạy:_ Giảm xuống **20-25**. (Chỉ coi là ngã khi nằm bất động hoàn toàn).

### 4. `FALL_CONFIRM_FRAMES` (Số khung hình xác nhận)

- **Mặc định:** `2` frames.
- **Tác dụng:** Số lần liên tiếp AI nhìn thấy dáng ngã mới chốt kết quả.
- **Điều chỉnh:**
  - _Nhạy hơn:_ Giảm xuống **1**.
  - _Bớt nhạy:_ Tăng lên **3-4**. (Giảm báo ảo do camera bị nhiễu chớp nhoáng).

### 5. `COOLDOWN_SECONDS` (Thời gian chờ báo lại)

- **Mặc định:** `10` giây.
- **Tác dụng:** Khoảng cách giữa 2 lần gửi tin nhắn cảnh báo liên tiếp. Tăng lên nếu bạn không muốn bị spam tin nhắn.

---

## 🚀 Cách sử dụng nhanh

1.  Đảm bảo đã cài đặt đủ thư viện: `pip install ultralytics opencv-python requests`
2.  Mở file script chính, cập nhật:
    - Link RTSP camera của bạn.
    - Telegram Bot Token & Chat ID.
3.  Chạy script: `python "Fall detection.py"`

> **Lưu ý:** Luôn kiểm tra thực tế bằng cách giả vờ ngã (cẩn thận!) để tinh chỉnh thông số cho phù hợp nhất.
