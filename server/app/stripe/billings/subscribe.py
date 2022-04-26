from fastapi import HTTPException, status
from ...settings.config import stripe


def create(**kwargs):
    try:
        context = stripe.Subscription.create(
            customer=kwargs["customer_id"],
            items=kwargs["items"],
            collection_method=kwargs["collection_method"],
            default_payment_method=kwargs["default_payment_method"],
        )
        return context
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid request")
