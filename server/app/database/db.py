from ..settings.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient


"""stripe database credentials yo market"""
client = AsyncIOMotorClient(settings.stripe_db_url)
db = client[settings.stripe_db_name]
customer_collection = db.get_collection("shapon_test_billings_customer")
card_detail_collection = db.get_collection("shapon_test_billings_card")
invoice_collection = db.get_collection("shapon_test_billings_invoice")
subscribe_collection = db.get_collection("shapon_test_billings_subscribe")
cardholder_collection = db.get_collection("shapon_test_issuing_cardholder")
card_issuing_collection = db.get_collection("shapon_test_issuing_card")


"""yo_launcher database credentials"""
client = MongoClient(settings.yo_launcher_db_url)
launcher_db = client[settings.yo_launcher_db_name]
package_collection = launcher_db.yo_package
business_collection = launcher_db.yo_business
