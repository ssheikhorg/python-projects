from fastapi import HTTPException, status
from ...settings.config import stripe


def create(**kwargs):
    try:
        context = stripe.Invoice.create(
            customer=kwargs["customer"],
            auto_advance=kwargs["auto_advance"],
            collection_method=kwargs["collection_method"],
            description=kwargs["description"],
        )
        return context
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoices cannot be created for this customer",
        )


def pay(invoice_id):
    """pay an billings"""
    try:
        context = stripe.Invoice.pay(invoice_id)
        return context
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoices cannot be paid for this customer",
        )


def line_items(cust_id, data) -> list:
    """create a list of line items for an billings"""
    item_list = []
    for x in data:
        item_list.append(
            stripe.InvoiceItem.create(
                customer=cust_id,
                description=x.description,
                currency=x.currency,
                unit_amount=x.unit_amount,
                quantity=x.quantity,
            )
        )
    return item_list
