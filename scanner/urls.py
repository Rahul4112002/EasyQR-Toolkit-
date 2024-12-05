
from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    
    path('generate/',views.generate_qr, name='generate_qr'),
    path('scan/',views.scan_qr, name='scan_qr'),
]