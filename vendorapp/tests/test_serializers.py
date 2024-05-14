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