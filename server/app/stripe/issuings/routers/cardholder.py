from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from ..api import card_holder
from .. import models
from ..schema import ch_schema

cardholder_router = APIRouter()


@cardholder_router.post("/create-cardholder/")
async def create_cardholder(body: ch_schema.CardHolderCreate):
    """create cardholder account"""
    try:
        ch = card_holder.create_cardholder(
            type=body.type,
            name=body.name,
            email=body.email,
            phone_number=body.phone_number,
            address=body.address,
            spending_limits=body.spending_limits,
        )
        cardholder = await models.create_cardholder(
            created_date=datetime.now(),
            type=ch["type"],
            name=ch["name"],
            email=ch["email"],
            phone=ch["phone_number"],
            card_holder_id=ch["id"],
            address=ch["billing"]["address"],
        )
        return {
            "cardholder": ch,
            "cardholder_db": cardholder,
            "message": "Cardholder created successfully",
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cardholder creation failed",
        )
