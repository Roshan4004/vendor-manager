from .models import Vendor, PurchaseOrder, HistoricalPerformance, MyUser
from .serializers import (
    VendorSerializer,
    PurchaseOrderSerializer,
    HistoricalPerformanceSerializer,
    MyUserSerializer
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
import datetime
from . import signals
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated


class VendorAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, format=None):
        id = pk
        if id is not None:
            if Vendor.objects.filter(id=id).first() is None:
                return Response('Provided ID is invalid', status.HTTP_400_BAD_REQUEST)
            serializer = VendorSerializer(Vendor.objects.get(id=id))
            return Response(serializer.data)
        ven = Vendor.objects.all()
        serializer = VendorSerializer(ven, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Data created'}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, format=None):
        id = pk
        if Vendor.objects.filter(id=id).first() is None:
            return Response('Provided ID is invalid', status.HTTP_400_BAD_REQUEST)
        serializer = VendorSerializer(Vendor.objects.get(id=id), data=request.data, context={'request_type': request.method, 'pk': pk})
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Complete data updated'}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, format=None):
        id = pk
        stu = Vendor.objects.get(pk=id)
        stu.delete()
        return Response({'msg': 'Data deleted'})


class PurchaseAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, format=None):
        id = pk
        if id is not None:
            if PurchaseOrder.objects.filter(id=id).first() is None:
                return Response('Provided ID is invalid', status.HTTP_400_BAD_REQUEST)
            serializer = PurchaseOrderSerializer(PurchaseOrder.objects.get(id=id))
            return Response(serializer.data)
        pur = PurchaseOrder.objects.all()
        serializer = PurchaseOrderSerializer(pur, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PurchaseOrderSerializer(data=request.data, context={'request_type': request.method})
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Data created'}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, format=None):
        id = pk
        if PurchaseOrder.objects.filter(id=id).first() is None:
            return Response('Provided ID is invalid', status.HTTP_400_BAD_REQUEST)
        serializer = PurchaseOrderSerializer(PurchaseOrder.objects.get(id=id), data=request.data, context={'request_type': request.method, 'pk': pk})
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Complete data updated'}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, format=None):
        id = pk
        stu = PurchaseOrder.objects.get(pk=id)
        stu.delete()
        return Response({'msg': 'Data deleted'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def acknowledge(request, pk=None):
    id = pk
    if PurchaseOrder.objects.filter(id=id).first() is None:
        return Response('Provided ID is invalid', status.HTTP_400_BAD_REQUEST)
    ac_date = request.POST.get('acknowledgment_date')
    if ac_date is None:
        ac_date = datetime.datetime.now()
    obj = PurchaseOrder.objects.filter(id=id).first()
    if obj.acknowledgment_date is not None:
        return Response({'msg': 'The purchase was already acknowledged!'}, status.HTTP_201_CREATED)
    else:
        obj.acknowledgment_date = ac_date
        obj.save(update_fields=['acknowledgment_date'])
        signals.order_acknowledgement_signal.send(sender=obj.__class__, instance=obj)
        return Response({'msg': 'Purchase has been acknowledged!'})


class HistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, format=None):
        id = pk
        if id is not None:
            if HistoricalPerformance.objects.filter(vendor=id).count() < 1:
                return Response('Provided ID is invalid', status.HTTP_400_BAD_REQUEST)
            serializer = HistoricalPerformanceSerializer(HistoricalPerformance.objects.filter(vendor=id), many=True)
            return Response(serializer.data)
        return Response({'msg': 'The provided ID is invalid, please check and try again.'}, status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        user = MyUser.objects.filter(username=request.data['username'], password=request.data['password']).first()
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


class RegistrationView(APIView):
    def post(self, request):
        serializer = MyUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'User created successfully'}, status.HTTP_201_CREATED)
        return Response({'error': 'Username already exists!'}, status=401)
