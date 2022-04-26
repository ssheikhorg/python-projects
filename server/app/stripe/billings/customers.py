from fastapi import HTTPException, status

from ...settings.config import stripe


def create(**kwargs):
    """create a stripe customer"""
    try:
        context = stripe.Customer.create(
            name=kwargs["name"],
            email=kwargs["email"],
            phone=kwargs["phone"],
            description=kwargs["description"],
            address=kwargs["address"],
        )
        return context
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer creation failed",
        )


def modify(customer_id, method):
    """modify the customer object to add the payment method"""
    try:
        context = stripe.Customer.modify(
            customer_id, invoice_settings={"default_payment_method": method}
        )
        return context
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer modification failed",
        )


def retrieve(customer_id):
    """retrieve a stripe customer"""
    try:
        context = stripe.Customer.retrieve(customer_id)
        return context
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer retrieval failed",
        )


def delete(customer_id):
    """delete a stripe customer"""
    try:
        context = stripe.Customer.delete(customer_id)
        return context
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer deletion failed",
        )
