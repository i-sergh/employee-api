from database import Base
from sqlalchemy import (Column, Integer, String, DateTime, Date, CheckConstraint,
                        Boolean, func)

from config import IMG_DEFAULT_MINI, IMG_DEFAULT


class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True)

    last_name = Column(String(100), index=True, default="")    
    first_name = Column(String(100), index=True, default="")   
    middle_name = Column(String(100), index=True, default="")   

    sex = Column(String(5), default="")
    
    sex = Column(String(5), default="")
    phone = Column(String(20), index=True, default="")
    birth_date = Column(Date, default=None)

    image = Column(String(500), default=IMG_DEFAULT)
    image_mini = Column(String(500), default=IMG_DEFAULT_MINI)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    draft = Column(Boolean, default=True, nullable=False)
    

    __table_args__ = (
        CheckConstraint("sex IN ('муж.', 'жен.', '')", name="check_sex"),
    )


