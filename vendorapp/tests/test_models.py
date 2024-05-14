from django.test import TestCase
from vendorapp.models import Vendor, PurchaseOrder, HistoricalPerformance, MyUser
from django.contrib.auth import authenticate

class UserTest(TestCase):
    def test_create_user(self):
        username="admin"
        password="admin"
        email="someone@gmail.com"

        user=MyUser.objects.create(username=username,password=password,email=email)

        self.assertEqual(user.email,email)
        self.assertEqual(user.username,username)
        self.assertEqual(user.password,password)

        check_user=MyUser.objects.get(username=username,password=password)
        self.assertEqual(user,check_user)

class VendorTest(TestCase):

    def setUp(self):
        self.vendor=Vendor.objects.create(name="Vendor1",contact_details="Some number",address="Somewhere",vendor_code="V1")
        self.id=self.vendor.id
    
    def test_model_data(self):
        self.assertEqual(
            str(self.vendor),
            self.vendor.name
        )
    
    def test_calculate_average_response_time(self):
        self.assertEqual(
            self.vendor.calculate_average_response_time(),0
        )
    
    #Same can be done for all other methods of Vendor. However all data will be '0' so negleting other functions here.

class Purchase_OrderTest(TestCase):
    def setUp(self):
        self.vendor=Vendor.objects.create(name="Vendor1",contact_details="Some number",address="Somewhere",vendor_code="V1")
        po_data={
        "po_number": "p1",
        "order_date": "2024-05-09 17:16:52.734505",
        "delivery_date": "2024-05-14 17:18:52.158786",
        "items": {
            "SHIRT": 1
        },
        "quantity": 4,
        "vendor": self.vendor
            }
        self.purchase=PurchaseOrder.objects.create(**po_data)

    def test_purchase_data(self):
        self.assertEqual(
            str(self.purchase),
            "Vendor1:p1"
        )
        self.assertEqual(
            self.purchase.quantity,
            4
        )

class HistoricalTest(TestCase):
    def setUp(self):
        self.vendor=Vendor.objects.create(name="Vendor1",contact_details="Some number",address="Somewhere",vendor_code="V1")
        po_data={
        "po_number": "p1",
        "order_date": "2024-05-09 17:16:52.734505",
        "delivery_date": "2024-05-14 17:18:52.158786",
        "items": {
            "SHIRT": 1
        },
        "quantity": 4,
        "vendor": self.vendor
            }
        self.purchase=PurchaseOrder.objects.create(**po_data)
        history_data=    {
        "date": "2024-05-10T02:52:38.465231Z",
        "on_time_delivery_rate": 1,
        "quality_rating_avg": 4,
        "average_response_time": -0.4,
        "fulfillment_rate": 1,
        "vendor": self.vendor
    }
        self.historical=HistoricalPerformance.objects.create(**history_data)

    def test_historical_data(self):
        self.assertEqual(
            str(self.historical),
            "Vendor1:2024-05-10T02:52:38.465231Z"
        )
        self.assertEqual(
            self.historical.quality_rating_avg,
            4
        )
        self.assertEqual(
            self.historical.average_response_time,
            -0.4
        )