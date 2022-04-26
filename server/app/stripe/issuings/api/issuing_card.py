from fastapi import HTTPException, status
import stripe
from fastapi.encoders import jsonable_encoder

from ....settings import config

stripe.api_key = config.settings.stripe_secret_key


def create_issuing_card(**kwargs):
    """create issuing card virtual/physical for a customer"""
    try:
        data = jsonable_encoder(kwargs)
        if data["type"] == "virtual":
            card = stripe.issuing.Card.create(
                cardholder=data["card_holder_id"],
                currency=data["currency"],
                type=data["type"],
                status=data["status"],
                spending_controls={
                    "spending_limits": [data["spending_limits"]],
                },
            )
        elif data["type"] == "physical":
            card = stripe.issuing.Card.create(
                cardholder=data["card_holder_id"],
                currency=data["currency"],
                type=data["type"],
                status=data["status"],
                shipping=data["shipping"],
                spending_controls={
                    "spending_limits": [data["spending_limits"]],
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid card type.",
            )
        return card

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card creation failed",
        )


def activate_card(**kwargs):
    """activate a card"""
    try:
        update_card = stripe.issuing.Card.modify(
            kwargs["card_id"], status=kwargs["status"]
        )
        return update_card
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card activation failed",
        )
