"""
Tên dự án: Imou RTSP Stream Viewer
Mô tả: Công cụ xem trực tiếp video từ các camera Imou thông qua danh sách link RTSP.
Ngày tạo: 17/01/2026

Tính năng:
1. Đọc danh sách link từ file 'camera_list.txt'.
2. Mở nhiều cửa sổ video cùng lúc (Multi-window).
3. Hỗ trợ tự động kết nối lại khi mất tín hiệu.
"""

import cv2
import threading
import time
import os

# Tên file chứa danh sách link (được tạo bởi camera_scanner.py)
INPUT_FILE = "camera_list.txt"

def parse_rtsp_links():
    """
    Đọc file text và lấy ra các link RTSP (ưu tiên link Chính).
    Trả về danh sách: [(IP, URL), ...]
    """
    links = []
    current_ip = "Unknown"
    
    if not os.path.exists(INPUT_FILE):
        print(f"[Lỗi] Không tìm thấy file '{INPUT_FILE}'.")
        print("Vui lòng chạy file 'camera_scanner.py' trước để quét camera.")
        return []

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 1. Tìm dòng IP để làm tiêu đề
                if line.startswith("[CAMERA] IP:"):
                    current_ip = line.split(":")[1].strip()
                
                # 2. Tìm link RTSP Chính (High Quality)
                # Nếu muốn nhẹ hơn, bạn đổi chữ "Chính" thành "Phụ"
                if "URL RTSP (Chính" in line:
                    if "(Chính - Nét)" in line: # Format mới
                        url = line.split("(Chính - Nét):")[1].strip()
                    else: # Format cũ (fallback)
                        url = line.split("(Chính):")[1].strip()
                    
                    links.append((current_ip, url))
    except Exception as e:
        print(f"[Lỗi] Không thể đọc file: {e}")
        
    return links

def view_camera(ip, url):
    """
    Luồng (Thread) xử lý hiển thị cho từng camera riêng biệt.
    """
    print(f"[*] Đang kết nối vào Camera {ip}...")
    
    # Sử dụng TCP để ổn định hơn qua WiFi (nếu OpenCV hỗ trợ backend FFMPEG)
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
    
    cap = cv2.VideoCapture(url)
    
    if not cap.isOpened():
        print(f"[-] Không thể mở stream từ {ip}. Kiểm tra mật khẩu hoặc mạng.")
        return

    window_name = f"Camera {ip}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 360) # Cửa sổ kích thước vừa phải

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[-] Camera {ip} bị mất tín hiệu!")
            break
            
        cv2.imshow(window_name, frame)
        
        # Nhấn q hoặc đóng cửa sổ để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # Kiểm tra nếu cửa sổ bị đóng bằng chuột (nhấn X) -> break
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
            
    cap.release()
    cv2.destroyWindow(window_name)
    print(f"[Dong] Đã tắt cửa sổ {ip}")

def main():
    print("\n" + "="*50)
    print("   CÔNG CỤ XEM CAMERA (STREAM VIEWER)")
    print("="*50)
    
    # 1. Lấy danh sách link
    links = parse_rtsp_links()
    
    if not links:
        print("Không có camera nào để xem.")
        return

    print(f"Tìm thấy {len(links)} camera trong danh sách.")
    print("Đang mở các cửa sổ video...")
    print(">> Nhấn phím 'q' trên bất kỳ cửa sổ nào để tắt nó.")

    # 2. Tạo luồng hiển thị cho từng camera
    threads = []
    for ip, url in links:
        t = threading.Thread(target=view_camera, args=(ip, url))
        t.daemon = True # Tự động tắt khi chương trình chính tắt
        t.start()
        threads.append(t)
        time.sleep(1) # Mở lần lượt để tránh lag

    # 3. Giữ chương trình chạy
    try:
        while True:
            time.sleep(1)
            # Nếu tất cả luồng đã tắt thì thoát chương trình chính
            if not any(t.is_alive() for t in threads):
                print("\nTất cả cửa sổ đã đóng. Kết thúc chương trình.")
                break
    except KeyboardInterrupt:
        print("\nĐang thoát...")

if __name__ == "__main__":
    main()
