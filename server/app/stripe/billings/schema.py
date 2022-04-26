from pydantic import BaseModel, EmailStr


class LineItem(BaseModel):
    description: str | None = None
    unit_amount: int | None = None
    quantity: int | None = None
    currency: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "description": "Sea Food",
                "currency": "gbp",
                "unit_amount": 1000,
                "quantity": 1
            }
        }


class Address(BaseModel):
    line1: str | None = None
    line2: str | None = None
    postal_code: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "line1": "790",
                "line2": "Keyford",
                "postal_code": "BA11 1JF",
                "city": "Frome",
                "state": "Somerset",
                "country": "GB"
            }
        }


class Card(BaseModel):
    card_number: str | None = None
    expiry_month: int | None = None
    expiry_year: int | None = None
    cvc: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "card_number": "4242424242424242",
                "expiry_month": 3,
                "expiry_year": 2023,
                "cvc": "123"
            }
        }


class PaymentMethod(BaseModel):
    type: str | None = None
    card: Card | None = None

    class Config:
        schema_extra = {
            "example": {
                "type": "card",
                "card": {
                    "card_number": "371449635398431",
                    "expiry_month": 3,
                    "expiry_year": 2023,
                    "cvc": "314"
                }
            }
        }


class Customer(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    description: str | None = None
    address: Address | None = None

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "doe@mail.com",
                "phone": "+44020744440000",
                "address": {
                    "line1": "790",
                    "line2": "Keyford",
                    "postal_code": "BA11 1JF",
                    "city": "Frome",
                    "state": "Somerset",
                    "country": "GB"
                },
                "description": "Order Description",
            }
        }


class Invoice(BaseModel):
    auto_advance: bool | None = True
    collection_method: str | None = "charge_automatically"
    description: str | None = "Memo"


class CreateInvoiceSchema(BaseModel):
    stripe_customer_id: str | None = None
    items: list[LineItem]
    customer: Customer | None = None
    payment_method: PaymentMethod | None = None
    invoice: Invoice | None = None


class BillingSubscribeRequest(BaseModel):
    stripe_customer_id: str | None = None
    customer: Customer | None = None
    payment_method: PaymentMethod | None = None
