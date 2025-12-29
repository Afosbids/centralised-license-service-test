from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Brand Schemas
class BrandBase(BaseModel):
    name: str
    email: str

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str

class ProductCreate(ProductBase):
    brand_id: int

class Product(ProductBase):
    id: int
    brand_id: int
    
    class Config:
        from_attributes = True

# Customer Schemas
class CustomerBase(BaseModel):
    email: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    
    class Config:
        from_attributes = True

# License Schemas
class LicenseBase(BaseModel):
    customer_id: int
    product_id: int
    is_active: bool = True
    expiration_date: Optional[datetime] = None
    max_seats: int = 1
    active_seats: int = 0

class LicenseCreate(LicenseBase):
    key: Optional[str] = None

class License(LicenseBase):
    id: int
    key: str
    created_at: datetime
    activations: List['Activation'] = []
    
    class Config:
        from_attributes = True

class LicenseValidate(BaseModel):
    key: str
    product_id: int
    machine_id: Optional[str] = None # US3: Device ID

# Activation Schemas
class ActivationBase(BaseModel):
    machine_id: str
    friendly_name: Optional[str] = None

class ActivationCreate(ActivationBase):
    license_key: str

class Activation(ActivationBase):
    id: int
    license_id: int
    activated_at: datetime
    
    class Config:
        from_attributes = True

# Rebuild License model to resolve forward reference
License.model_rebuild()
