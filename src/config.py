import os

# --- CẤU HÌNH ĐƯỜNG DẪN HỆ THỐNG ---
# Đường dẫn gốc của dự án (D:/AI_Agent)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Thư mục dữ liệu
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "chroma_db")

# Đầu vào tri thức
INPUT_DIR = os.path.join(DATA_DIR, "inputs")
DIR_STANDARDS = os.path.join(INPUT_DIR, "Tieu_Chuan")
DIR_SYLLABUSES = os.path.join(INPUT_DIR, "Giao_An")

# Đầu ra kết quả
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")
OUTPUT_JSON_DIR = os.path.join(OUTPUT_DIR, "raw_json")
OUTPUT_MD_DIR = os.path.join(OUTPUT_DIR, "markdown")

# --- CẤU HÌNH AI MODEL ---
MODEL_NAME = "gemma2"

# Tự động khởi tạo toàn bộ cấu trúc thư mục vật lý nếu chưa có
SUBJECTS = ["Python", "Java", "Web"]
REQUIRED_FOLDERS = [
    DB_PATH,
    OUTPUT_JSON_DIR,
    OUTPUT_MD_DIR
]

for folder in REQUIRED_FOLDERS:
    os.makedirs(folder, exist_ok=True)

# Khởi tạo các thư mục môn học con cho tiêu chuẩn và giáo án lý thuyết
for subject in SUBJECTS:
    os.makedirs(os.path.join(DIR_STANDARDS, subject), exist_ok=True)
    os.makedirs(os.path.join(DIR_SYLLABUSES, subject), exist_ok=True)
