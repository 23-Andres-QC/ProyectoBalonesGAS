from typing import Optional
from app.domain.entities.user import User
from app.application.ports.user_repository import UserRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class InMemoryUserRepo(UserRepository):
    def __init__(self):
        # Usuario: admin / pass: admin123
        self.users = {
            "admin": User(
                username="admin", 
                password_hash=pwd_context.hash("admin123"),
                role="admin"
            )
        }

    async def get_by_username(self, username: str) -> Optional[User]:
        return self.users.get(username)
