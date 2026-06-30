import requests

class RikkeiPortalAPI:
    """
    Dịch vụ tích hợp kết nối với API Rikkei Portal.
    """
    def __init__(self, token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im5ndXllbmx4aEByaWtrZWllZHVjYXRpb24uY29tIiwibmFtZSI6IkzGsHUgWHXDom4gSG_DoG5nIE5ndXnDqm4iLCJpZCI6NTQsInJvbGUiOlt7ImlkIjozLCJuYW1lIjoiVEVBQ0hFUiJ9LHsiaWQiOjQsIm5hbWUiOiJURUFDSEVSX0FTU0lTVEFOVCJ9XSwidHlwZSI6InVzZXIiLCJpYXQiOjE3ODI3OTcxOTgsImV4cCI6MTc4Mjg4MzU5OH0.hRAgLRE6kwZZWAJ6jDflxy3GCh6wtdVwczUAhxN9P5k"):
        self.domain = "https://apiportal.rikkei.edu.vn"
        
        # Chuẩn hóa Bearer Token
        if token and not token.startswith("Bearer "):
            self.token = f"Bearer {token}"
        else:
            self.token = token

    def get_systems(self):
        """
        Lấy danh sách các Hệ đào tạo hiện có trên Rikkei Portal.
        """
        url = f"{self.domain}/automation/systems"
        headers = {
            "Accept": "application/json",
            "Authorization": self.token
        }
        
        print("[Rikkei Portal API] Dang gui yeu cau lay danh sach He dao tao...")
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                systems = response.json()
                print("Ket noi thanh cong! Nhan phan hoi tu Rikkei Portal.")
                return systems
            elif response.status_code in [401, 403]:
                print(f"[Loi] {response.status_code}: Token het han hoac khong hop le. Hay kiem tra lai.")
                return None
            else:
                print(f"[Loi] tu server Rikkei Portal: Ma {response.status_code}")
                return None
        except Exception as e:
            print(f"[Loi] That bai khi ket noi API: {e}")
            return None

    def post_homework(self, homework_data):
        """
        [Mở rộng trong tương lai] Đẩy dữ liệu bài tập về nhà đã được sinh tự động lên hệ thống QLĐT.
        """
        # API endpoint thực tế sẽ được định nghĩa ở đây
        # url = f"{self.domain}/automation/homework"
        print("[Rikkei Portal API] Chuc nang day truc tiep bai tap len QLDT dang duoc phat trien...")
        return True
