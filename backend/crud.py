from sqlalchemy.orm import Session
from . import models, schemas
import uuid
import logging

logger = logging.getLogger(__name__)

# Brand CRUD
def get_brand(db: Session, brand_id: int):
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()

def get_brand_by_name(db: Session, name: str):
    return db.query(models.Brand).filter(models.Brand.name == name).first()

def get_brands(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Brand).offset(skip).limit(limit).all()

def create_brand(db: Session, brand: schemas.BrandCreate):
    db_brand = models.Brand(name=brand.name, email=brand.email)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    logger.info(f"Brand created: {db_brand.name} (ID: {db_brand.id})")
    return db_brand

# Product CRUD
def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product created: {db_product.name} (ID: {db_product.id}, Brand ID: {db_product.brand_id})")
    return db_product

# Customer CRUD
def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def get_customer_by_email(db: Session, email: str):
    return db.query(models.Customer).filter(models.Customer.email == email).first()

def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(email=customer.email)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# License CRUD
def get_license(db: Session, license_id: int):
    return db.query(models.License).filter(models.License.id == license_id).first()

def get_license_by_key(db: Session, key: str):
    return db.query(models.License).filter(models.License.key == key).first()

def create_license(db: Session, license: schemas.LicenseCreate):
    db_license = models.License(**license.model_dump())
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    logger.info(f"License created for customer ID {db_license.customer_id}, product ID {db_license.product_id}")
    return db_license

def get_licenses_by_customer(db: Session, customer_id: int):
    return db.query(models.License).filter(models.License.customer_id == customer_id).all()

# Activation CRUD
def get_activation(db: Session, license_id: int, machine_id: str):
    return db.query(models.Activation).filter(
        models.Activation.license_id == license_id,
        models.Activation.machine_id == machine_id
    ).first()

def create_activation(db: Session, license_id: int, machine_id: str, friendly_name: str = None):
    db_activation = models.Activation(
        license_id=license_id,
        machine_id=machine_id,
        friendly_name=friendly_name
    )
    db.add(db_activation)
    
    # Increment seat count on license
    db_license = get_license(db, license_id)
    if db_license:
        db_license.active_seats += 1
        
    db.commit()
    db.refresh(db_activation)
    logger.info(f"License activated on machine {machine_id} for license ID {license_id}")
    return db_activation

def delete_activation(db: Session, activation_id: int):
    db_activation = db.query(models.Activation).filter(models.Activation.id == activation_id).first()
    if db_activation:
        # Decrement seat count
        db_license = get_license(db, db_activation.license_id)
        if db_license and db_license.active_seats > 0:
            db_license.active_seats -= 1
            
        db.delete(db_activation)
        db.commit()
        return True
    return False

def update_license_status(db: Session, license_id: int, is_active: bool):
    db_license = get_license(db, license_id)
    if db_license:
        db_license.is_active = is_active
        db.commit()
        db.refresh(db_license)
        return db_license
    return None

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

# API Key CRUD
def create_api_key(db: Session, key_hash: str, api_key: schemas.APIKeyCreate):
    """Create a new API key with hashed key."""
    db_api_key = models.APIKey(
        key_hash=key_hash,
        name=api_key.name,
        brand_id=api_key.brand_id,
        expires_at=api_key.expires_at
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def get_api_key(db: Session, api_key_id: int):
    """Get a specific API key by ID."""
    return db.query(models.APIKey).filter(models.APIKey.id == api_key_id).first()

def get_all_api_keys(db: Session):
    """Get all API keys (for validation purposes)."""
    return db.query(models.APIKey).filter(models.APIKey.is_active == True).all()

def list_api_keys(db: Session, skip: int = 0, limit: int = 100):
    """List all API keys (for admin purposes)."""
    return db.query(models.APIKey).offset(skip).limit(limit).all()

def update_api_key_last_used(db: Session, api_key_id: int):
    """Update the last_used_at timestamp for an API key."""
    from datetime import datetime
    db_api_key = get_api_key(db, api_key_id)
    if db_api_key:
        db_api_key.last_used_at = datetime.utcnow()
        db.commit()
    return db_api_key

def revoke_api_key(db: Session, api_key_id: int):
    """Revoke (deactivate) an API key."""
    db_api_key = get_api_key(db, api_key_id)
    if db_api_key:
        db_api_key.is_active = False
        db.commit()
        db.refresh(db_api_key)
    return db_api_key
