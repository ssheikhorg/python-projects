from datetime import datetime
from fastapi import APIRouter, status, HTTPException

from . import schema
from ...settings import config
from . import models

from . import customers, method, invoices, subscribe


billing_router = APIRouter()


@billing_router.post("/invoice", status_code=status.HTTP_201_CREATED)
async def create_invoices(body: schema.CreateInvoiceSchema):
    """
    Create a new billings with the given body.
    - :param [optional] **body.stripe_customer_id**: str -> for customers recurring payment we can use this id
    - :param [required] **body.items**: list -> list of items from cart, the list of foods customer wants to buy
    - :param [required] **body.customer**: dict -> required for new customer, all the details of customer are optional
    - :param [required] **body.payment_method**: dict -> required for new account, it will be added as default PM
    - :param [required] **body.billings**: dict -> it will create a new billings for the customer
    """
    try:
        c_body = await models.retrieve_customer(body.stripe_customer_id)
        if c_body is not None:
            customer = customers.retrieve(c_body["stripe_customer_id"])

            cards = await models.retrieve_payment_method(customer["id"])
            for pm in cards:
                if not (
                    body.payment_method.card.expiry_month == pm["card"]["exp_month"]
                    and body.payment_method.card.expiry_year == pm["card"]["exp_year"]
                    and body.payment_method.card.card_number[-4:] == pm["card"]["last4"]
                ):

                    pm = method.create_pm(
                        type=body.payment_method.type,
                        card={
                            "number": body.payment_method.card.card_number,
                            "exp_month": body.payment_method.card.expiry_month,
                            "exp_year": body.payment_method.card.expiry_year,
                            "cvc": body.payment_method.card.cvc,
                        },
                        customer_id=customer["id"],
                    )

                    """insert new card details to database"""
                    payment_method = await models.create_payment_method(
                        created_date=pm["created"],
                        address=pm["billing_details"]["address"],
                        card_number=pm["card"]["last4"],
                        expiry_month=pm["card"]["exp_month"],
                        expiry_year=pm["card"]["exp_year"],
                        payment_method_id=pm["id"],
                        cust_id=customer["id"],
                        card_holder_name=pm["billing_details"]["name"],
                        card_type=pm["type"],
                    )

                    """creates billings items from cart from billings items function"""
                    invoices.line_items(customer["id"], body.items)

                    """creates invoices with customer, card and items bodys"""
                    invoice = invoices.create(
                        customer=customer["id"],
                        auto_advance=body.invoice.auto_advance,
                        collection_method=body.invoice.collection_method,
                        description=body.invoice.description,
                    )

                    """pay billings payments from attached default payment method"""
                    invoices.pay(invoice["id"])

                    context = {"payment_method": payment_method, "billings": invoice}
                    return models.response_model(context, status.HTTP_201_CREATED)
                else:
                    """creates billings items from cart from billings items function"""
                    invoices.line_items(customer["id"], body.items)

                    """creates invoices with customer, card and items bodys"""
                    invoice = invoices.create(
                        customer=customer["id"],
                        auto_advance=body.invoice.auto_advance,
                        collection_method=body.invoice.collection_method,
                        description=body.invoice.description,
                    )

                    """pay billings payments from attached default payment method"""
                    invoices.pay(invoice["id"])

                    context = {"billings": invoice}
                    return models.response_model(context, status.HTTP_201_CREATED)
        else:
            """creates customer and payment method"""
            customer = customers.create(
                name=body.customer.name,
                email=body.customer.email,
                phone=body.customer.phone,
                description=body.customer.description,
                address={
                    "line1": body.customer.address.line1,
                    "line2": body.customer.address.line2,
                    "postal_code": body.customer.address.postal_code,
                    "city": body.customer.address.city,
                    "state": body.customer.address.state,
                    "country": body.customer.address.country,
                },
            )
            pm = method.create_pm(
                type=body.payment_method.type,
                card={
                    "number": body.payment_method.card.card_number,
                    "exp_month": body.payment_method.card.expiry_month,
                    "exp_year": body.payment_method.card.expiry_year,
                    "cvc": body.payment_method.card.cvc,
                },
                customer_id=customer["id"],
            )

            """insert customer details to bodybase"""
            new_customer = await models.create_customer(
                created_date=datetime.now(),
                name=customer["name"],
                email=customer["email"],
                phone=customer["phone"],
                stripe_customer_id=customer["id"],
                address=customer["address"],
            )

            """insert new card details to bodybase"""
            payment_method = await models.create_payment_method(
                created_date=pm["created"],
                address=pm["billing_details"]["address"],
                card_number=pm["card"]["last4"],
                expiry_month=pm["card"]["exp_month"],
                expiry_year=pm["card"]["exp_year"],
                payment_method_id=pm["id"],
                cust_id=customer["id"],
                card_holder_name=pm["billing_details"]["name"],
                card_type=pm["type"],
            )

            """creates billings items from cart from billings items function"""
            invoices.line_items(customer["id"], body.items)

            """creates invoices with customer, card and items bodys"""
            invoice = invoices.create(
                customer=customer["id"],
                auto_advance=body.invoice.auto_advance,
                collection_method=body.invoice.collection_method,
                description=body.invoice.description,
            )

            """pay billings payments from attached default payment method"""
            invoices.pay(invoice["id"])

            """insert billings details to bodybase"""
            invoice_details = await models.create_invoice(
                created_date=datetime.now(),
                collection_method=invoice["collection_method"],
                amount_due=invoice["amount_due"],
                amount_paid=invoice["amount_paid"],
                amount_remaining=invoice["amount_remaining"],
                total=invoice["total"],
                currency=invoice["currency"],
                invoice_id=invoice["id"],
                customer_id=customer["id"],
                description=invoice["description"],
                customer_name=customer["name"],
                customer_email=customer["email"],
                customer_phone=customer["phone"],
                customer_address=customer["address"],
            )
            context = {
                "billings": invoice_details,
                "customer": new_customer,
                "payment_method": payment_method,
                "message": "Invoice, Customer, Payment method has been created successfully",
            }

            return models.response_model(context, status.HTTP_201_CREATED)

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Error creating customer and payment method"},
        )


