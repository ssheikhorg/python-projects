from ...database import db


def new_card_serializer(card) -> dict:
    """serialize a card"""
    context = {
        "id": str(card["_id"]),
        "created_date": str(card["created_date"]),
        "card": {
            "last4": card["card_number"],
            "exp_month": card["expiry_month"],
            "exp_year": card["expiry_year"],
        },
        "address": card["address"],
        "payment_method_id": card["payment_method_id"],
        "cust_id": card["cust_id"],
        "card_holder_name": card["card_holder_name"],
        "card_type": card["card_type"],
    }
    return context


def customer_serializer(customer) -> dict:
    """serialize a customer"""
    context = {
        "id": str(customer["_id"]),
        "created_date": str(customer["created_date"]),
        "name": customer["name"],
        "email": customer["email"],
        "phone": customer["phone"],
        "stripe_customer_id": customer["stripe_customer_id"],
        "address": customer["address"],
    }
    return context


def invoice_serializer(data) -> dict:
    """serialize a customer"""
    context = {
        "id": str(data["_id"]),
        "created_date": str(data["created_date"]),
        "collection_method": data["collection_method"],
        "amount_due": data["amount_due"],
        "amount_paid": data["amount_paid"],
        "amount_remaining": data["amount_remaining"],
        "total": data["total"],
        "currency": data["currency"],
        "invoice_id": data["invoice_id"],
        "customer_id": data["customer_id"],
        "description": data["description"],
        "customer_name": data["customer_name"],
        "customer_email": data["customer_email"],
        "customer_phone": data["customer_phone"],
        "customer_address": data["customer_address"],
    }
    return context


async def create_invoice(**kwargs):
    """add a new billings to database"""
    invoice = await db.invoice_collection.insert_one(kwargs)
    new_invoice = await db.invoice_collection.find_one(
        {"_id": invoice.inserted_id},
    )
    context = invoice_serializer(new_invoice)
    return context


async def create_customer(**kwargs):
    """add a new customer to database"""
    customer = await db.customer_collection.insert_one(kwargs)
    new_customer = await db.customer_collection.find_one(
        {"_id": customer.inserted_id},
    )
    context = customer_serializer(new_customer)
    return context


async def retrieve_customer(data: str) -> dict:
    """retrieve a customer from database with a ID"""
    user = await db.customer_collection.find_one({"stripe_customer_id": data})
    if user:
        return customer_serializer(user)


async def retrieve_payment_method(data: str) -> list:
    """retrieve a customer from database with a ID"""
    cards = db.card_detail_collection.find({"cust_id": data})
    method = []
    async for card in cards:
        method.append(new_card_serializer(card))
    return method


async def create_payment_method(**kwargs):
    """create a new payment method to database"""
    card = await db.card_detail_collection.insert_one(kwargs)
    new_card = await db.card_detail_collection.find_one(
        {"_id": card.inserted_id},
    )
    method = new_card_serializer(new_card)
    return method


def response_model(data, code_status):
    return {"data": data, "code": code_status}


# async def create_subscribe(**kwargs):
#     """add a new customer to database"""
#     subscribe = await db.subscribe_collection.insert_one(kwargs)
#     new_subscribe = await db.subscribe_collection.find_one(
#         {"_id": subscribe.inserted_id}
#     )
#     context = subscribe_serializer(new_subscribe)
#     return context
