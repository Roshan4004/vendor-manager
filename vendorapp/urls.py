from django.urls import path
from vendorapp import views

urlpatterns = [
    path('vendors/<int:pk>', views.VendorAPI.as_view(),name="vendor_some"),
    path('vendors/', views.VendorAPI.as_view(),name="vendor"),
    path('purchase_orders/<int:pk>', views.PurchaseAPI.as_view(),name="purchase_order_some"),
    path('purchase_orders/', views.PurchaseAPI.as_view(),name="purchase_order"),
    path('purchase_orders/<int:pk>/acknowledge/', views.acknowledge,name="acknowledge"),
    path('vendors/<int:pk>/performance/', views.HistoryAPI.as_view(),name="performance"),
    path('login', views.LoginView.as_view(),name="login"),
    path('register', views.RegistrationView.as_view(),name="register"),
]
