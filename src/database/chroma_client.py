import os
# pyrefly: ignore [missing-import]
import chromadb
from src import config

class RikkeiChromaClient:
    def __init__(self):
        # Kết nối tới cơ sở dữ liệu Vector (ChromaDB)
        self.client = chromadb.PersistentClient(path=config.DB_PATH)
        
        # Khởi tạo/Lấy hai tủ hồ sơ lưu trữ riêng biệt
        self.col_standards = self.client.get_or_create_collection(name="rikkei_standards")
        self.col_syllabuses = self.client.get_or_create_collection(name="rikkei_syllabuses")

    @staticmethod
    def chunk_text(text, chunk_size=500, chunk_overlap=100):
        """
        Băm nhỏ tài liệu văn bản thành các đoạn nhỏ để tránh vượt quá ngữ cảnh của LLM.
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end].strip())
            start += chunk_size - chunk_overlap
        return chunks

    def ingest_folder_with_metadata(self, folder_path, collection_target):
        """
        Quét các thư mục con (môn học), đọc tài liệu, băm nhỏ và gán metadata 'subject' khi lưu vào Vector DB.
        """
        if not os.path.exists(folder_path):
            print(f"[Loi] Thu muc khong ton tai: {folder_path}")
            return
            
        category_name = os.path.basename(folder_path)
        
        # Duyệt qua các thư mục con môn học (Python, Java, Web)
        for subject_dir in os.listdir(folder_path):
            subject_path = os.path.join(folder_path, subject_dir)
            if not os.path.isdir(subject_path):
                continue
                
            subject_name = subject_dir.lower()  # python, java, web
            files = [f for f in os.listdir(subject_path) if f.endswith(('.txt', '.md'))]
            
            for file_name in files:
                file_path = os.path.join(subject_path, file_name)
                print(f"  [{subject_dir}] Dang doc va so hoa file: {file_name}")
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                chunks = self.chunk_text(content)
                docs, metadatas, ids = [], [], []
                
                for idx, chunk in enumerate(chunks):
                    # Tạo ID kết hợp môn học tránh trùng lặp
                    chunk_id = f"{subject_name}_{file_name}_chunk_{idx}"
                    docs.append(chunk)
                    metadatas.append({
                        "source": file_name,
                        "category": category_name,
                        "subject": subject_name
                    })
                    ids.append(chunk_id)
                    
                # Nạp dữ liệu kèm Metadata vào tủ hồ sơ
                collection_target.add(documents=docs, metadatas=metadatas, ids=ids)
                print(f"    [{subject_dir}] Da nap thanh cong {len(chunks)} doan vao tu '{collection_target.name}'.")

    def run_sync(self):
        """
        Chạy quy trình đồng bộ hóa tự động tài liệu đầu vào kèm Metadata môn học
        """
        print("[ChromaDB] Bat dau dong bo tai lieu tri thuc kem bo loc Metadata mon hoc...")
        self.ingest_folder_with_metadata(config.DIR_STANDARDS, self.col_standards)
        self.ingest_folder_with_metadata(config.DIR_SYLLABUSES, self.col_syllabuses)
        print(f"   Tu Tieu chuan hien co: {self.col_standards.count()} ban ghi.")
        print(f"   Tu Giao an hien co: {self.col_syllabuses.count()} ban ghi.")
        print("   Dong bo bo nho dai han (Vector DB) hoan tat!")
