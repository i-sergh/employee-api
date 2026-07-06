from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from typing import List
import re


class EmployeeEdit(BaseModel):
    last_name:str|None=None
    first_name:str|None=None   
    middle_name:str|None=None   
    sex:str|None=None
    phone:str|None=None
    birth_date:date|None=None

    draft:bool=True

    @model_validator(mode="after")
    def check_if_draft(self):
        """
        Checks all required fields when draft is false
        """
        if not self.draft:
            missing_fields = []
            # проверяем все требуемые поля
            for field in ["first_name", "last_name", "sex", "phone", "birth_date"]:
                if getattr(self, field) in (None, ""):
                    missing_fields.append(field)
            # при наличии пустых полей - ошибка
            if missing_fields:
                raise ValueError(
                    f"Fill in the required fields: {', '.join(missing_fields)}"
                )
        return self
 
    @model_validator(mode="after")
    def validate_phone(self):
        '''
        Validatnes phone number
        unifies the phone number format
        '''
        v = self.phone
        
        if v == "" and self.draft == True:
            return self
        # убираем пробелы
        v = "".join(v.split())
        # убираем все знаки
        v = re.sub(r"[^\d+]", "", v)
        # проверяем на соответствие формату номера телефона
        pattern = r"^(?:\+7|8)\d{10}$"
        if not re.match(pattern, v):
            raise ValueError("Incorrect phone number format") #
        return self
    
    @field_validator("sex")
    def validate_sex(v):
        if v  in ['муж.', 'жен.', '']:
            return v
        raise ValueError(f"Incorrect sex format. Should be {['муж.', 'жен.', '']}")
    
    

class ParsedSearch(BaseModel):
    strs:List[str]=[]
    nums:List[str]=[]
    skip:List[str]=[]