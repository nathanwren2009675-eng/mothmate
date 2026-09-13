from django.contrib import admin
from django.urls import path
from records import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('add/', views.add_sighting, name='add-sighting'),
    path('records/', views.records, name='records'),
    path('delete/<int:sighting_id>/', views.delete_sighting, name='delete-sighting'),
    path('delete-all/', views.delete_all_records, name='delete-all'),  # ← MUST HAVE THIS LINE!
    path('transfer/', views.legacy_transfer, name='legacy-transfer'),
    path('stats/', views.stats, name='stats'),
    path('about/', views.about, name='about'),
]