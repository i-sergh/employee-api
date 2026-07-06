from sqlalchemy import Select, Insert, Delete, Update, func, extract
from sqlalchemy.orm import Session
from PIL import Image
from fastapi import HTTPException, UploadFile
import os

from employee import models, schemas
from config import IMG_UPLOAD_DIR, STATIC_DIR


async def get_employee_list( db:Session,
                             limit:int=25,
                             offset:int=0, 
                             show_drafts:bool=False,
                             show_male:bool=True,
                             show_female:bool=True,
                             age_from:int|None=None,
                             age_to:int|None=None,
                             search:schemas.ParsedSearch=schemas.ParsedSearch()):

    sql = Select(
        models.Employee.id,
        func.concat(
                    models.Employee.last_name, ' ',
                    models.Employee.first_name, ' ',
                    models.Employee.middle_name
                ).label('full_name'),
        extract('year', func.age(models.Employee.birth_date)).label('age'),
        models.Employee.phone,
        models.Employee.sex,
        models.Employee.image_mini,
        models.Employee.image,
        models.Employee.draft,
        )
    sql_total = Select(func.count()).select_from(models.Employee)
    sex = []
    if show_male:
        sex.append('муж.') 
    if show_female:
        sex.append('жен.') 

    if not show_drafts:
        sql = sql.where(models.Employee.draft==False)
        sql_total = sql_total.where(models.Employee.draft==False)
    else:
        sex.append('')    
    
    sql = sql.where(models.Employee.sex.in_(sex))
    sql_total = sql_total.where(models.Employee.sex.in_(sex))

    for srch in search.strs:
        pattern = f'%{srch}%'
        sql = sql.where(models.Employee.first_name.like(pattern) |
                        models.Employee.last_name.like(pattern) |
                        models.Employee.middle_name.like(pattern))
        
        sql_total = sql_total.where(models.Employee.first_name.like(pattern) |
                                    models.Employee.last_name.like(pattern) |
                                    models.Employee.middle_name.like(pattern))

    for srch in search.nums:
        pattern = f'%{srch}%'
        sql = sql.where(models.Employee.phone.like(pattern))
        sql_total = sql_total.where(models.Employee.phone.like(pattern))

    if age_from:
        sql = sql.where(extract('year', func.age(models.Employee.birth_date))>=age_from)
        sql_total = sql_total.where(extract('year', func.age(models.Employee.birth_date))>=age_from)

    if age_to:
        sql = sql.where(extract('year', func.age(models.Employee.birth_date))<=age_to)
        sql_total = sql_total.where(extract('year', func.age(models.Employee.birth_date))<=age_to)

    sql = sql.limit(limit).offset(offset)
    
    result = await db.execute(sql)
    total = await db.scalar(sql_total)
    rows = result.mappings().all()

    return rows, total


async def get_employee(id:int, db:Session):
    sql = Select(models.Employee.id,
                 models.Employee.last_name, 
                 models.Employee.first_name, 
                 models.Employee.middle_name,
                 models.Employee.birth_date,
                 models.Employee.phone,
                 models.Employee.sex,
                 models.Employee.image_mini,
                 models.Employee.image,
                 models.Employee.draft,
                 ).where(models.Employee.id==id)
    result = await db.execute(sql)
    emp = result.mappings().first()
    return emp


def parse_search_result(search:str) -> schemas.ParsedSearch:
    subs = search.split()
    result = schemas.ParsedSearch()
    for sub in subs:
        if sub.isalpha():
            result.strs.append(sub)
            continue
        if sub.isdigit() or (sub[0] == '+' and sub.isdigit()):
            result.nums.append(sub)
            continue
        result.skip.append(sub)

    return result


async def create_employee_empty_entry( db:Session)->int:
    '''
    creates empty entry in db and returns it id
    '''
    sql = Insert(models.Employee)
    result = await db.execute(sql)
    await db.commit()
    return result.inserted_primary_key.id 


async def edit_employee(id:int,
                        employee_data:schemas.EmployeeEdit, 
                        db:Session):
    employee_dict = employee_data.model_dump()
    employee_dict['id'] = id
    sql = Update(models.Employee).\
            where(models.Employee.id==id).\
            values(**employee_dict)
    
    await db.execute(sql)
    await db.commit()


async def delete_employee(id:int,db:Session):

    sql = Delete(models.Employee).where(models.Employee.id == id)
    await db.execute(sql)
    await db.commit()



async def verify_image(file:UploadFile):
    
    if file.size > 200 * 1024:
        raise HTTPException(400, "The file size must not exceed 200 KB") 
    
    if not file.content_type.startswith("image/") :
        raise HTTPException(400, "Файл должен быть изображением")
    
    ALLOWED_FORMATS = {'jpeg', 'png', 'gif', 'webp', 'bmp'}
    try:
        file.file.seek(0)
        with Image.open(file.file) as img:
            format = img.format.lower() if img.format else ''
            if format not in ALLOWED_FORMATS:
                raise HTTPException()
            img.verify()

            return format
    except HTTPException: 
        raise HTTPException( 400, f"Поддерживаемые форматы: {', '.join(ALLOWED_FORMATS)}")
    except Exception:
        raise HTTPException(400, "Файл не является изображением")
    

async def generate_image_mini( file:UploadFile,
                               size: tuple[int, int] = (100, 100)) -> Image.Image:
    file.file.seek(0)
    with Image.open(file.file) as img:
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    


async def save_image(id:int, file:UploadFile, ext:str):

    filename = f"employee.{ext}"
    filename_mini = f"employee_mini.{ext}"
    filedir = os.path.join(STATIC_DIR, IMG_UPLOAD_DIR, str(id))
    filepath = os.path.join(STATIC_DIR, IMG_UPLOAD_DIR, str(id), filename)
    filepath_mini = os.path.join(STATIC_DIR, IMG_UPLOAD_DIR, str(id), filename_mini)

    link = os.path.join(IMG_UPLOAD_DIR,str(id),filename)
    link_mini = os.path.join(IMG_UPLOAD_DIR,str(id),filename_mini)

    os.makedirs(filedir, exist_ok=True)

    img_mini = await generate_image_mini(file=file)
    file.file.seek(0)
    
    with Image.open(file.file) as img:
        img.save(filepath, quality=85, optimize=True)
    img_mini.save(filepath_mini, quality=85, optimize=True)
    return link, link_mini


async def update_employee_image(id:int, im_link:str, im_link_mini:str, db:Session):
    sql = Update(models.Employee).\
            where(models.Employee.id==id).\
            values(image=im_link,
                   image_mini=im_link_mini)
    await db.execute(sql)
    await db.commit()