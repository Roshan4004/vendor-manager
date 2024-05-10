from django.dispatch import Signal, receiver
from .models import HistoricalPerformance
import datetime

order_completion_signal = Signal()
order_acknowledgement_signal = Signal()


@receiver(signal=order_completion_signal)
def update_vendor_performance(sender, instance, **kwargs):
    vendor_instance = instance.vendor
    average_quality_rating = vendor_instance.calculate_average_quality_rating()
    fulfillment_ratio = vendor_instance.calculate_fulfillment_ratio()
    on_time_delivery = vendor_instance.calculate_on_time_delivery_ratio()

    vendor_instance.on_time_delivery_rate = on_time_delivery
    vendor_instance.quality_rating_avg = average_quality_rating
    vendor_instance.fulfillment_rate = fulfillment_ratio
    vendor_instance.save()
    vendor_instance.refresh_from_db()

    history_obj = HistoricalPerformance.objects.filter(vendor=vendor_instance.id).first()
    if history_obj:
        obj = HistoricalPerformance.objects.get(vendor=vendor_instance.id)
        obj.quality_rating_avg = average_quality_rating
        obj.fulfillment_rate = fulfillment_ratio
        obj.average_response_time = vendor_instance.average_response_time
        obj.on_time_delivery_rate = on_time_delivery
        obj.date = datetime.datetime.now()
        obj.save(update_fields=["quality_rating_avg", "fulfillment_rate", "average_response_time", "vendor", "on_time_delivery_rate", "date"])
    else:
        HistoricalPerformance.objects.create(
            quality_rating_avg=average_quality_rating,
            fulfillment_rate=fulfillment_ratio,
            average_response_time=vendor_instance.average_response_time,
            vendor=vendor_instance,
            on_time_delivery_rate=on_time_delivery,
            date=datetime.datetime.now()
        )
    return vendor_instance


@receiver(signal=order_acknowledgement_signal)
def update_response_time(sender, instance, **kwargs):
    vendor_instance = instance.vendor
    
    vendor_instance.average_response_time = vendor_instance.calculate_average_response_time()
    vendor_instance.save()
    return vendor_instance
