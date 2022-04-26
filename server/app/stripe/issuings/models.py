from ...database import db


def cardholder_serializer(cardholder) -> dict:
    """serialize a cardholder"""
    return {
        "id": str(cardholder["_id"]),
        "created_date": str(cardholder["created_date"]),
        "type": cardholder["type"],
        "name": cardholder["name"],
        "email": cardholder["email"],
        "phone": cardholder["phone"],
        "card_holder_id": cardholder["card_holder_id"],
        "address": cardholder["address"],
    }


def issuing_card_serializer(issued_card) -> dict:
    """serialize a issued_card"""
    return {
        "id": str(issued_card["_id"]),
        "created_date": str(issued_card["created_date"]),
        "issued_card_id": issued_card["issued_card_id"],
        "card_holder_id": issued_card["card_holder_id"],
        "card_type": issued_card["card_type"],
        "currency": issued_card["currency"],
        "status": issued_card["status"],
        "shipping": issued_card["shipping"],
    }


async def create_cardholder(**kwargs):
    """add a new billings to database"""
    cardholder = await db.cardholder_collection.insert_one(kwargs)
    new_cardholder = await db.cardholder_collection.find_one(
        {"_id": cardholder.inserted_id}
    )
    context = cardholder_serializer(new_cardholder)
    return context


async def retrieve_cardholder(data: str) -> dict:
    """retrieve a cardholder from database with an ID"""
    cardholder = await db.cardholder_collection.find_one(
        {
            "card_holder_id": data,
        }
    )
    if cardholder:
        return cardholder_serializer(cardholder)


async def create_card_issuing(**data: dict) -> dict:
    """add a new card to a cardholder"""
    issued_card = await db.card_issuing_collection.insert_one(data)
    new_issued_card = await db.card_issuing_collection.find_one(
        {"_id": issued_card.inserted_id}
    )
    context = issuing_card_serializer(new_issued_card)
    return context


async def retrieve_issued_card(data: str) -> dict:
    """retrieve a issued card from database with an ID"""
    issued_card = await db.cardholder_collection.find_one(
        {"issued_card_id": data},
    )
    if issued_card:
        return cardholder_serializer(issued_card)


async def update_card_issuing(**data: dict) -> dict:
    """update an issued card from database with an ID"""
    await db.card_issuing_collection.update_one(
        {"issued_card_id": data["card_id"]},
        {
            "$set": {"status": data["status"]},
        },
    )
    return {"message": "Card updated successfully"}
