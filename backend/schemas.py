from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import RoleEnum, PaymentMethodEnum, OrderStatusEnum, PaymentStatusEnum, DeliveryStatusEnum

class UserBase(BaseModel):
    username: str
    role: RoleEnum
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class GasCylinderBase(BaseModel):
    size_kg: float
    stock_quantity: int
    price: float

class GasCylinderCreate(GasCylinderBase):
    pass

class GasCylinder(GasCylinderBase):
    id: int
    station_id: int

    class Config:
        orm_mode = True

class StationBase(BaseModel):
    name: str
    logo_url: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    phone: Optional[str] = None
    city: str

class StationCreate(StationBase):
    pass

class Station(StationBase):
    id: int
    cylinders: List[GasCylinder] = []

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    station_id: int
    cylinder_id: int
    quantity: int
    customer_name: str
    customer_phone: str
    customer_town: Optional[str] = None
    customer_quarter: Optional[str] = None
    customer_address: Optional[str] = None
    payment_method: PaymentMethodEnum

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    payment_status: PaymentStatusEnum
    status: OrderStatusEnum
    validation_code: Optional[str] = None
    order_date: datetime

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    username: str
    role: str

class DeliveryBase(BaseModel):
    order_id: int
    delivery_person_id: int

class Delivery(DeliveryBase):
    id: int
    status: DeliveryStatusEnum
    
    class Config:
        orm_mode = True

class OrderWithDetails(Order):
    station: Station
    cylinder: GasCylinder
    delivery: Optional[Delivery] = None

