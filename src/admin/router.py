
from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy import Delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from employee import router as e_router
from employee import models as e_models
from employee.schemas import EmployeeEdit
from admin.employees_data import EMPLOYEES_DATA



router = APIRouter(prefix="/admin", tags=["Admin"])

'''
Данные ручки исключительно для ручного тестирования
'''


@router.post("/generate-employees")
async def generate_employees(db:Annotated[AsyncSession, Depends(get_async_session)]):
    """
    Генерирует 165 тестовых сотрудников из заготовленного списка.
    """
    created_count = 0
    errors = []

    for employee_data in EMPLOYEES_DATA:
        try:
            # создаем запись сотрудника
            e_id = await e_router.employee_create_empty_entry(db=db)

            # Обновляем его 
            e_data = EmployeeEdit(**employee_data)
            await e_router.employee_edit(db=db,employe_data=e_data, id=e_id['id'])

            created_count += 1
        except Exception as e:
            errors.append({
                "employee": f"{employee_data['last_name']} {employee_data['first_name']}",
                "error": str(e)
            })

    return {
        "message": f"Создано {created_count} сотрудников",
        "total": len(EMPLOYEES_DATA),
        "created": created_count,
        "errors": errors,
    }

@router.delete("/delete-all-employees")
async def delete_employees( db:Annotated[AsyncSession, Depends(get_async_session)],
                            r_u_sure:bool=False):
    """
    Удаляет все записи из модели Employee
    """
    sql = Delete(e_models.Employee)
    await db.execute(sql)
    await db.commit()

    return {'result': 'success'}
    