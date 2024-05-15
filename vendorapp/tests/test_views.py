from rest_framework.test import APITestCase, APIClient
from vendorapp.models import Vendor, PurchaseOrder, HistoricalPerformance,MyUser
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from rest_framework import status
from django.contrib.auth import get_user_model
import datetime

class RegisterViewTest(APITestCase):

    def setUp(self):
        self.url=reverse('register')
        self.data={
            'username':'admin',
            'password':'admin',
            'email':'someone@gmail.com'
        }
    def test_register_view_success(self):
        response=self.client.post(self.url,self.data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['msg'],"User created successfully")
    
    def test_register_view_duplicate_username(self):
        response=self.client.post(self.url,self.data,format='json')

        response1=self.client.post(self.url,self.data,format='json')
        self.assertEqual(response1.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response1.data['error'],'Username already exists!')

class LoginViewTest(APITestCase):
    def setUp(self):
        self.url=reverse('login')
        self.data={
            'username':'admin',
            'password':'admin',
            'email':'someone@gmail.com'
        }
        self.client.post(reverse('register'),self.data,format='json')

    def test_login_view_success(self):
        self.data.pop('email')
        response=self.client.post(self.url,self.data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        user=Token.objects.get(user=MyUser.objects.get(username='admin'))
        self.assertEquals(response.data['token'],str(user))
    
    def test_login_view_wrong_credentials(self):
        self.data['username']='not_a_username'
        response1=self.client.post(self.url,self.data,format='json')
        self.assertEqual(response1.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response1.data['error'],'Invalid credentials')

class VendorViewTest(APITestCase):
    def setUp(self):
        self.vendor_data={
            "name":"Vendor1",
            "contact_details":"Some number",
            "address":"Somewhere","vendor_code":"v1"
        }
        self.user=MyUser.objects.create(username="admin",password="admin",email="someone@gmail.com")
        self.token=str(Token.objects.create(user=self.user))
        self.headers={'Authorization':f'Token {self.token}'}
    
    def test_vendor_create_succcess(self):
        response=self.client.post(reverse('vendor'),self.vendor_data,headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['msg'],'Data created')
    
    def test_vendor_create_duplicate_vendorcode(self):
        VendorViewTest.test_vendor_create_succcess(self)
        response=self.client.post(reverse('vendor'),self.vendor_data,headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['vendor_code'][0]),'vendor with this vendor code already exists.')
        
    def test_vendor_get_all_success(self):
        VendorViewTest.test_vendor_create_succcess(self)
        response=self.client.get(reverse('vendor'),headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(str(response.data[0]['name']),"Vendor1")
        self.assertEqual(str(response.data[0]['vendor_code']),"v1")

    def test_vendor_get_some_success(self):
        VendorViewTest.test_vendor_create_succcess(self)
        response=self.client.get(reverse('vendor_some',args=[1]),headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(str(response.data['name']),"Vendor1")
        self.assertEqual(str(response.data['vendor_code']),"v1")
    
    def test_vendor_get_some_wrong_id(self):
        response=self.client.get(reverse('vendor_some',args=[1]),headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['error']),"Provided ID is invalid")

    def test_vendor_put_success(self):
        VendorViewTest.test_vendor_create_succcess(self)
        self.vendor_data["name"]="Ven1"
        self.vendor_data["contact_details"]="Some changed Number"
        response=self.client.put(reverse('vendor_some',args=[1]),self.vendor_data,headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['msg'],'Complete data updated')

    def test_vendor_put_duplicate_vendorcode(self):

        #Creating a new vendor
        VendorViewTest.test_vendor_create_succcess(self)

        #Creating another vendor
        self.vendor_data["name"]="Vendor2"
        self.vendor_data["contact_details"]="Some changed Number"
        self.vendor_data["vendor_code"]="v2"
        VendorViewTest.test_vendor_create_succcess(self)

        #Changing values for put, but giving vendor_code v2 which is already used by Vendor2
        self.vendor_data["name"]="Ven1"
        self.vendor_data["contact_details"]="Some changed Number"
        self.vendor_data["vendor_code"]="v2"

        #Updating that changed data to Vendor1, but the code is already used by Vendor2
        response=self.client.put(reverse('vendor_some',args=[1]),self.vendor_data,headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['vendor_code'][0],'vendor with this vendor code already exists.')
    
    def test_vendor_put_wrong_ID(self):
        response=self.client.put(reverse('vendor_some',args=[1]),self.vendor_data,headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'],'Provided ID is invalid')

    def test_vendor_delete_success(self):
        VendorViewTest.test_vendor_create_succcess(self)    
        response=self.client.delete(reverse('vendor_some',args=[1]),self.vendor_data,headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['msg'],'Data deleted')

class PurchaseOrderTest(APITestCase):
    def setUp(self):
        self.vendor1=Vendor.objects.create(name="Vendor1",contact_details="Some number",address="Somewhere",vendor_code="v1")
        self.po_data={
        "po_number": "p1",
        "order_date": "2024-05-09 17:16:52.734505",
        "delivery_date": "2024-05-14 17:18:52.158786",
        "items": {
            "SHIRT": 1
        },
        "quantity": 4,
        "vendor": self.vendor1.pk
            }
        self.user=MyUser.objects.create(username="admin",password="admin",email="someone@gmail.com")
        self.token=str(Token.objects.create(user=self.user))
        self.headers={'Authorization':f'Token {self.token}'}
    
    def test_purchase_order_create_success(self):
        response=self.client.post(reverse('purchase_order'),self.po_data,headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['msg'],'Data created')
    
    def test_purchase_create_duplicate_ponumber(self):
        PurchaseOrderTest.test_purchase_order_create_success(self)
        response=self.client.post(reverse('purchase_order'),self.po_data,headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['po_number'][0]),'purchase order with this po number already exists.')
    
    def test_purchase_get_all_success(self):
        PurchaseOrderTest.test_purchase_order_create_success(self)
        response=self.client.get(reverse('purchase_order'),headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(str(response.data[0]['po_number']),"p1")
        self.assertEqual(response.data[0]['quantity'],4)
        self.assertEqual(response.data[0]['acknowledgment_date'],None)
    
    def test_purchase_get_some_success(self):
        PurchaseOrderTest.test_purchase_order_create_success(self)
        response=self.client.get(reverse('purchase_order_some',args=[1]),headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(str(response.data['po_number']),"p1")
        self.assertEqual(response.data['quantity'],4)
    
    def test_purchase_get_some_wrong_id(self):
        response=self.client.get(reverse('purchase_order_some',args=[1]),headers=self.headers)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['error']),"Provided ID is invalid")
    
    def test_purchase_put_success(self):
        PurchaseOrderTest.test_purchase_order_create_success(self)
        self.po_data["po_number"]="p2"
        self.po_data["quantity"]=5
        response=self.client.put(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['msg'],'Complete data updated')

    def test_purchase_put_duplicate_ponumber(self):

        #Creating a new vendor
        PurchaseOrderTest.test_purchase_order_create_success(self)

        #Creating another vendor
        self.po_data["po_number"]="p2"
        self.po_data["quantity"]=5
        PurchaseOrderTest.test_purchase_order_create_success(self)

        #Changing values for put, but giving vendor_code v2 which is already used by Vendor2
        self.po_data["po_number"]="p2"
        self.po_data["quantity"]=7

        #Updating that changed data to Vendor1, but the code is already used by Vendor2
        response=self.client.put(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['po_number'][0]),'purchase order with this po number already exists.')

    def test_purchase_put_wrong_ID(self):
        response=self.client.put(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'],'Provided ID is invalid')

    def test_purchase_delete_success(self):
        PurchaseOrderTest.test_purchase_order_create_success(self)    
        response=self.client.delete(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['msg'],'Data deleted')

    def test_purchase_order_acknowledge_success(self):
        PurchaseOrderTest.test_purchase_order_create_success(self)    
        response=self.client.post(reverse('acknowledge',args=[1]),headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['msg'],'Purchase has been acknowledged!')
    
    def test_purchase_order_acknowledge_wrongID(self):    
        response=self.client.post(reverse('acknowledge',args=[1]),headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'],'Provided ID is invalid')
    
    def test_purchase_order_acknowledge_already_acknowledged(self):    
        PurchaseOrderTest.test_purchase_order_create_success(self)  
        response1=self.client.post(reverse('acknowledge',args=[1]),headers=self.headers,format="json")
        response=self.client.post(reverse('acknowledge',args=[1]),headers=self.headers,format="json")
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['msg'],'The purchase was already acknowledged!')

class PerformanceTest(APITestCase):
    def setUp(self):
        self.vendor1=Vendor.objects.create(name="Vendor1",contact_details="Some number",address="Somewhere",vendor_code="v1")
        self.po_data={
        "po_number": "p1",
        "order_date": "2024-05-09 17:16:52.734505",
        "delivery_date": "2024-05-14 17:16:52.734505",
        "issue_date": "2024-05-09 17:16:52.734505",
        "items": {
            "SHIRT": 1
        },
        "quantity": 4,
        "vendor": self.vendor1
            }
        self.user=MyUser.objects.create(username="admin",password="admin",email="someone@gmail.com")
        self.token=str(Token.objects.create(user=self.user))
        self.headers={'Authorization':f'Token {self.token}'}
        self.po=PurchaseOrder.objects.create(**self.po_data)

    def test_average_response_time(self):
        acknowledge_data={"acknowledgment_date":"2024-05-12 17:16:52.734505"}
        self.client.post(reverse('acknowledge',args=[1]),acknowledge_data,headers=self.headers,format="json")
        vendor=Vendor.objects.get(pk=1)
        acknowledgment_date = datetime.datetime.strptime(acknowledge_data["acknowledgment_date"],"%Y-%m-%d %H:%M:%S.%f")
        issue_date = datetime.datetime.strptime(self.po_data["issue_date"],"%Y-%m-%d %H:%M:%S.%f")
        
        self.assertEqual(round((acknowledgment_date-issue_date).total_seconds(), 2),vendor.average_response_time)

    def test_on_time_delivery_ratio(self):
        acknowledge_data={"acknowledgment_date":"2024-05-12 17:16:52.734505"}
        self.client.post(reverse('acknowledge',args=[1]),acknowledge_data,headers=self.headers,format="json")
        
        self.po_data["status"]="completed"
        self.po_data["vendor"]=self.vendor1.pk
        self.client.put(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")
        vendor=Vendor.objects.get(pk=1)

        self.assertEqual(vendor.on_time_delivery_rate,1.0)

    def test_quality_rating_average(self):
        acknowledge_data={"acknowledgment_date":"2024-05-12 17:16:52.734505"}
        self.client.post(reverse('acknowledge',args=[1]),acknowledge_data,headers=self.headers,format="json")
        
        self.po_data["status"]="completed"
        self.po_data["vendor"]=self.vendor1.pk
        self.po_data["quality_rating"]=5
        self.client.put(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")
        vendor=Vendor.objects.get(pk=1)

        self.assertEqual(vendor.quality_rating_avg,5.0)

    def test_fulfilment_ratio(self):
        acknowledge_data={"acknowledgment_date":"2024-05-12 17:16:52.734505"}
        self.client.post(reverse('acknowledge',args=[1]),acknowledge_data,headers=self.headers,format="json")
        
        self.po_data["status"]="completed"
        self.po_data["vendor"]=self.vendor1.pk
        self.po_data["quality_rating"]=5
        self.client.put(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")
        vendor=Vendor.objects.get(pk=1)

        self.assertEqual(vendor.fulfillment_rate,1.0)

    def test_get_all_performance_metrics_success(self):
        acknowledge_data={"acknowledgment_date":"2024-05-12 17:16:52.734505"}
        self.client.post(reverse('acknowledge',args=[1]),acknowledge_data,headers=self.headers,format="json")
        
        self.po_data["status"]="completed"
        self.po_data["vendor"]=self.vendor1.pk
        self.po_data["quality_rating"]=5
        self.client.put(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")


        response=self.client.get(reverse('performance',args=[1]),headers=self.headers,format="json")

        self.assertEqual(response.data[0]['vendor'],1)
        self.assertEqual(response.data[0]['on_time_delivery_rate'],1.0)
        self.assertEqual(response.data[0]['quality_rating_avg'],5.0)
        self.assertEqual(response.data[0]['average_response_time'],259200.0)
        self.assertEqual(response.data[0]['fulfillment_rate'],1.0)

    def test_get_all_performance_metrics_wrongID(self):
        acknowledge_data={"acknowledgment_date":"2024-05-12 17:16:52.734505"}
        self.client.post(reverse('acknowledge',args=[1]),acknowledge_data,headers=self.headers,format="json")
        
        self.po_data["status"]="completed"
        self.po_data["vendor"]=self.vendor1.pk
        self.po_data["quality_rating"]=5
        self.client.put(reverse('purchase_order_some',args=[1]),self.po_data,headers=self.headers,format="json")


        response=self.client.get(reverse('performance',args=[2]),headers=self.headers,format="json")

        self.assertEqual(response.data['error'],'Provided ID is invalid')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    