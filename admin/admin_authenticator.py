# Pattern: Singleton
import hashlib
from datetime import datetime, timedelta
from typing import Optional

class AdminAuthenticator:

    
    _instance = None
    
    # Default admin credentials (in production, use environment variables or secure config)
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdminAuthenticator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.current_session = None
        self.session_timeout = timedelta(hours=1)
        self._initialized = True
    
    def verify_credentials(self, password: str) -> bool:

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == self.ADMIN_PASSWORD_HASH
    
    def create_session(self, username: str = "admin") -> str:

        session_id = hashlib.sha256(
            f"{username}{datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        self.current_session = {
            "id": session_id,
            "username": username,
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        return session_id
    
    def validate_session(self, session_id: Optional[str] = None) -> bool:

        if not self.current_session:
            return False
        
        if session_id and session_id != self.current_session["id"]:
            return False
        
        # Check if session has expired
        time_elapsed = datetime.now() - self.current_session["last_activity"]
        if time_elapsed > self.session_timeout:
            self.current_session = None
            return False
        
        # Update last activity
        self.current_session["last_activity"] = datetime.now()
        return True
    
    def logout(self):

        self.current_session = None
    
    def is_admin_logged_in(self) -> bool:

        return self.validate_session()
    
    def get_current_session(self) -> Optional[dict]:

        if self.validate_session():
            return self.current_session.copy()
        return None
