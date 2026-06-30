# 📘 HỆ THỐNG BÀI TẬP VỀ NHÀ CHUẨN CHỈNH: XỬ LÝ CHUỖI TRONG PYTHON (PYTHON)

### 🎯 Mục tiêu buổi học:
Sau bài học này, sinh viên sẽ biết cách sử dụng các hàm và phương thức cơ bản để xử lý chuỗi trong Python.

---

## I. VẬN DỤNG CƠ BẢN

### 1. Bài 1: Sửa lỗi/Vá code: Xoá khoảng trắng thừa

▪ **Bối cảnh & vai trò:**
Một cửa hàng online cần xóa khoảng trắng thừa ở đầu và cuối của tên sản phẩm trước khi lưu vào database.

▪ **Vấn đề hiện tại:**
Khoảng trắng thừa ở đầu và cuối tên sản phẩm làm ảnh hưởng đến việc sắp xếp và tìm kiếm.

▪ **Hiện trường giả (Source code lỗi):**
```python
 product_name = "   Laptop Gaming   "
 print(product_name)
```

▪ **Yêu cầu nộp bài:**
1. Xác định đoạn code sai hoặc thiếu điều kiện bằng dữ liệu test case cụ thể. 2. Source code đã được sửa chuẩn, sử dụng hàm `strip()` để loại bỏ khoảng trắng thừa ở đầu và cuối chuỗi.

---

### 2. Bài 2: Sửa lỗi/Vá code: Chia chuỗi thành danh sách

▪ **Bối cảnh & vai trò:**
Một website cần phân chia đường dẫn URL thành các phần riêng biệt để xử lý.

▪ **Vấn đề hiện tại:**
Đường dẫn URL chưa được chia thành các phần riêng biệt.

▪ **Hiện trường giả (Source code lỗi):**
```python
 url = "https://www.example.com/products/laptop/gaming"
 print(url)
```

▪ **Yêu cầu nộp bài:**
1. Xác định đoạn code sai hoặc thiếu điều kiện bằng dữ liệu test case cụ thể. 2. Source code đã được sửa chuẩn, sử dụng hàm `split()` để chia chuỗi URL thành danh sách.

---

## II. VẬN DỤNG CHUYÊN SÂU

### 1. Bài 3: Vận dụng chuyên sâu: Tạo mã băm cho chuỗi

▪ **Bối cảnh & vai trò:**
Một hệ thống quản lý người dùng cần tạo mã băm cho mật khẩu của người dùng để bảo mật.

▪ **Quy tắc nghiệp vụ:**
Tạo mã băm SHA-256 cho chuỗi mật khẩu.

▪ **Bẫy dữ liệu:**
Kiểm tra mã băm cho các trường hợp khác nhau (mật khẩu dài, ngắn, có ký tự đặc biệt).

▪ **Yêu cầu nộp bài:**
1.  Báo cáo phân tích và thiết kế giải pháp (Phân tích bài toán I/O, đề xuất ý tưởng, thiết kế các bước mã giả). 2. Triển khai code hoàn chỉnh tính toán mã băm SHA-256 cho chuỗi input.

---

## III. PHÂN TÍCH

### 1. Bài 4: Phân tích: Tìm kiếm chuỗi con trong một chuỗi lớn

▪ **Bối cảnh & vai trò:**
Một công ty cần tìm kiếm thông tin cụ thể trong các hồ sơ văn bản.

▪ **Quy tắc nghiệp vụ:**
Tìm kiếm chuỗi con có độ dài nhất định trong một chuỗi lớn.

▪ **Bẫy dữ liệu:**
Chuỗi con có thể xuất hiện nhiều lần trong chuỗi chính.
 - Các ký tự đặc biệt và chữ hoa/thường.

▪ **Yêu cầu nộp bài:**
1. Phân tích & Đề xuất (Xác định I/O, đề xuất tối thiểu 2 giải pháp khác nhau: sử dụng hàm `find()` hoặc `index()`). 2. So sánh & Lựa chọn (Bảng so sánh ưu nhược trade-off giữa hai giải pháp). 3. Thiết kế & Triển khai (Mã giả các bước, viết code hoàn chỉnh tìm kiếm chuỗi con trong chuỗi lớn).

---

## IV. SÁNG TẠO

### 1. Bài 5: Sáng tạo: Tạo một công cụ thay thế cho hàm replace()

▪ **Bối cảnh & vai trò:**
Hãy sáng tạo một function python có thể thay thế cho hàm `replace()` nhưng hoạt động hiệu quả hơn với các chuỗi dài và phức tạp.

▪ **Ràng buộc kỹ thuật:**
Function phải nhận vào chuỗi gốc, chuỗi cần thay thế, chuỗi thay thế.
 - Hàm `replace()` của Python có thể gặp vấn đề hiệu suất khi xử lý chuỗi dài. Hãy tìm cách cải thiện hiệu quả hơn.

▪ **Yêu cầu nộp bài:**
1. Thiết kế kiến trúc (Xác định các module và luồng data flow).
 2. Sản phẩm hoàn chỉnh (Source code xử lý mượt mọi ngoại lệ/bẫy dữ liệu, gõ phím liên tục để kiểm tra hiệu suất so với hàm `replace()`).

---

