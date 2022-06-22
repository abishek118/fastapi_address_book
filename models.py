from sqlalchemy import Column,Integer,String
from database import Base

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index = True)
    address = Column(String)
    coordinates = Column(String)



