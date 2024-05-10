from rest_framework import serializers
from vendorapp.models import Vendor, HistoricalPerformance, PurchaseOrder, MyUser
import datetime
from . import signals


class VendorSerializer(serializers.ModelSerializer):

    def validate(self, data):
        try:
            if self.context["request_type"] == 'PUT':
                if Vendor.objects.filter(vendor_code=data.get('vendor_code')).exclude(id=self.context["pk"]).first():
                    raise serializers.ValidationError("Vendor Code already exists!")
                return super().validate(data)
        except Exception:
            pass      
        if Vendor.objects.filter(vendor_code=data.get('vendor_code')).first():
            raise serializers.ValidationError("Vendor Code already exists!")
        return super().validate(data)        

    class Meta:
        model = Vendor
        fields = "__all__"
        extra_kwargs = {
            "name": {"error_messages": {"required": "The name of Vendor is required"}},
            "contact_details": {"error_messages": {"required": "Contact details of the vendor is required"}},
            "address": {"error_messages": {"required": "Address of vendor is required"}},
        }


class PurchaseOrderSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data.get('issue_date') is None:
            data['issue_date'] = datetime.datetime.now()
        if self.context["request_type"] == 'PUT':
            obj = PurchaseOrder.objects.filter(id=self.context["pk"]).first()
            if obj.status == "completed":
                raise serializers.ValidationError("You can't update a completed order!")
            if PurchaseOrder.objects.filter(po_number=data.get('po_number')).exclude(id=self.context["pk"]).first():
                raise serializers.ValidationError("Purchase Number already exists!")
            return super().validate(data)   
        else:
            if PurchaseOrder.objects.filter(po_number=data.get('po_number')).first():
                raise serializers.ValidationError("Purchase Number already exists!")
            return super().validate(data)
        
    class Meta:
        model = PurchaseOrder
        fields = "__all__"
        extra_kwargs = {
            "vendor": {"error_messages": {"required": "Vendor ID is required"}},
            "po_number": {"error_messages": {"required": "Purchase order's unique number is required"}},
            "order_date": {"error_messages": {"required": "Order date is required"}},
            "delivery_date": {"error_messages": {"required": "Delivery date is required"}},
            "quantity": {"error_messages": {"required": "Total number of item is required"}},
            "quality_ratings": {"min_value": 0.0, "max_value": 10.0},
            "items": {"error_messages": {"required": "Item list is required"}},
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if instance.status == "completed":
            instance.issue_date = datetime.datetime.now()
            instance.save(update_fields=["issue_date"])
            signals.order_completion_signal.send(sender=instance.__class__, instance=instance)
        return instance


class POAcknowledgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrder
        fields = ["acknowledgment_date"]
        extra_kwargs = {"acknowledgment_date": {"required": True}}

    def validate_acknowledgment_date(self, value):
        if not value:
            value = datetime.da.now()
        return value

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        signals.purchase_order_acknowledged.send(sender=instance.__class__, instance=instance)
        return instance


class HistoricalPerformanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = HistoricalPerformance
        fields = "__all__"


class MyUserSerializer(serializers.ModelSerializer):

    def validate(self, data):
        obj = MyUser.objects.filter(username=data.get('username')).first()
        if obj:
            raise serializers.ValidationError("Username already exists!")
        return super().validate(data)
    
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password')
