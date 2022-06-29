from datetime import datetime

from pydantic import BaseModel


class Supplier(BaseModel):
    supplierID: int
    companyName: str
    contactName: str = None
    contactTitle: str = None
    phone: int = None
    fax: int = None
    homepage: str = None


class Order(BaseModel):
    orderID: int
    orderDate: datetime = datetime.now()
    requiredDate: datetime = None
    shippedDate: datetime = None
    shipVia: int = None
    freight: float = None


class Customer(BaseModel):
    customerID: str
    contactTitle: str = None
    contactName: str


class Product(BaseModel):
    productID: int
    productName: str
