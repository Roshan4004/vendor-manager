from django.db import models
from django.db.models import Avg, F
from django.contrib.auth.models import AbstractUser

class MyUser(AbstractUser):
    pass

    def __str__(self):
        return self.username

class Vendor(models.Model):
    name = models.CharField(max_length=500)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(unique=True, blank=False, max_length=20, null=False)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

    def filter_purchase_orders_by_status(self, type=None):
        if type is None:
            return self.purchase_order.all()
        elif type not in ["completed", "pending", "cancelled"]:
            return None
        else:
            return self.purchase_order.filter(status=type)

    def calculate_average_response_time(self):
        filtered_purchase_orders = self.purchase_order.filter(
            issue_date__isnull=False, acknowledgment_date__isnull=False
        )
        if filtered_purchase_orders.exists():
            avg_response_time = filtered_purchase_orders.aggregate(
                avg_response_time=Avg(
                    F("acknowledgment_date") - F("issue_date")
                )
            ).get("avg_response_time")

            if avg_response_time is not None:
                return round(avg_response_time.total_seconds(), 2)
        return 0

    def calculate_on_time_delivery_ratio(self):
        completed_purchase_orders = self.filter_purchase_orders_by_status(type="completed")
        on_time_deliveries = completed_purchase_orders.filter(
            acknowledgment_date__lte=F("delivery_date")
        )
        try:
            return round(on_time_deliveries.count() / completed_purchase_orders.count(), 2)
        except ZeroDivisionError:
            return 0

    def calculate_average_quality_rating(self):
        completed_purchase_orders = self.filter_purchase_orders_by_status(type="completed")
        result = completed_purchase_orders.aggregate(
            avg_quality_rating=Avg("quality_rating", default=0.0)
        )
        return round(result.get("avg_quality_rating"), 2)

    def calculate_fulfillment_ratio(self):
        completed_purchase_orders = self.filter_purchase_orders_by_status(type="completed")
        all_purchase_orders = self.purchase_order.all()
        try:
            return round(completed_purchase_orders.count() / all_purchase_orders.count(), 2)
        except ZeroDivisionError:
            return 0

class PurchaseOrder(models.Model):
    po_number = models.CharField(unique=True, blank=False, max_length=20)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="purchase_order")
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(default="Pending", max_length=20)
    quality_rating = models.FloatField(default=0.0)
    issue_date = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    acknowledgment_date = models.DateTimeField(null=True, blank=True, auto_now_add=False)

    def __str__(self):
        return f"{self.vendor.name}:{self.po_number}"
    
    class Meta:
        ordering = ["-order_date"]

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="historical")
    date = models.DateTimeField(blank=True, null=True)
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def __str__(self):
        return f"{self.vendor.name}:{self.date}"

    class Meta:
        ordering = ["-date"]
