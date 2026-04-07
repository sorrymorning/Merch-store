from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from app.repositories.repository import UserRepository
from app.models.models import Users

import pytest

@pytest.fixture
def mock_db() -> AsyncMock:
    """
    Mock AsyncSession
    """
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db



class TestUserRepository:
    @pytest.mark.asyncio
    async def test_get_user_info(self, mock_db):
        repo = UserRepository(mock_db)
        user = Users(
            username = "Amir",
            password_hash = "asdasd"
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        mock_db.execute.return_value = mock_result

        result = await repo.get_info(1)
        assert result == user
        mock_db.execute.assert_called_once()

