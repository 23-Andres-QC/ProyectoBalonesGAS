from app.infrastructure.persistence.memory.in_memory_user_repo import InMemoryUserRepo
from app.infrastructure.security.auth_service import AuthService

class Container:
    def __init__(self):
        self.user_repo = InMemoryUserRepo()
        self.auth_service = AuthService()

# Global instance
container = Container()
