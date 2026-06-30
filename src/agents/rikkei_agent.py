import json
import os
# pyrefly: ignore [missing-import]
import ollama
# pyrefly: ignore [missing-import]
import chromadb
from src import config
from src.agents.base import BaseAgent
from src.database.chroma_client import RikkeiChromaClient
from src.services.rikkei_api import RikkeiPortalAPI
from src.utils.publisher import publish_json_to_markdown

class RikkeiAgent(BaseAgent):
    """
    Agent chuyên môn hóa cho Rikkei Portal:
    Sử dụng cơ chế ReAct (Reasoning and Acting) tự trị bằng cấu trúc JSON
    tích hợp bộ lọc Metadata ChromaDB và vòng lặp tự kiểm duyệt (Reflection Loop) kết hợp mã nguồn cứng và LLM.
    """
    def __init__(self, chroma_client: RikkeiChromaClient, model_name=config.MODEL_NAME):
        super().__init__(model_name)
        self.chroma_client = chroma_client
        self.api_service = RikkeiPortalAPI()
        
        # Hướng dẫn quy trình ReAct dạng JSON kèm theo bộ lọc môn học
        self.system_instruction = (
            "Bạn là một Trợ lý AI Agent tự trị (Autonomous Agent) chuyên trách đào tạo tại Rikkei Academy.\n"
            "Nhiệm vụ của bạn là hỗ trợ biên soạn học liệu và sản xuất bộ bài tập về nhà dựa trên bối cảnh tri thức.\n\n"
            "QUY ĐỊNH ĐỊNH DẠNG PHẢN HỒI:\n"
            "Mỗi lượt phản hồi, bạn BẮT BUỘC phải trả về định dạng JSON thuần túy theo cấu trúc sau:\n"
            "{\n"
            '  "thought": "Mô tả suy nghĩ hiện tại của bạn và bước tiếp theo sẽ thực hiện",\n'
            '  "action": "tên_công_cụ_muốn_gọi",\n'
            '  "arguments": { ... các tham số truyền cho công cụ tương ứng ... }\n'
            "}\n\n"
            "DANH SÁCH CÁC CÔNG CỤ (TOOLS) BẠN CÓ THỂ GỌI:\n"
            "1. `retrieve_knowledge(query: str, category: str, subject: str)`:\n"
            "   - Tìm kiếm tri thức trong Vector DB kèm bộ lọc môn học.\n"
            "   - Các tham số:\n"
            "     * `query` (từ khóa tìm kiếm)\n"
            "     * `category` ('syllabuses' cho lý thuyết giáo án hoặc 'standards' cho quy chuẩn học liệu)\n"
            "     * `subject` ('python', 'java' hoặc 'web' để lọc chính xác môn học cần tìm kiếm)\n"
            "2. `publish_homework_markdown(homework_json: dict)`:\n"
            "   - Đóng gói và xuất bản file Markdown từ cấu trúc bài tập JSON.\n"
            "   - Bài tập của bạn sẽ được KIỂM DUYỆT nghiêm ngặt bởi Trưởng bộ môn dựa trên nội dung tệp quy chuẩn thực tế.\n"
            "   - Tham số: `homework_json` là JSON có cấu trúc phẳng dễ xuất như sau:\n"
            "     {\n"
            '       "subject": "môn học chữ thường (\'python\', \'java\' hoặc \'web\')",\n'
            '       "chu_de": "tên chủ đề chính của buổi học",\n'
            '       "muc_tieu": "mục tiêu buổi học (học viên sẽ làm được gì)",\n'
            '       "danh_sach_bai_tap": [\n'
            "         {\n"
            '           "ten_bai": "tên bài tập ngắn gọn",\n'
            '           "muc_do": "mức độ phân hóa (\'Vận dụng cơ bản (1.5đ)\', \'Vận dụng chuyên sâu (2đ)\', \'Phân tích (2đ)\', \'Sáng tạo (3đ)\')",\n'
            '           "boi_canh_nghiep_vu": "mô tả bối cảnh thực tế/dự án/vai diễn của bài tập",\n'
            '           "code_loi_chua_sua": "đoạn code Python thô chạy được nhưng sai logic/thiếu điều kiện để sinh viên dò lỗi và vá (BẮT BUỘC có cho bài Vận dụng cơ bản, để trống cho các bài khác)",\n'
            '           "yeu_cau_chi_tiet": "nội dung chi tiết yêu cầu đầu ra (phải tuân thủ cấu trúc mục con quy định bên dưới)",\n'
            '           "tieu_chi_cham": ["danh sách gạch đầu dòng barem chấm điểm chi tiết (ví dụ: \'- 0.5đ: ...\')"]\n'
            "         }\n"
            "       ]\n"
            "     }\n"
            "3. `fetch_rikkei_systems()`:\n"
            "   - [TẠM THỜI KHÔNG DÙNG] Lấy danh sách các Hệ đào tạo hiện có trên Rikkei Portal.\n"
            "4. `sync_homework_to_rikkei(homework_json: dict)`:\n"
            "   - [TẠM THỜI KHÔNG DÙNG] Đồng bộ dữ liệu bài tập lên Rikkei Portal.\n"
            "5. `final_answer(response: str)`:\n"
            "   - Trả lời trực tiếp cho người dùng sau khi đã hoàn tất toàn bộ các bước hành động cần thiết.\n"
            "   - Tham số: `response` (nội dung phản hồi hoàn thành nhiệm vụ gửi người dùng).\n\n"
            "LUỒNG VẬN HÀNH BẮT BUỘC SOẠN BÀI TẬP:\n"
            "Bạn phải thực hiện tuần tự qua các bước sau mà không được bỏ sót:\n"
            "- Bước 1 (Truy vấn quy chuẩn): Bạn BẮT BUỘC gọi `retrieve_knowledge` với category='standards' và subject tương ứng môn học để đọc các quy định xây dựng bài tập.\n"
            "- Bước 2 (Truy vấn giáo án): Gọi `retrieve_knowledge` với category='syllabuses' để tìm giáo trình lý thuyết môn học. Nếu giáo trình lý thuyết không tồn tại, tự lập luận nội dung chuyên môn dựa trên kiến thức nền nhưng sản phẩm bài tập vẫn phải đạt chuẩn 100% theo tiêu chuẩn ở bước 1.\n"
            "- Bước 3 (Soạn bài tập & Đóng gói): Thiết kế bộ bài tập gồm đúng 5 bài và gọi công cụ `publish_homework_markdown` với cấu trúc `homework_json` đơn giản trên.\n"
            "  * Quy định bắt buộc khi thiết kế nội dung bài tập:\n"
            "    + Phân bổ: Gồm đúng 5 bài: Bài 1 & 2: Vận dụng cơ bản (1.5đ mỗi bài); Bài 3: Vận dụng chuyên sâu (2đ); Bài 4: Phân tích (2đ); Bài 5: Sáng tạo (3đ). Tổng điểm = 10.\n"
            "    + Đóng HOW - Mở WHAT & WHY: Đề bài cấm chỉ định thuật toán hoặc các bước code cụ thể trong yêu cầu đề bài. Hãy để sinh viên tự do lựa chọn giải thuật. Ví dụ: cấm dùng cụm từ 'sử dụng hàm split', 'sử dụng hàm append', 'dùng vòng lặp for' trong đề bài.\n"
            "    + Domain đồng nhất: Cả 5 bài cùng thuộc một bối cảnh nghiệp vụ thực tế duy nhất (ví dụ: Hệ thống bán hàng E-commerce, Quản lý kho hàng...).\n"
            "    + Bẫy dữ liệu: Cài cắm ít nhất 1-2 kịch bản dữ liệu dị biệt (số âm, chuỗi trống, kiểu sai) và yêu cầu sinh viên viết code chặn lỗi để tránh crash.\n"
            "    + Cấu trúc trình bày trong trường `yeu_cau_chi_tiet` của từng bài BẮT BUỘC tuân thủ đầu mục sau:\n"
            "      * Bài 1 & 2 (Vận dụng cơ bản - Sửa lỗi/Vá code): Trường `code_loi_chua_sua` phải chứa mã nguồn lỗi logic/thiếu ràng buộc. Trường `yeu_cau_chi_tiet` định dạng:\n"
            "        `[Vấn đề hiện tại]: Khách hàng phàn nàn... \n\n[Yêu cầu đầu ra]: 1. Chỉ ra đoạn code sai hoặc thiếu điều kiện bằng dữ liệu test case cụ thể. 2. Source code đã được sửa chuẩn.`\n"
            "      * Bài 3 (Vận dụng chuyên sâu - Tự code): Trường `yeu_cau_chi_tiet` định dạng:\n"
            "        `[Yêu cầu nghiệp vụ]: ... \n\n[Ràng buộc & Bẫy dữ liệu]: Đặt ra 1-2 kịch bản dữ liệu dị biệt... \n\n[Yêu cầu đầu ra]: 1. Báo cáo phân tích và thiết kế giải pháp (Phân tích bài toán I/O, đề xuất ý tưởng, thiết kế các bước mã giả). 2. Triển khai code hoàn chỉnh chặn bẫy.`\n"
            "      * Bài 4 (Phân tích - Đa giải pháp): Trường `yeu_cau_chi_tiet` định dạng:\n"
            "        `[Quy tắc nghiệp vụ]: ... \n\n[Ràng buộc & Bẫy dữ liệu]: ... \n\n[Yêu cầu đầu ra]: 1. Phân tích & Đề xuất (Xác định I/O, đề xuất tối thiểu 2 giải pháp khác nhau). 2. So sánh & Lựa chọn (Bảng so sánh ưu nhược trade-off, chốt chọn 1 giải pháp). 3. Thiết kế & Triển khai (Mã giả các bước, viết code hoàn chỉnh chặn bẫy).`\n"
            "      * Bài 5 (Sáng tạo - Bài toán mở): Trường `yeu_cau_chi_tiet` định dạng:\n"
            "        `[Ràng buộc kỹ thuật]: ... \n\n[Yêu cầu đầu ra]: 1. Thiết kế kiến trúc (Xác định các module và luồng data flow). 2. Sản phẩm hoàn chỉnh (Source code xử lý mượt mọi ngoại lệ/bẫy dữ liệu, giao tiếp thân thiện).`\n"
            "- Bước 4 (Hoàn tất): Nếu công cụ trả về APPROVED, gọi công cụ `final_answer` để thông báo đường dẫn file Markdown cho người dùng và kết thúc nhiệm vụ. Nếu trả về REJECTED, tự sửa đổi bài tập theo feedback lỗi và gọi lại công cụ xuất bản. Chú ý: thoát các dấu nháy kép bên trong chuỗi bằng \\\" để tránh lỗi cú pháp parse JSON."
        )

        # Bản đồ ánh xạ gọi hàm Python
        self.tools_map = {
            'retrieve_knowledge': self._tool_retrieve_knowledge,
            'publish_homework_markdown': self._tool_publish_homework_markdown,
            'fetch_rikkei_systems': self._tool_fetch_rikkei_systems,
            'sync_homework_to_rikkei': self._tool_sync_homework_to_rikkei
        }

    # --- IMPLEMENTATION CỦA CÁC CÔNG CỤ CỤ THỂ ---

    def _tool_retrieve_knowledge(self, query, category, subject=None):
        print(f"   [ChromaDB Tool] Dang luc tim boi canh '{query}' tai tu '{category}' (Loc mon hoc: {subject})...")
        
        # Xây dựng bộ lọc Metadata where
        where_filter = {}
        if subject:
            where_filter["subject"] = subject.lower()

        if category == 'standards':
            res = self.chroma_client.col_standards.query(
                query_texts=[query], 
                n_results=1,
                where=where_filter if where_filter else None
            )
        else:
            res = self.chroma_client.col_syllabuses.query(
                query_texts=[query], 
                n_results=1,
                where=where_filter if where_filter else None
            )

        if res and res.get('documents') and len(res['documents']) > 0 and len(res['documents'][0]) > 0:
            context = res['documents'][0][0]
            print(f"   [ChromaDB Tool] Tim thay tri thuc lien quan ({len(context)} ky tu).")
            return context
        print("   [ChromaDB Tool] Khong tim thay du lieu lien quan phu hop.")
        return f"Không có tri thức cụ thể nào về danh mục '{category}' môn '{subject}' trong Vector DB."

    def _validate_homework_structure(self, homework_json):
        """
        Kiểm duyệt cứng bằng code Python để đảm bảo cấu trúc bài tập đạt chuẩn Rikkei Academy 100%.
        """
        danh_sach = homework_json.get("danh_sach_bai_tap", [])
        if len(danh_sach) != 5:
            return f"Số lượng bài tập không đúng. Tiêu chuẩn yêu cầu đúng 5 bài tập, hiện tại có {len(danh_sach)} bài."

        levels_expected = [
            "vận dụng cơ bản",
            "vận dụng cơ bản",
            "vận dụng chuyên sâu",
            "phân tích",
            "sáng tạo"
        ]
        
        # 1. Kiểm tra cấp độ
        for idx, bt in enumerate(danh_sach):
            muc_do = bt.get("muc_do", "").lower()
            expected = levels_expected[idx]
            if expected not in muc_do:
                return f"Bài {idx+1} sai mức độ phân hóa. Kỳ vọng chứa '{expected}', thực tế là '{muc_do}'."

        # 2. Kiểm tra bài 1 & 2 bắt buộc có code lỗi mẫu
        for idx in [0, 1]:
            bt = danh_sach[idx]
            code_loi = (bt.get("code_loi_chua_sua") or "").strip()
            if not code_loi:
                return f"Bài {idx+1} (Vận dụng cơ bản) bắt buộc phải cung cấp mã nguồn lỗi mẫu trong trường 'code_loi_chua_sua' để sinh viên vá lỗi. Hãy sinh một đoạn code Python chạy được nhưng có lỗi logic hoặc thiếu điều kiện chặn lỗi."

        # 3. Kiểm tra các tiêu đề bắt buộc trong yeu_cau_chi_tiet
        for idx, bt in enumerate(danh_sach, 1):
            yeu_cau = bt.get("yeu_cau_chi_tiet", "")
            yeu_cau_lower = yeu_cau.lower()
            if idx in (1, 2):
                if "vấn đề hiện tại" not in yeu_cau_lower or "yêu cầu đầu ra" not in yeu_cau_lower:
                    return (
                        f"Bài {idx} (Vận dụng cơ bản) thiếu thẻ cấu trúc bắt buộc 'Vấn đề hiện tại' hoặc 'Yêu cầu đầu ra' trong yeu_cau_chi_tiet. "
                        "Hãy thiết lập đúng dạng:\n"
                        "[Vấn đề hiện tại]: Khách hàng phàn nàn là...\n\n"
                        "[Yêu cầu đầu ra]: 1. Chỉ ra đoạn code sai bằng dữ liệu test case. 2. Source code đã sửa."
                    )
            elif idx == 3:
                has_rules = "yêu cầu nghiệp vụ" in yeu_cau_lower or "quy tắc nghiệp vụ" in yeu_cau_lower or "quy tắc điểm danh" in yeu_cau_lower
                has_traps = "bẫy dữ liệu" in yeu_cau_lower or "ràng buộc & bẫy dữ liệu" in yeu_cau_lower
                has_output = "yêu cầu đầu ra" in yeu_cau_lower or "yêu cầu nộp bài" in yeu_cau_lower
                if not has_rules or not has_traps or not has_output:
                    return (
                        f"Bài {idx} (Vận dụng chuyên sâu) thiếu thẻ cấu trúc bắt buộc 'Yêu cầu nghiệp vụ', 'Ràng buộc & Bẫy dữ liệu' hoặc 'Yêu cầu đầu ra' trong yeu_cau_chi_tiet. "
                        "Hãy thiết lập đúng dạng:\n"
                        "[Yêu cầu nghiệp vụ]: Quy tắc hệ thống...\n\n"
                        "[Ràng buộc & Bẫy dữ liệu]: Kịch bản dữ liệu dị biệt...\n\n"
                        "[Yêu cầu đầu ra]: 1. Báo cáo phân tích và thiết kế giải pháp (Phân tích bài toán I/O, ý tưởng, lưu đồ/mã giả). 2. Triển khai code và chống lỗi."
                    )
                if "phân tích" not in yeu_cau_lower and "thiết kế" not in yeu_cau_lower:
                    return f"Bài 3 (Vận dụng chuyên sâu) thiếu yêu cầu học viên nộp 'Báo cáo phân tích' hoặc 'thiết kế giải pháp' trong phần 'Yêu cầu đầu ra'."
            elif idx == 4:
                has_rules = "quy tắc nghiệp vụ" in yeu_cau_lower or "yêu cầu nghiệp vụ" in yeu_cau_lower
                has_traps = "bẫy dữ liệu" in yeu_cau_lower or "ràng buộc & bẫy dữ liệu" in yeu_cau_lower
                has_output = "yêu cầu đầu ra" in yeu_cau_lower or "yêu cầu nộp bài" in yeu_cau_lower
                if not has_rules or not has_traps or not has_output:
                    return (
                        f"Bài 4 (Phân tích) thiếu thẻ cấu trúc bắt buộc 'Quy tắc nghiệp vụ', 'Ràng buộc & Bẫy dữ liệu' hoặc 'Yêu cầu đầu ra' trong yeu_cau_chi_tiet. "
                        "Hãy thiết lập đúng dạng:\n"
                        "[Quy tắc nghiệp vụ]: Điều kiện tính toán...\n\n"
                        "[Ràng buộc & Bẫy dữ liệu]: Kịch bản ngoại lệ...\n\n"
                        "[Yêu cầu đầu ra]: 1. Phân tích & Đề xuất (Đa giải pháp, I/O). 2. So sánh & Lựa chọn (Bảng so sánh ưu nhược trade-off, chốt chọn 1). 3. Thiết kế & Triển khai."
                    )
                if "giải pháp" not in yeu_cau_lower or "so sánh" not in yeu_cau_lower:
                    return f"Bài 4 (Phân tích) thiếu yêu cầu học viên đề xuất 'Đa giải pháp' hoặc lập bảng 'So sánh/Lựa chọn' trong phần 'Yêu cầu đầu ra'."
            elif idx == 5:
                has_tech = "ràng buộc kỹ thuật" in yeu_cau_lower or "giới hạn công nghệ" in yeu_cau_lower
                has_output = "yêu cầu đầu ra" in yeu_cau_lower or "yêu cầu nộp bài" in yeu_cau_lower
                if not has_tech or not has_output:
                    return (
                        f"Bài 5 (Sáng tạo) thiếu thẻ cấu trúc bắt buộc 'Ràng buộc kỹ thuật' hoặc 'Yêu cầu đầu ra' trong yeu_cau_chi_tiet. "
                        "Hãy thiết lập đúng dạng:\n"
                        "[Ràng buộc kỹ thuật]: Giới hạn công nghệ...\n\n"
                        "[Yêu cầu đầu ra]: 1. Thiết kế kiến trúc (Module, data flow). 2. Sản phẩm hoàn chỉnh (Code xử lý mượt mọi ngoại lệ)."
                    )
                if "kiến trúc" not in yeu_cau_lower and "module" not in yeu_cau_lower and "data flow" not in yeu_cau_lower:
                    return f"Bài 5 (Sáng tạo) thiếu yêu cầu học viên nộp 'Thiết kế kiến trúc' hoặc mô tả 'luồng dữ liệu' trong phần 'Yêu cầu đầu ra'."

        # 4. Kiểm tra nguyên tắc Đóng HOW (Cấm chỉ dẫn thuật toán trong đề bài)
        forbidden_phrases = [
            "sử dụng hàm split", "sử dụng hàm join", "sử dụng hàm strip", "sử dụng hàm replace", "sử dụng hàm sort",
            "dùng hàm split", "dùng hàm join", "dùng hàm strip", "dùng hàm replace", "dùng hàm sort", "dùng hàm pop",
            "sử dụng vòng lặp for", "sử dụng vòng lặp while", "sử dụng câu lệnh if", "dùng vòng lặp"
        ]
        for idx, bt in enumerate(danh_sach, 1):
            yeu_cau = bt.get("yeu_cau_chi_tiet", "").lower()
            for phrase in forbidden_phrases:
                if phrase in yeu_cau:
                    return f"Bài {idx} vi phạm quy tắc Đóng HOW: Đề bài không được hướng dẫn giải thuật chi tiết (Phát hiện cụm từ cấm: '{phrase}'). Hãy mô tả WHAT/WHY và yêu cầu sinh viên tự chọn thuật toán."

        return None

    def _tool_publish_homework_markdown(self, homework_json):
        try:
            chu_de = homework_json.get("chu_de", "Bai_Tap")
            subject = homework_json.get("subject", "python").lower()
            print(f"   📝 [Publisher Tool] Tiến hành gửi bài tập học phần '{chu_de}' qua vòng lặp kiểm duyệt (Reflection Loop) môn '{subject}'...")
            
            # --- 1. KIỂM DUYỆT CỨNG BẰNG PYTHON (PROGRAMMATIC VALIDATION) ---
            validation_error = self._validate_homework_structure(homework_json)
            if validation_error:
                print(f"   [Programmatic Validation] Kiem duyet THAT BAI: {validation_error}")
                return f"Lỗi kiểm duyệt chất lượng (REJECTED): {validation_error} Vui lòng tự sửa đổi bài tập cho đúng quy chuẩn và gọi lại công cụ này."
            
            print("   [Programmatic Validation] Kiem duyet cau truc thanh cong.")
            
            # --- 2. ĐỌC QUY CHUẨN ĐỂ LLM SUPERVISOR KIỂM DUYỆT SÂU ---
            standards_context = ""
            try:
                standards_dir = os.path.join(config.DIR_STANDARDS, subject.capitalize())
                if os.path.exists(standards_dir):
                    contents = []
                    for f_name in os.listdir(standards_dir):
                        if f_name.endswith(('.txt', '.md')):
                            with open(os.path.join(standards_dir, f_name), "r", encoding="utf-8") as sf:
                                contents.append(sf.read())
                    if contents:
                        standards_context = "\n\n".join(contents)
                        print(f"   [Publisher Tool] Da doc truc tiep quy chuan tu o cung ({len(standards_context)} ky tu).")
            except Exception as fe:
                print(f"   [Publisher Tool] Loi doc quy chuan truc tiep: {fe}")

            if not standards_context:
                try:
                    res = self.chroma_client.col_standards.query(
                        query_texts=["Quy định xây dựng hệ thống bài tập"],
                        n_results=10,
                        where={"subject": subject}
                    )
                    if res and res.get('documents') and len(res['documents']) > 0:
                        standards_context = "\n\n".join(res['documents'][0])
                        print(f"   [Publisher Tool] Da tai quy chuan du phong tu Vector DB ({len(standards_context)} ky tu).")
                except Exception as dbe:
                    print(f"   [ChromaDB Warning] Loi khi truy van quy chuan du phong: {dbe}")
            
            if not standards_context:
                standards_context = (
                    "Quy chuẩn bắt buộc:\n"
                    "1. Gồm 5 bài (Bài 1&2: 1.5đ, Bài 3: 2đ, Bài 4: 2đ, Bài 5: 3đ), tổng điểm bằng 10.\n"
                    "2. Cấm ghi hướng dẫn giải thuật (HOW) trong đề bài.\n"
                    "3. Có bối cảnh thực tế đồng nhất, có bẫy dữ liệu."
                )

            # --- VÒNG LẶP KIỂM DUYỆT CHẤT LƯỢNG (REFLECTION LOOP) ---
            evaluation_instruction = (
                "Bạn là một Trưởng bộ môn kiểm định chất lượng học liệu chuyên nghiệp.\n"
                "Nhiệm vụ của bạn là đánh giá chất lượng bộ bài tập về nhà do AI Agent thiết kế sau đây.\n\n"
                "Bạn BẮT BUỘC phải đối chiếu kỹ lượng bộ bài tập với Tài liệu Quy chuẩn học liệu được cung cấp dưới đây.\n\n"
                f"--- TÀI LIỆU QUY CHUẨN KIỂM ĐỊNH ---\n{standards_context}\n--------------------------------------\n\n"
                "Các điểm kiểm tra cốt lõi bắt buộc (NẾU BÀI TẬP KHÔNG ĐÁP ỨNG THÌ PHẢI BÁO REJECTED NGAY):\n"
                "1. Số lượng bài tập có đúng là 5 bài theo đúng phân cấp (2 Vận dụng cơ bản, 1 Vận dụng chuyên sâu, 1 Phân tích, 1 Sáng tạo) không?\n"
                "2. Các bài Vận dụng cơ bản (Bài 1 & 2) có chứa mã nguồn lỗi trong trường 'code_loi_chua_sua' và yêu cầu học viên chỉ ra lỗi logic/vá lỗi không? (Cấm việc bắt học viên viết code từ đầu cho bài cơ bản).\n"
                "3. CẤM CHỈ ĐỊNH GIẢI THUẬT (ĐÓNG HOW): Đề bài tuyệt đối không được viết các câu hướng dẫn thuật toán hay hàm cụ thể kiểu 'sử dụng vòng lặp for', 'dùng hàm append', 'dùng split', v.v. Sinh viên phải tự quyết định cách giải. Nếu đề bài CHỈ mô tả nghiệp vụ (What) và lý do (Why) mà KHÔNG hướng dẫn thuật toán, đây là hành vi ĐÚNG ĐẮN, bạn phải phê duyệt. Nghiêm cấm từ chối bài tập vì lý do 'thiếu hướng dẫn thuật toán/hàm số'.\n"
                "4. Bài tập có bối cảnh dự án/vai diễn (Roleplay) thực tế không hay là các bài toán học vô tri (UCLN, in mảng, in số tự nhiên...)?\n"
                "5. Có cài cắm bẫy dữ liệu dị biệt (Edge cases) và yêu cầu sinh viên viết code chặn lỗi để tránh crash không?\n"
                "6. Tổng số điểm của cả bộ bài tập có đúng bằng 10 điểm hay không? (Bắt buộc phân bổ: Bài 1: 1.5đ, Bài 2: 1.5đ, Bài 3: 2đ, Bài 4: 2đ, Bài 5: 3đ).\n"
                "7. Các bài tập có chung một bối cảnh nghiệp vụ đồng nhất (E-commerce, FinTech...) và bài sau kế thừa bài trước không?\n"
                "8. Các phần 'yeu_cau_chi_tiet' có chứa đúng các đầu mục con quy định cho từng cấp độ bài tập không?\n\n"
                "BẮT BUỘC TRẢ VỀ JSON CÓ CẤU TRÚC CHÍNH XÁC NHƯ SAU:\n"
                "{\n"
                '  "status": "APPROVED" hoặc "REJECTED",\n'
                '  "reason": "Giải thích chi tiết lý do duyệt hoặc lý do từ chối cụ thể kèm hướng dẫn từng bước cách sửa đổi bài tập cho đúng tiêu chuẩn"\n'
                "}"
            )
            
            eval_prompt = f"Hãy đánh giá bộ bài tập sau:\n{json.dumps(homework_json, ensure_ascii=False, indent=2)}"
            
            print("   [Reflection Loop] Dang goi Truong bo mon LLM de kiem dinh chat luong...")
            eval_res = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": evaluation_instruction},
                    {"role": "user", "content": eval_prompt}
                ],
                format="json"
            )
            
            eval_data = json.loads(eval_res['message']['content'])
            status = eval_data.get("status", "REJECTED").upper()
            reason = eval_data.get("reason", "Không có mô tả chi tiết lý do.")
            
            if status == "REJECTED":
                print(f"   [Reflection Loop] Kiem duyet THAT BAI: {reason}")
                return f"Lỗi kiểm duyệt chất lượng (REJECTED): {reason}. Vui lòng tự sửa đổi bài tập cho đúng quy chuẩn và gọi lại công cụ này."
                
            print("   [Reflection Loop] Kiem duyet THANH CONG: APPROVED.")
            
            # --- LƯU TRỮ VẬT LÝ SAU KHI ĐƯỢC PHÊ DUYỆT ---
            safe_name = chu_de.replace(" ", "_").replace("-", "_")
            json_file_path = os.path.join(config.OUTPUT_JSON_DIR, f"RawAgent_{safe_name}.json")
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(homework_json, f, ensure_ascii=False, indent=4)
                
            # Đóng gói sang Markdown
            md_file_path = publish_json_to_markdown(homework_json)
            if md_file_path:
                return f"Kiểm duyệt thông qua (APPROVED). Đã xuất bản file JSON tại '{json_file_path}' và file Markdown tại '{md_file_path}'."
            return "Kiểm duyệt thông qua nhưng gặp lỗi khi xuất bản file Markdown."
            
        except Exception as e:
            return f"Lỗi trong quá trình kiểm duyệt và xuất bản: {str(e)}"

    def _tool_fetch_rikkei_systems(self):
        print("   [Rikkei API Tool] Goi API de lay danh sach He dao tao...")
        systems = self.api_service.get_systems()
        if systems:
            return json.dumps(systems, ensure_ascii=False, indent=2)
        return "Thất bại: Token hết hạn hoặc server bảo trì."

    def _tool_sync_homework_to_rikkei(self, homework_json):
        print("   [Rikkei API Tool] Dang dong bo hoa bai tap len Rikkei Portal...")
        success = self.api_service.post_homework(homework_json)
        if success:
            return "Đồng bộ bài tập lên Rikkei Portal thành công!"
        return "Thất bại khi kết nối máy chủ đồng bộ."

    # --- HÀM CHẠY CHÍNH ---

    def run_agent(self, user_command):
        """
        Kích hoạt vòng lặp tư duy tự quyết định công cụ (ReAct loop) của RikkeiAgent.
        """
        print(f"\n[Agent] Da tiep nhan yeu cau hanh dong tu tri: '{user_command}'")
        final_answer = self.chat_with_tools(
            user_message=user_command,
            system_instruction=self.system_instruction,
            tools_map=self.tools_map
        )
        return final_answer
