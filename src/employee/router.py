from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from math import ceil

from employee import crud, schemas, wrapers
from database import get_async_session


router = APIRouter(prefix="/articles", tags=["Articles"])

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.get("/")
async def employee_list(db:Annotated[Session, Depends(get_async_session)],
                        page: int = Query(default=1, ge=1),
                        per_page: int = Query(default=10, choices=[10, 25, 50]),
                        show_drafts:bool=False,
                        age_from:int|None=None,
                        age_to:int|None=None,
                        show_male:bool=True,
                        show_female:bool=True,
                        search:str=''):
    
    serch_parse = crud.parse_search_result(search=search)
    if serch_parse.skip:
            return {'items': [],
            'total': 0,
            'total_pages': 1,
            'page': page,
            'per_page': per_page}
    
    employees, total = await crud.get_employee_list(db=db,
                                            limit=per_page,
                                            offset=per_page*(page-1),
                                            show_drafts=show_drafts,
                                            show_male=show_male,
                                            show_female=show_female,
                                            search=serch_parse,
                                            age_from=age_from,
                                            age_to=age_to) 

    total_pages = ceil(total/per_page) if total > 0 else 1

    return {'items': employees,
            'total': total,
            'total_pages': total_pages,
            'page': page,
            'per_page': per_page}


@router.post("/")
async def employee_create_empty_entry(db:Annotated[Session, Depends(get_async_session)]):
    result = await crud.create_employee_empty_entry(db=db)
    return {"id": result}


@router.get("/{id}")
@wrapers.employee_existance
async def employee_get(id:int,
                       db:Annotated[Session, Depends(get_async_session)]):
    
    return await crud.get_employee(id=id, db=db)


@router.put("/{id}")
@wrapers.employee_existance
async def employee_edit(id:int,
                        employe_data:schemas.EmployeeEdit,
                        db:Annotated[Session, Depends(get_async_session)]):
    await crud.edit_employee(id=id, employee_data=employe_data, db=db)
    return {'result': 'success'}
    

@router.delete("/{id}")
@wrapers.employee_existance
async def employee_delete(id:int,
                          db:Annotated[Session, Depends(get_async_session)]):
    await crud.delete_employee(id=id, db=db)

    return {'result': 'success'}


@router.post("/{id}/upload-photo")
@wrapers.employee_existance
async def upload_photo( db:Annotated[Session, Depends(get_async_session)],
                        id: int,
                        file: UploadFile = File(...)):
    
    ext = await crud.verify_image(file)


    im_link, im_link_mini = await crud.save_image(id=id, file=file, ext=ext)

    await crud.update_employee_image(id=id,
                                     im_link=im_link,
                                     im_link_mini=im_link_mini,
                                     db=db)

    return {"image_url": im_link}