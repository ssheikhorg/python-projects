from enum import Enum

from pydantic import BaseModel, EmailStr
from . import card_schema


class CardHolderType(str, Enum):
    individual = "individual"
    company = "company"


class CardHolderCreate(BaseModel):
    type: CardHolderType = CardHolderType.individual
    name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    spending_limits: card_schema.SpendingLimit | None = None
    address: card_schema.Address | None

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "type": "individual",
                "name": "John Doe",
                "email": "doe@mail.com",
                "phone_number": "+441632960982",
                "spending_limits": {
                    "amount": 6000,
                    "interval": "weekly",
                    "categories": ["fast_food_restaurants"],
                },
                "address": {
                    "line1": "790",
                    "line2": "Keyford",
                    "postal_code": "BA11 1JF",
                    "city": "Frome",
                    "state": "Somerset",
                    "country": "GB",
                },
            }
        }