@billing_router.post("/subscribe/")
async def billing_subscription(body: schema.BillingSubscribeRequest):
    """
    Create a new billings with the given body.
    - :param [optional] **body.stripe_customer_id**: str -> for customers recurring payment we can use this id
    - :param [required] **body.items**: list -> list of prices from the products
    - :param [required] **body.customer**: dict -> required for new customer, all the details of customer are optional
    - :param [required] **body.payment_method**: dict -> required for new account, it will be added as default PM
    - :param [required] **body.billings**: dict -> it will create a new billings for the customer
    """
    try:
        customer = customers.create(
            name=body.customer.name,
            email=body.customer.email,
            phone=body.customer.phone,
            description=body.customer.description,
            address={
                "line1": body.customer.address.line1,
                "line2": body.customer.address.line2,
                "postal_code": body.customer.address.postal_code,
                "city": body.customer.address.city,
                "state": body.customer.address.state,
                "country": body.customer.address.country,
            },
        )
        pm = method.create_pm(
            type=body.payment_method.type,
            card={
                "number": body.payment_method.card.card_number,
                "exp_month": body.payment_method.card.expiry_month,
                "exp_year": body.payment_method.card.expiry_year,
                "cvc": body.payment_method.card.cvc,
            },
            customer_id=customer["id"],
        )

        subscription = subscribe.create(
            customer_id=customer["id"],
            items=[
                {
                    "price": config.settings.stripe_price_basic,
                }
            ],
            collection_method="charge_automatically",
            default_payment_method=pm["id"],
        )

        return subscription
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Error creating subscription, customer and payment method"},
        )
