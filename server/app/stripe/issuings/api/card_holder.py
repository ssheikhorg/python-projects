import stripe
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from ....settings import config

stripe.api_key = config.settings.stripe_secret_key


def create_cardholder(**kwargs):
    """create cardholder account"""
    try:
        data = jsonable_encoder(kwargs)
        cardholder = stripe.issuing.Cardholder.create(
            type=data["type"],
            name=data["name"],
            email=data["email"],
            phone_number=data["phone_number"],
            spending_controls={
                    "spending_limits": [data["spending_limits"]],
                },
            billing={
                "address": data["address"],
            },
        )
        return cardholder
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cardholder not created")


def update_cardholder(**kwargs):
    """update cardholder account"""
    try:
        data = jsonable_encoder(kwargs)
        cardholder = stripe.issuing.Cardholder.retrieve(data["id"])
        cardholder.name = data["name"]
        cardholder.email = data["email"]
        cardholder.phone_number = data["phone_number"]
        cardholder.spending_controls = {
            "spending_limits": [data["spending_limits"]],
        }
        cardholder.billing = {
            "address": data["address"],
        }
        cardholder.save()
        return cardholder
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cardholder not updated")
