# Imou Camera Scanner & Viewer

Bộ công cụ Python đơn giản giúp tự động quét, tìm kiếm và xem trực tiếp (Live Stream) các camera Imou/Dahua trong mạng WiFi nội bộ (LAN).

## Tính năng chính

- **Camera Scanner**: Tự động quét toàn bộ dải mạng để tìm thiết bị mở cổng RTSP (554). Tự động thử kết nối với mật khẩu cho trước.
- **Stream Viewer**: Mở nhiều cửa sổ xem camera cùng lúc từ danh sách đã quét được.
- **Hỗ trợ tiếng Việt**: Giao diện dòng lệnh và comment code hoàn toàn bằng tiếng Việt.

## Yêu cầu cài đặt

- Python 3.8 trở lên
- Các thư viện phụ thuộc:
  ```bash
  pip install -r requirements.txt
  ```
  _(Bao gồm: `opencv-python`, `requests`, `numpy`, `ultralytics`)_

## Hướng dẫn sử dụng

### 1. Cấu hình

Mở file `camera_scanner.py`, tìm dòng sau để sửa mật khẩu camera của bạn (Safety Code trên tem hoặc mật khẩu đã đổi):

```python
SAFETY_CODE = ""  # Thay mật khẩu của bạn vào đây
```

### 2. Quét tìm Camera

Chạy lệnh sau để quét mạng và tạo file danh sách `camera_list.txt`:

```bash
python camera_scanner.py
```

_Kết quả sẽ hiển thị các IP tìm được và trạng thái kết nối._

### 3. Xem Camera

Sau khi quét xong, chạy lệnh sau để mở các cửa sổ xem camera:

```bash
python stream_viewer.py
```

_Nhấn phím **'q'** trên cửa sổ video để tắt._

## Cấu trúc thư mục

- `camera_scanner.py`: Script quét mạng tìm camera.
- `stream_viewer.py`: Script xem video từ danh sách đã quét.
- `requirements.txt`: Danh sách thư viện cần thiết.
- `camera_list.txt`: (Tự động tạo) Chứa thông tin IP và link RTSP của camera.

## Lưu ý

- Máy tính chạy code và Camera phải kết nối chung một mạng WiFi/LAN.
- Nếu không tìm thấy camera, hãy kiểm tra lại mật khẩu `SAFETY_CODE` và đảm bảo máy tính không bật VPN/Firewall chặn kết nối nội bộ.

## Module Mở Rộng: Phát Hiện Té Ngã (AI Fall Detection)

Dự án này bao gồm một module nâng cao sử dụng **YOLO Pose** để phát hiện hành động té ngã trong thời gian thực.

- **Thư mục:** `Fall detection - Phát hiện ngã/`
- **Tính năng:**
  - Nhận diện dáng người và cảnh báo khi có người ngã.
  - Tự động chụp ảnh/quay video sự kiện.
  - Gửi cảnh báo qua Telegram.
- **Tác giả module:** Tiktok @camerasontung
- **Chi tiết:** Xem file `README.md` bên trong thư mục `Fall detection - Phát hiện ngã` để biết cách cài đặt và tinh chỉnh độ nhạy.
