from django.test import TestCase
from vendorapp.models import Vendor, PurchaseOrder, HistoricalPerformance
from vendorapp.serializers import VendorSerializer, HistoricalPerformanceSerializer, PurchaseOrderSerializer

class VendorSerializerTestCase(TestCase):
    def setUp(self):
        self.vendor_data={
            "name":"Vendor1",
            "contact_details":"Some number",
            "address":"Somewhere","vendor_code":"v1"
        }
    
    def test_vendor_serializer(self):
        serializer=VendorSerializer(self.vendor_data)
        data=serializer.data
        self.assertEqual(data["name"],"Vendor1")
        self.assertEqual(data["vendor_code"],"v1")
    
    def test_vendor_serializer_duplicate_vendorcode_data(self):
        Vendor.objects.create(**self.vendor_data)
        wrong_data={
            "name":"Vendor1",
            "contact_details":"Some number",
            "address":"Somewhere","vendor_code":"v1"
        }
        serializer1=VendorSerializer(data=wrong_data)

        self.assertFalse(serializer1.is_valid())
        self.assertEqual(str(serializer1.errors['vendor_code'][0]),"vendor with this vendor code already exists.")

class PurchaseSerializerTestCase(TestCase):
    def setUp(self):
        self.vendor2=Vendor.objects.create(name="Vendor2",contact_details="Some number",address="Somewhere",vendor_code="v2")
        self.po_data={
        "po_number": "p1",
        "order_date": "2024-05-09 17:16:52.734505",
        "delivery_date": "2024-05-14 17:18:52.158786",
        "items": {
            "SHIRT": 1
        },
        "quantity": 4,
        "vendor": self.vendor2.pk
            }
    
    def test_purchase_data(self):
        serializer=PurchaseOrderSerializer(data=self.po_data,context={'request_type':'POST'})
        self.assertTrue(serializer.is_valid())
        data=serializer.data
        self.assertEqual(data["po_number"],"p1")
        self.assertEqual(data["vendor"],self.vendor2.pk)

    def test_purchase_serializer_duplicate_ponumber_data(self):
        self.po_data["vendor"]=self.vendor2
        PurchaseOrder.objects.create(**self.po_data)
        wrong_data={
        "po_number": "p1",
        "order_date": "2024-05-09 17:16:52.734505",
        "delivery_date": "2024-05-14 17:18:52.158786",
        "items": {
            "SHIRT": 1
        },
        "quantity": 4,
        "vendor": self.vendor2.pk
            }
        serializer2=PurchaseOrderSerializer(data=wrong_data,context={'request_type': "POST"})

        self.assertFalse(serializer2.is_valid())
        self.assertEqual(str(serializer2.errors['po_number'][0]),"purchase order with this po number already exists.")

class HistoricalSerializerTest(TestCase):

    def setUp(self):
        self.vendor3=Vendor.objects.create(name="Vendor3",contact_details="Some number",address="Somewhere",vendor_code="v3")
        self.h_data={
        "date": "2024-05-10T02:52:38.465231Z",
        "on_time_delivery_rate": 1,
        "quality_rating_avg": 4,
        "average_response_time": -0.4,
        "fulfillment_rate": 1,
        "vendor": self.vendor3.pk
            }

    def test_historical_serializer_data(self):
        serializer=HistoricalPerformanceSerializer(data=self.h_data)
        self.assertTrue(serializer.is_valid())
        data=serializer.data
        self.assertEqual(data["on_time_delivery_rate"],1.0)
        self.assertEqual(data["quality_rating_avg"],4)
        self.assertEqual(data["vendor"],self.vendor3.pk)
