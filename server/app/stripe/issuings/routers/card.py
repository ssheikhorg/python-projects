from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from ..api import issuing_card
from .. import models
from ..schema import card_schema


card_router = APIRouter()


@card_router.post("/create-card/")
async def card_issuing(body: card_schema.CardCreate):
    """create issuing card virtual/physical for a customer"""
    try:
        c_holder = await models.retrieve_cardholder(body.card_holder_id)

        if body.type == "virtual":
            card = issuing_card.create_issuing_card(
                card_holder_id=body.card_holder_id,
                currency=body.currency,
                status=body.status,
                type=body.type,
                spending_limits=body.spending_limits,
            )
        elif body.type == "physical":
            card = issuing_card.create_issuing_card(
                card_holder_id=c_holder["card_holder_id"],
                currency=body.currency,
                type=body.type,
                status=body.status,
                shipping=body.shipping,
                spending_limits=body.spending_limits,
            )

        db_card = await models.create_card_issuing(
            created_date=datetime.now(),
            card_holder_id=c_holder["card_holder_id"],
            card_type=card["type"],
            currency=card["currency"],
            issued_card_id=card["id"],
            status=card["status"],
            shipping=card["shipping"],
        )
        return {"card": card, "card_db": db_card, "message": "Card issued successfully"}
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cardholder not created",
        )


@card_router.post("/activate-card/")
async def activate_card(body: card_schema.ActivateCard):
    """activate a card with status active"""
    try:
        card = issuing_card.activate_card(
            card_id=body.card_id,
            status=body.status,
        )
        update_card = await models.update_card_issuing(
            card_id=card["id"],
            status=card["status"],
        )
        return {
            "card": update_card,
            "message": "Card activated successfully",
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card activation failed",
        )
