from django.urls import path
from vendorapp import views

urlpatterns = [
    path('vendors/<int:pk>', views.VendorAPI.as_view()),
    path('vendors/', views.VendorAPI.as_view()),
    path('purchase_orders/<int:pk>', views.PurchaseAPI.as_view()),
    path('purchase_orders/', views.PurchaseAPI.as_view()),
    path('purchase_orders/<int:pk>/acknowledge/', views.acknowledge),
    path('vendors/<int:pk>/performance/', views.HistoryAPI.as_view()),
    path('login', views.LoginView.as_view()),
    path('register', views.RegistrationView.as_view()),
]
