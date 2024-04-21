from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_image, name='upload_image'),
    path('generate_stickers/', views.generate_stickers, name='generate_stickers'),
]
