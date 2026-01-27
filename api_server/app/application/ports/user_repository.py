from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass
