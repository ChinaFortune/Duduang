import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
USERS_DB_PATH = BASE_DIR / 'bazi' / 'data' / 'users_database.json'

def _hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = "duduang_secure_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

class AuthProviderBase:
    """
    Abstract Base Authentication Provider.
    Subclass this interface to integrate with external identity providers
    such as Supabase, Firebase, OAuth2, or custom Microservice APIs.
    """
    def register(self, email: str, password: str, full_name: str = "") -> dict:
        raise NotImplementedError

    def authenticate(self, email: str, password: str) -> dict:
        raise NotImplementedError

    def get_user_by_id(self, user_id: str) -> dict:
        raise NotImplementedError

    def list_users(self) -> list:
        raise NotImplementedError

    def create_user(self, email: str, password: str, full_name: str = "", role: str = "member") -> dict:
        raise NotImplementedError

    def update_user(self, user_id: str, email: str = None, full_name: str = None, role: str = None, password: str = None) -> dict:
        raise NotImplementedError

    def delete_user(self, user_id: str) -> dict:
        raise NotImplementedError


class ExternalApiAuthProviderTemplate(AuthProviderBase):
    """
    [TEMPLATE FOR FUTURE API INTEGRATION]
    Fill in your API credentials and endpoints here once an external authentication
    service (e.g. Supabase, Auth0, FastAPI backend) is ready to connect.
    """
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or os.environ.get("AUTH_API_URL", "https://api.example.com/v1/auth")
        self.api_key = api_key or os.environ.get("AUTH_API_KEY", "")

    def register(self, email: str, password: str, full_name: str = "") -> dict:
        # TODO: Implement HTTP POST to external API endpoint
        # Example: response = requests.post(f"{self.api_url}/register", json={...}, headers={...})
        pass

    def authenticate(self, email: str, password: str) -> dict:
        # TODO: Implement HTTP POST to external API login endpoint
        # Example: response = requests.post(f"{self.api_url}/login", json={...})
        pass

    def get_user_by_id(self, user_id: str) -> dict:
        # TODO: Implement GET user profile from external API
        pass

    def list_users(self) -> list:
        # TODO: Implement GET all users list for admin dashboard
        pass


class JsonFileAuthProvider(AuthProviderBase):
    """
    Local JSON-based User Store used as temporary mock database
    until external API connection is activated.
    """
    def __init__(self, file_path: Path = USERS_DB_PATH):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not self.file_path.exists():
            default_data = {
                "users": [
                    {
                        "id": "usr_admin_01",
                        "email": "consultant@duduang.com",
                        "password_hash": _hash_password("admin8888"),
                        "full_name": "อาจารย์หนิง ซินแสพลังงาน",
                        "role": "consultant",
                        "created_at": "2026-01-01T08:00:00Z",
                        "last_login": "2026-09-10T00:00:00Z"
                    },
                    {
                        "id": "usr_demo_02",
                        "email": "user@example.com",
                        "password_hash": _hash_password("password123"),
                        "full_name": "กฤษณะ แสงทอง",
                        "role": "member",
                        "created_at": "2026-02-14T09:30:00Z",
                        "last_login": "2026-09-09T18:00:00Z"
                    }
                ]
            }
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)

    def _read_data(self) -> dict:
        self._ensure_file()
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_data(self, data: dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def register(self, email: str, password: str, full_name: str = "") -> dict:
        data = self._read_data()
        clean_email = email.strip().lower()
        for u in data.get("users", []):
            if u["email"].lower() == clean_email:
                return {"success": False, "error": "อีเมลนี้ถูกลงทะเบียนไว้แล้วในระบบ"}

        new_user = {
            "id": f"usr_{int(datetime.now().timestamp())}",
            "email": clean_email,
            "password_hash": _hash_password(password),
            "full_name": full_name.strip() or clean_email.split('@')[0],
            "role": "member",
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
        data.setdefault("users", []).append(new_user)
        self._write_data(data)
        return {"success": True, "user": new_user}

    def authenticate(self, email: str, password: str) -> dict:
        data = self._read_data()
        clean_email = email.strip().lower()
        hashed = _hash_password(password)
        for u in data.get("users", []):
            if u["email"].lower() == clean_email:
                if u["password_hash"] == hashed:
                    u["last_login"] = datetime.now().isoformat()
                    self._write_data(data)
                    return {"success": True, "user": u}
                else:
                    return {"success": False, "error": "รหัสผ่านไม่ถูกต้อง"}
        return {"success": False, "error": "ไม่พบบัญชีผู้ใช้นี้ในระบบ"}

    def get_user_by_id(self, user_id: str) -> dict:
        data = self._read_data()
        for u in data.get("users", []):
            if u["id"] == user_id:
                return u
        return None

    def list_users(self) -> list:
        data = self._read_data()
        return data.get("users", [])

    def create_user(self, email: str, password: str, full_name: str = "", role: str = "member") -> dict:
        data = self._read_data()
        clean_email = email.strip().lower()
        if not clean_email:
            return {"success": False, "error": "กรุณาระบุอีเมล"}
        if not password:
            return {"success": False, "error": "กรุณาระบุรหัสผ่าน"}
        for u in data.get("users", []):
            if u["email"].lower() == clean_email:
                return {"success": False, "error": "อีเมลนี้มีอยู่ในระบบแล้ว"}

        new_user = {
            "id": f"usr_{int(datetime.now().timestamp())}",
            "email": clean_email,
            "password_hash": _hash_password(password),
            "full_name": full_name.strip() or clean_email.split('@')[0],
            "role": role.strip().lower() if role else "member",
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
        data.setdefault("users", []).append(new_user)
        self._write_data(data)
        return {"success": True, "user": new_user}

    def update_user(self, user_id: str, email: str = None, full_name: str = None, role: str = None, password: str = None) -> dict:
        data = self._read_data()
        user_found = None
        for u in data.get("users", []):
            if u["id"] == user_id:
                user_found = u
                break
        if not user_found:
            return {"success": False, "error": "ไม่พบผู้ใช้นี้"}

        if email:
            clean_email = email.strip().lower()
            for other in data.get("users", []):
                if other["id"] != user_id and other["email"].lower() == clean_email:
                    return {"success": False, "error": "อีเมลนี้ถูกใช้งานโดยผู้ใช้อื่นแล้ว"}
            user_found["email"] = clean_email

        if full_name is not None:
            user_found["full_name"] = full_name.strip()

        if role:
            user_found["role"] = role.strip().lower()

        if password:
            user_found["password_hash"] = _hash_password(password)

        self._write_data(data)
        return {"success": True, "user": user_found}

    def delete_user(self, user_id: str) -> dict:
        data = self._read_data()
        original_count = len(data.get("users", []))
        data["users"] = [u for u in data.get("users", []) if u["id"] != user_id]
        if len(data["users"]) == original_count:
            return {"success": False, "error": "ไม่พบผู้ใช้ที่ต้องการลบ"}
        self._write_data(data)
        return {"success": True}


# Default active provider instance (Switchable to ExternalApiAuthProviderTemplate when ready)
auth_service = JsonFileAuthProvider()

