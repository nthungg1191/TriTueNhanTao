# 📋 Hệ thống tính công làm việc - Triển khai V2

## ✅ Thực hiện xong

Đã triển khai thành công hệ thống tính công làm việc với các quy tắc tính công động dựa trên 4 thời điểm check-in/check-out.

### 🆕 Quy tắc tính công (Phiên bản 2):

**Điều kiện cơ bản**: Kiểm tra tất cả 4 thời điểm punch (08:00, 12:00, 13:00, 17:00)

| Tình huống | Trừ công | Kết quả |
|-----------|---------|--------|
| **Tất cả 4 điểm đúng giờ** | Không | **8 công** |
| **Bất kỳ điểm muộn 0.1s - 30 phút** | **-0.5 công** | 7.5 công |
| **Bất kỳ điểm muộn 30 phút - 1 tiếng** | **-1.0 công** | 7.0 công |
| **Bất kỳ điểm muộn > 1 tiếng** | **-1.5 công** | 6.5 công |

**Lưu ý**: 
- Check-out/check-in_2 muộn = rời khỏi sớm (vào lại muộn)
- Các trừ công **cộng dồn**: Nếu nhiều điểm có vấn đề, tính tổng

---

## 📝 Các thay đổi

### File chính: `app/models/attendance.py`

#### 1. Phương thức `calculate_working_hours()` - Được cập nhật

```python
def calculate_working_hours(self):
    """Calculate total working hours with late/early deductions"""
    # Tính giờ thực tế làm việc từ punch times
    # Sau đó áp dụng logic trừ công từ _apply_time_deductions
```

#### 2. Phương thức `_apply_time_deductions()` - Mới thêm

**Kiểm tra từng thời điểm punch**:
- Check-in (08:00) - Muộn? Trừ công
- Check-out (12:00) - Sớm? Trừ công  
- Check-in_2 (13:00) - Muộn? Trừ công
- Check-out_2 (17:00) - Sớm? Trừ công

```python
def _apply_time_deductions(self, base_hours=8.0):
    """
    Áp dụng trừ công dựa trên thời gian punch
    
    - Tất cả 4 punch đúng → 8 giờ
    - Punch muộn → trừ công tương ứng
    - Punch sớm → trừ công tương ứng
    """
    # Kiểm tra schedule chuẩn (8:00-17:00)
    # Tính độ lệch từng punch
    # Áp dụng trừ công từng cái
    # Trả về giờ cuối cùng
```

#### 3. Phương thức `_calculate_deduction()` - Mới thêm

```python
def _calculate_deduction(self, time_diff_seconds):
    """Tính trừ công dựa trên độ chênh lệch thời gian"""
    # 0.1s - 30 phút → -0.5 công
    # 30 phút - 1 giờ → -1.0 công
    # > 1 giờ → -1.5 công
```

---

## 🧪 Kiểm thử hoàn toàn

Đã tạo test file: `test_late_penalty.py`

Kết quả kiểm thử (✅ Tất cả đều pass):

```
✓ All on-time test: 8.0h
✓ Check-in 5min late: 7.5h (trừ 0.5)
✓ Check-out 45min early: 7.0h (trừ 1.0)
✓ Afternoon check-in 35min late: 7.0h (trừ 1.0)
✓ Multiple deductions: 7.0h (trừ 0.5 + 0.5)
✓ Afternoon checkout 50min early: 7.0h (trừ 1.0)
```

---

## 📊 Ví dụ cụ thể từ ảnh

### Ví dụ từ attachment: Phạm Thị Thảo

```
Check-in: 08:00:00 ✓ (đúng giờ)
Check-out: 12:01:00 ⚠️ (muộn 1 phút trong break)
Check-in_2: 13:00:00 ✓ (đúng giờ) 
Check-out_2: 17:00:00 ✓ (đúng giờ)

→ Kết quả: 8.0 - 0.5 = 7.5 công (muộn 1 phút = trừ 0.5)
```

**Nhưng hiện tại hiển thị 8.02h vì chưa áp dụng logic mới**

---

## 🔧 Cách hoạt động

### Quy trình xử lý:

1. Khi nhân viên **check-out**, hệ thống tự động:
   - Tính giờ làm thực tế từ 4 punch times
   - Lấy lịch làm việc chuẩn (8:00-17:00)
   - Kiểm tra mỗi punch:
     - Nếu check-in/in_2 muộn: Tính độ muộn
     - Nếu check-out/out_2 sớm: Tính độ sớm
   - Áp dụng quy tắc trừ công
   - Tính tổng công cuối cùng
   - Lưu vào database

2. Hệ thống chỉ áp dụng cho:
   - ✅ Lịch làm việc chuẩn (8:00 sáng - 5:00 chiều)
   - ✅ Nhân viên có đủ 4 punch
   - ❌ Sẽ bỏ qua nếu lịch làm việc khác

---

## 🔑 Các trường hợp

### 1️⃣ Đúng giờ (8 công)
```
08:00 | 12:00 | 13:00 | 17:00 → 8.0h
```

### 2️⃣ Muộn sáng (trừ 0.5)
```
08:15 | 12:00 | 13:00 | 17:00 → 7.5h
```

### 3️⃣ Rời sớm đồi (trừ 1.0)
```
08:00 | 11:30 | 13:00 | 17:00 → 7.0h
```

### 4️⃣ Muộn cả sáng + chiều (trừ 0.5 + 0.5)
```
08:10 | 12:00 | 13:20 | 17:00 → 7.0h
```

### 5️⃣ Muộn chiều > 30 phút (trừ 1.0)
```
08:00 | 12:00 | 13:45 | 17:00 → 7.0h
```

---

## 📌 Ghi chú quan trọng

✅ Hệ thống **tự động** áp dụng quy tắc khi:
- Nhân viên hoàn thành cả 4 punch times
- Nhân viên được gán lịch làm việc 8:00-17:00

⚠️ Các trường hợp đặc biệt:
- Nếu thiếu bất kỳ punch nào → không tính công (status = missing_*)
- Nếu lịch làm việc khác → không áp dụng quy tắc này
- Nếu không có lịch làm việc → trả về giờ thực tế

---

## 🚀 Tiếp theo

Để sử dụng trong ứng dụng:

1. Hệ thống sẽ **tự động** tính công khi nhân viên check-out lần cuối
2. Giá trị `working_hours` được lưu trong database
3. Báo cáo công sẽ hiển thị công đã tính
4. Có thể xem chi tiết tại trang Dashboard admin

---

*Ngày cập nhật: 2026-05-15 (v2)*

