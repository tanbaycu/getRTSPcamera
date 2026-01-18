"""
Tên dự án: Imou Camera Scanner
Mô tả: Công cụ quét mạng nội bộ để tìm kiếm và kiểm tra kết nối RTSP đến các camera Imou/Dahua.
Ngày tạo: 17/01/2026

Tính năng:
1. Tự động phát hiện dải mạng WiFi hiện tại.
2. Quét toàn bộ 254 địa chỉ IP để tìm cổng 554 (RTSP).
3. Thử kết nối với mật khẩu đã cung cấp (Safety Code).
4. Xuất kết quả ra file 'camera_list.txt'.
"""

import cv2
import socket
import time
import os
from concurrent.futures import ThreadPoolExecutor

# ================= CẤU HÌNH NGƯỜI DÙNG =================
# Mật khẩu "Safety Code" in trên tem camera hoặc mật khẩu thiết bị bạn đã đổi
SAFETY_CODE = "" 

# Tên file xuất kết quả
OUTPUT_FILE = "camera_list.txt" 
# ========================================================

def get_local_ip():
    """Lấy địa chỉ IP nội bộ của máy tính để xác định dải mạng."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Kết nối thử đến Google DNS (không gửi dữ liệu) để lấy IP Interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def check_rtsp_port(ip):
    """Kiểm tra xem IP có mở cổng 554 (RTSP) hay không."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5) # Timeout thấp (0.5s) để quét nhanh
            if s.connect_ex((ip, 554)) == 0:
                return True
    except:
        pass
    return False

def verify_camera(ip):
    """
    Thử đăng nhập vào Camera bằng mật khẩu đã cấu hình.
    Trả về thông tin chi tiết nếu thành công.
    """
    print(f"[*] Đang kiểm tra xác thực: {ip}")
    
    # 1. Thử Substream (Luồng phụ - Nhẹ, tải nhanh)
    # URL chuẩn cho Imou/Dahua/KBVision
    url_sub = f"rtsp://admin:{SAFETY_CODE}@{ip}:554/cam/realmonitor?channel=1&subtype=1"
    
    # Cố gắng mở luồng video
    cap = cv2.VideoCapture(url_sub)
    if cap.isOpened():
        cap.release()
        return {
            "ip": ip,
            "status": "Connectable", # Kết nối thành công
            "type": "Imou/Dahua",
            "url_sub": url_sub,
            "url_main": f"rtsp://admin:{SAFETY_CODE}@{ip}:554/cam/realmonitor?channel=1&subtype=0",
            "password": SAFETY_CODE
        }
        
    # 2. Nếu thất bại (cap.isOpened() == False)
    return {
        "ip": ip,
        "status": "Auth Failed / Error",
        "detail": "Cổng 554 mở nhưng sai mật khẩu hoặc bị chặn (lockout)."
    }

def main():
    print("\n" + "="*50)
    print("   CÔNG CỤ QUÉT CAMERA IMOU - RTSP SCANNER")
    print("="*50)
    
    # 1. Xác định mạng
    local_ip = get_local_ip()
    network_prefix = ".".join(local_ip.split(".")[:-1])
    print(f"[1] Địa chỉ IP máy tính: {local_ip}")
    print(f"[1] Dải mạng mục tiêu:   {network_prefix}.x")
    
    if local_ip == "127.0.0.1":
        print("Lỗi: Không tìm thấy kết nối mạng. Vui lòng kiểm tra WiFi/LAN.")
        return

    # 2. Quét cổng
    print("\n[2] Đang quét nhanh 254 IP để tìm cổng RTSP (554)...")
    ips = [f"{network_prefix}.{i}" for i in range(1, 255)]
    open_rtsp_ips = []
    
    # Sử dụng đa luồng (100 luồng) để quét cực nhanh
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(check_rtsp_port, ips)
        
    for ip, is_open in zip(ips, results):
        if is_open:
            print(f"    [+] Tìm thấy thiết bị online: {ip}")
            open_rtsp_ips.append(ip)
            
    if not open_rtsp_ips:
        print("\n[!] Không tìm thấy thiết bị nào mở cổng 554.")
        return

    # 3. Kiểm tra đăng nhập
    print(f"\n[3] Đang thử đăng nhập vào {len(open_rtsp_ips)} thiết bị bằng mật khẩu: {SAFETY_CODE}...")
    valid_cameras = []
    failed_devices = []
    
    for ip in open_rtsp_ips:
        info = verify_camera(ip)
        if info["status"] == "Connectable":
            print(f"    >>> THÀNH CÔNG: Camera tại {ip}")
            valid_cameras.append(info)
        else:
            print(f"    >>> THẤT BẠI: {ip} - {info['detail']}")
            failed_devices.append(info)
            
    # 4. Xuất báo cáo
    print(f"\n[4] Đang lưu kết quả vào file '{OUTPUT_FILE}'...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== DANH SÁCH CAMERA ĐÃ KẾT NỐI (IMOU) ===\n")
        f.write(f"Thời gian quét: {time.ctime()}\n")
        f.write(f"Mật khẩu chung đang dùng: {SAFETY_CODE}\n\n")
        
        for cam in valid_cameras:
            f.write(f"[CAMERA] IP: {cam['ip']}\n")
            f.write(f"   Trạng thái: Đã kết nối thành công\n")
            f.write(f"   URL RTSP (Phụ - Nhẹ):   {cam['url_sub']}\n")
            f.write(f"   URL RTSP (Chính - Nét): {cam['url_main']}\n")
            f.write("-" * 50 + "\n")
            
        f.write("\n=== CÁC THIẾT BỊ KHÁC (CÓ CỔNG 554 NHƯNG KHÔNG VÀO ĐƯỢC) ===\n")
        for dev in failed_devices:
            f.write(f"[DEVICE] IP: {dev['ip']}\n")
            f.write(f"   Lỗi: {dev['detail']}\n")
            f.write("-" * 50 + "\n")
            
    print("\n" + "="*50)
    print(f"HOÀN TẤT! Đã tìm thấy {len(valid_cameras)} camera hoạt động.")
    print(f"Mở file này để lấy link: {os.path.abspath(OUTPUT_FILE)}")
    print("="*50)

if __name__ == "__main__":
    main()
