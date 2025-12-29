from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",  # React app default port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Centralized License System API"}

# Brand Endpoints
@app.post("/brands/", response_model=schemas.Brand)
def create_brand(brand: schemas.BrandCreate, db: Session = Depends(get_db)):
    db_brand = crud.get_brand_by_name(db, name=brand.name)
    if db_brand:
        raise HTTPException(status_code=400, detail="Brand already registered")
    return crud.create_brand(db=db, brand=brand)

@app.get("/brands/", response_model=List[schemas.Brand])
def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    brands = crud.get_brands(db, skip=skip, limit=limit)
    return brands

# Product Endpoints
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

# Customer Endpoints
@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_customer(db=db, customer=customer)

@app.get("/customers/", response_model=List[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return customers


@app.get("/customers/{email}/licenses", response_model=List[schemas.License])
def read_customer_licenses(email: str, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_email(db, email=email)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.get_licenses_by_customer(db, customer_id=db_customer.id)


# License Endpoints
@app.post("/licenses/", response_model=schemas.License)
def create_license(license: schemas.LicenseCreate, db: Session = Depends(get_db)):
    start_key = license.key if license.key else str(uuid.uuid4())
    # Ensure key validation or auto-generation logic is handled if needed
    # For now, we assume key comes from request or needs generating
    if not license.key:
         license.key = str(uuid.uuid4())
    
    db_license = crud.get_license_by_key(db, key=license.key)
    if db_license:
        raise HTTPException(status_code=400, detail="License key already exists")
    return crud.create_license(db=db, license=license)

@app.post("/licenses/validate", response_model=dict)
def validate_license(validation: schemas.LicenseValidate, db: Session = Depends(get_db)):
    db_license = crud.get_license_by_key(db, key=validation.key)
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    
    if db_license.product_id != validation.product_id:
         raise HTTPException(status_code=400, detail="License invalid for this product")

    if not db_license.is_active:
         return {"valid": False, "reason": "License is inactive"}
    
    # Check expiration if set
    if db_license.expiration_date:
        import datetime
        if db_license.expiration_date < datetime.datetime.utcnow():
             return {"valid": False, "reason": "License expired"}

    return {"valid": True, "seats_available": db_license.max_seats - db_license.active_seats, "activations_count": db_license.active_seats}

@app.put("/licenses/{license_id}/suspend", response_model=schemas.License)
def suspend_license(license_id: int, db: Session = Depends(get_db)):
    db_license = crud.get_license(db, license_id=license_id)
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    return crud.update_license_status(db=db, license_id=license_id, is_active=False)

@app.put("/licenses/{license_id}/resume", response_model=schemas.License)
def resume_license(license_id: int, db: Session = Depends(get_db)):
    db_license = crud.get_license(db, license_id=license_id)
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    return crud.update_license_status(db=db, license_id=license_id, is_active=True)


@app.post("/licenses/activate", response_model=schemas.Activation)
def activate_license(activation: schemas.ActivationCreate, db: Session = Depends(get_db)):
    # 1. Find License
    db_license = crud.get_license_by_key(db, key=activation.license_key)
    if not db_license:
         raise HTTPException(status_code=404, detail="License not found")
    
    # 2. Check Validity
    if not db_license.is_active:
         raise HTTPException(status_code=400, detail="License is inactive")
    
    if db_license.expiration_date:
        import datetime
        if db_license.expiration_date < datetime.datetime.utcnow():
             raise HTTPException(status_code=400, detail="License expired")

    # 3. Check Duplicate Activation (Idempotency)
    existing_activation = crud.get_activation(db, license_id=db_license.id, machine_id=activation.machine_id)
    if existing_activation:
        return existing_activation

    # 4. Check Seats
    if db_license.active_seats >= db_license.max_seats:
         raise HTTPException(status_code=400, detail="Max seats reached")

    # 5. Create Activation
    return crud.create_activation(db=db, license_id=db_license.id, machine_id=activation.machine_id, friendly_name=activation.friendly_name)

@app.delete("/activations/{activation_id}")
def delete_activation(activation_id: int, db: Session = Depends(get_db)):
    success = crud.delete_activation(db, activation_id=activation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activation not found")
    return {"detail": "Activation deleted"}


