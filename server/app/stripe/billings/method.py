from fastapi import HTTPException, status
from ...settings.config import stripe

from . import customers


def create_pm(**kwargs):
    """
    -----create a payment method-----
    retrieve_customer: retrieve customer from stripe
    source: create a source/card to customer stripe profile
    method: create a payment method to customer stripe account
    context: attach payment method to customer stripe account
    modify: modify customer account to make payment method default
    """
    try:
        retrieve_customer = customers.retrieve(kwargs["customer_id"])

        source = stripe.Token.create(
            card=kwargs['card'],
        )['id']

        method = stripe.PaymentMethod.create(
            type=kwargs['type'],
            card={"token": source},
            billing_details={
                "address": {
                    "line1": retrieve_customer["address"]["line1"],
                    "line2": retrieve_customer["address"]["line2"],
                    "postal_code": retrieve_customer["address"]["postal_code"],
                    "state": retrieve_customer["address"]["state"],
                    "city": retrieve_customer["address"]["city"],
                    "country": retrieve_customer["address"]["country"],
                },
                "email": retrieve_customer["email"],
                "name": retrieve_customer["name"],
                "phone": retrieve_customer["phone"],
            })['id']

        context = stripe.PaymentMethod.attach(
            method,
            customer=kwargs['customer_id']
        )
        customers.modify(
            customer_id=kwargs['customer_id'],
            method=method
        )
        return context
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Payment method not created")
