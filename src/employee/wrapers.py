from sqlalchemy import Select
from sqlalchemy.orm import Session
from functools import wraps
from fastapi import HTTPException, status

from employee import models, schemas


def employee_existance(func):
    """
    wraper
    Checks the employee existance by id. If not found - 404


    """
    @wraps(func)
    async def wrapper(db:Session, 
                      id:int,
                      *args,
                      **kwargs):
        
        sql = Select(models.Employee).where(models.Employee.id == id)
        result = (await db.execute(sql)).scalars().first()
        if result == None:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
        return await func(db=db,id=id, *args, **kwargs)
    return wrapper