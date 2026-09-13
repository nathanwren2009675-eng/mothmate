from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-sighting/', views.add_sighting, name='add_sighting'),
    path('my-records/', views.my_records, name='my_records'),
    path('legacy-import/', views.legacy_import, name='legacy_import'),
]