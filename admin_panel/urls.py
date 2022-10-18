from .views import change_proxy_ip_endpoint, get_hard_ip
from django.urls import path

urlpatterns = [
    path('reconnect/', change_proxy_ip_endpoint),
    path('ip/', get_hard_ip)
]