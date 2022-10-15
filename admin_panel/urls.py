from .views import change_proxy_ip_endpoint
from django.urls import path

urlpatterns = [
    path('/reconnect', change_proxy_ip_endpoint)
]