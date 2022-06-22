from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel, Field
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from geopy import distance
import coordinates
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db =SessionLocal()
        yield db
    finally:
        db.close()

class Address_Book(BaseModel):
    
    address:str = Field(min_lehgth=1,max_length=200)


ADDRESS = []


# Get all data
@app.get("/")
def read_api(db: Session = Depends(get_db)):
    return db.query(models.Address).all()


# Get all data under the given radius from given address in parameter in km
@app.get("/nearby/{distance_in_km}/{street}/{city}/{state}")
def read_api(distance_in_miles:float,street:str,city:str,state:str,db: Session = Depends(get_db)):
    coordinates_loc = coordinates.coordinates(street+","+city+","+state)
    lat,lon=coordinates_loc.split(",")
    lat,lon= float(lat),float(lon)
    all_data=db.query(models.Address).all()

    near_by = []
    for single_add in all_data:
        cal_dis = distance.distance((lat,lon), ([float(x) for x in single_add.coordinates.split(",")])).km
        given_dis = distance_in_miles
        if cal_dis<=given_dis:
            near_by.append(single_add)

    return near_by
    
    
# Post the address and coordinates into Database 
@app.post("/")
def create_address(address:Address_Book, db:Session = Depends(get_db)):

    address_model = models.Address()
    address_model.address = address.address
    address_model.coordinates = coordinates.coordinates(address_model.address)

    db.add(address_model)
    db.commit()

    return address


# Update the address
@app.put("/{address_id}")
def update_address(address_id:int, address:Address_Book, db: Session = Depends(get_db)):
    address_model = db.query(models.Address).filter(models.Address.id == address_id).first()

    if address_model is None:
        raise HTTPException(
            status_code = 404,
            detail = f"ID {address_id} : Does not exist"
        )

    address_model.address = address.address
    address_model.coordinates = coordinates.coordinates(address_model.address)

    db.add(address_model)
    db.commit()

    return address 


#Delete the address
@app.delete("/{address_id}")
def delete_address(address_id:int, db: Session = Depends(get_db)):
    
    address_model = db.query(models.Address).filter(models.Address.id == address_id).first()

    if address_model is None:
        raise HTTPException(
            status_code=404,
            detail = f"ID {address_id} : Does not exist"
        )
    
    db.query(models.Address).filter(models.Address.id == address_id).delete()
    db.commit()