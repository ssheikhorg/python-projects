from enum import Enum

from pydantic import BaseModel


class Address(BaseModel):
    line1: str | None = None
    line2: str | None = None
    postal_code: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class CardStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    canceled = "canceled"


class CardType(str, Enum):
    virtual = "virtual"
    physical = "physical"


class ShippingService(str, Enum):
    standard = "standard"
    express = "express"
    priority = "priority"


class SpendingInterval(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"
    all_time = "all_time"
    per_authorization = "per_authorization"


class SpendingLimit(BaseModel):
    amount: int = None
    interval: SpendingInterval = SpendingInterval.weekly
    categories: list | None = None


class ShippingType(str, Enum):
    individual = "individual"
    bulk = "bulk"


# class ShippingStatus(str, Enum):
#     shipped = "shipped"
#     delivered = "delivered"
#     pending = "pending"
#     returned = "returned"
#     failure = "failure"
#     canceled = "canceled"


# class ShippingCarrier(str, Enum):
#     royal_mail = "royal_mail"
#     usps = "usps"
#     fedex = "fedex"
#     dhl = "dhl"


class Shipping(BaseModel):
    name: str | None = None
    service: ShippingService | None = ShippingService.standard
    type: ShippingType | None = ShippingType.individual
    address: Address | None = None

    # status: ShippingStatus | None = ShippingStatus.pending
    # carrier: ShippingCarrier | None = ShippingCarrier.royal_mail


class CardCreate(BaseModel):
    card_holder_id: str
    currency: str = "gbp"
    type: CardType = CardType.virtual
    status: CardStatus = CardStatus.inactive
    spending_limits: SpendingLimit
    shipping: Shipping | None = None

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "card_holder_id": "ich_1KqtdGJJwRD860NBzfgJeiCW",
                "currency": "gbp",
                "type": "physical",
                "status": "inactive",
                "spending_limits": {
                    "amount": 4000,
                    "interval": "weekly",
                    "categories": ["fast_food_restaurants"],
                },
                "shipping": {
                    "name": "Steve H",
                    "service": "standard",
                    "type": "individual",

                    # "status": "pending",
                    # "carrier": "royal_mail",

                    "address": {
                        "line1": "123 Main Street",
                        "line2": "Apt. 1",
                        "postal_code": "BA11 1JF",
                        "city": "Frome",
                        "state": "Somerset",
                        "country": "GB",
                    },
                },
            }
        }


class ActivateCard(BaseModel):
    card_id: str
    status: CardStatus = CardStatus.active

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "card_id": "ic_1Kq9ZNJJwRD860NB8bpjTfrf",
                "status": "active",
            }
        }
