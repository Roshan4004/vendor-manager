from django.contrib import admin
from vendorapp.models import Vendor, HistoricalPerformance, PurchaseOrder
# Register your models here.

admin.site.register(HistoricalPerformance)
admin.site.register(Vendor)
admin.site.register(PurchaseOrder)