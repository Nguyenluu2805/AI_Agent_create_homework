# HỆ THỐNG BÀI TẬP VỀ NHÀ CHUẨN CHỈNH: MẢNG VÀ LIST (PYTHON)

### Mục tiêu buổi học:
Sinh viên sẽ biết cách sử dụng các hàm cơ bản để thao tác với mảng trong Python.

---

## I. VẬN DỤNG CƠ BẢN

### 1. Bài 1: Thêm phần tử vào list

▪ **Bối cảnh & vai trò:**
Bạn là nhà phát triển cần thêm thông tin khách hàng vào danh sách.

▪ **Vấn đề hiện tại:**
Bạn cần thêm thông tin khách hàng mới vào danh sách.

▪ **Hiện trường giả (Source code lỗi):**
```python
customer_list = ['John Doe', 'Jane Smith']
customer_list.append('Peter Jones')
print(customer_list)
```

▪ **Yêu cầu nộp bài:**
1. Đề xuất và giải thích cách thêm tên 'Alice Brown' vào cuối danh sách khách hàng.

---

### 2. Bài 2: Xóa phần tử khỏi list

▪ **Bối cảnh & vai trò:**
Bạn là quản lý cần xóa thông tin khách hàng không còn sử dụng dịch vụ.

▪ **Vấn đề hiện tại:**
Bạn cần xóa thông tin khách hàng 'John Doe' khỏi danh sách.

▪ **Hiện trường giả (Source code lỗi):**
```python
customer_list = ['John Doe', 'Jane Smith', 'Peter Jones', 'Alice Brown']
print(customer_list)
customer_list.remove('Peter Jones')
print(customer_list)
```

▪ **Yêu cầu nộp bài:**
1. Đề xuất và giải thích cách sử dụng hàm remove() để xóa phần tử từ list.

---

## II. VẬN DỤNG CHUYÊN SÂU

### 1. Bài 3: Chèn phần tử vào list

▪ **Bối cảnh & vai trò:**
Bạn là nhà thiết kế cần chèn một thành viên mới vào giữa danh sách của đội ngũ phát triển.

▪ **Quy tắc nghiệp vụ:**
Chèn thành viên 'Bob' vào vị trí thứ 2 trong danh sách.

▪ **Bẫy dữ liệu:**
Không có dữ liệu bất thường.

▪ **Yêu cầu nộp bài:**
1. Báo cáo phân tích và thiết kế giải pháp (Phân tích bài toán I/O, đề xuất ý tưởng).
2. Triển khai code hoàn chỉnh chặn bẫy.

---

## III. PHÂN TÍCH

### 1. Bài 4: Sắp xếp mảng

▪ **Bối cảnh & vai trò:**
Bạn là chuyên viên marketing cần sắp xếp danh sách khách hàng theo thứ tự điểm số giảm dần.

▪ **Quy tắc nghiệp vụ:**
Danh sách khách hàng được đánh giá dựa trên điểm số.

▪ **Bẫy dữ liệu:**
Có thể có trường hợp không có điểm số hoặc điểm số âm.

▪ **Yêu cầu nộp bài:**
1. Phân tích & Đề xuất (Xác định I/O, đề xuất tối thiểu 2 giải pháp khác nhau). 2. So sánh & Lựa chọn (Bảng so sánh ưu nhược trade-off, chốt chọn 1 giải pháp). 3. Thiết kế & Triển khai (Mã giả các bước, viết code hoàn chỉnh chặn bẫy).

---

## IV. SÁNG TẠO

### 1. Bài 5: Tìm kiếm phần tử trong list

▪ **Bối cảnh & vai trò:**
Bạn là nhà phát triển cần thiết kế một ứng dụng tìm kiếm thông tin khách hàng dựa trên tên.

▪ **Ràng buộc kỹ thuật:**
Sử dụng list comprehension để tối ưu hóa quá trình tìm kiếm.

▪ **Yêu cầu nộp bài:**
1. Thiết kế kiến trúc (Xác định các module và luồng data flow).
2. Sản phẩm hoàn chỉnh (Source code xử lý mượt mọi ngoại lệ/bẫy dữ liệu, giao tiếp thân thiện).

---

