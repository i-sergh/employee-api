import pytest
from sqlalchemy import text
from config import PG_TEST_NAME



@pytest.mark.asyncio( loop_scope="module")
async def test_database_connection(get_async_session):
    """Проверяем подключение к тестовой БД"""
    async with get_async_session as session:
        
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1


@pytest.mark.asyncio( loop_scope="module")
async def test_database_name(get_async_session):
    """Проверяем,что БД именно тестовая"""
    async with get_async_session as session:
    
        result = await session.execute(text("SELECT current_database()"))
        db_name = result.scalar()
        assert db_name == PG_TEST_NAME