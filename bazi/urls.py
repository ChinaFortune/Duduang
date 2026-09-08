from django.urls import path
from . import views

app_name = 'bazi'

urlpatterns = [
    path('', views.form_view, name='form'),
    path('login/', views.login_view, name='login'),
    path('result/', views.result_view, name='result'),
    path('admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/', views.admin_dashboard_view, name='dashboard'),
]
