from rest_framework.test import APITestCase, APIClient
from vendorapp.models import Vendor, PurchaseOrder, HistoricalPerformance,MyUser
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from rest_framework import status
from django.contrib.auth import get_user_model

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
        self.model=Vendor
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
