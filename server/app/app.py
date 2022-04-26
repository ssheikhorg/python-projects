from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .stripe.billings.routers import billing_router
from .stripe.issuings.routers import card, cardholder
from .yolauncher.routers import router as yo_launcher_router


app = FastAPI()


"""Stripe invoice routers"""
app.include_router(billing_router, tags=["Stripe-Billings"], prefix="/v1")

"""Stripe issuing card routers"""
app.include_router(
    cardholder.cardholder_router,
    tags=["Issuing Virtual/Physical Card"],
    prefix="/v1",
)
app.include_router(
    card.card_router,
    tags=["Issuing Virtual/Physical Card"],
    prefix="/v1",
)


"""Yo Launcher App Routers"""
app.mount(
    "/yo-launcher-apk",
    StaticFiles(directory="server/app/yolauncher/launcherfiles", check_dir=False),
    name="launcherfiles",
)
app.include_router(yo_launcher_router, tags=["YoLauncher"], prefix="/launcher")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this YoLauncher/Stripe Invoice App!"}
