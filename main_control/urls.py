"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from .views import (
    home,
    intro,
    result,
    login_view,
    google_login,
    google_callback,
    logout_view,
    register_view,
    check_email_api,
    save_fortune_view,
    history_view,
    delete_fortune_view,
)

urlpatterns = [
    path('', intro, name='intro'),
    path('home/', home, name='home'),
    path('result/<int:user_id>/', result, name='result'),
    path('login/', login_view, name='login'),
    path('login/google/', google_login, name='google_login'),
    path('login/google/callback/', google_callback, name='google_callback'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('api/check-email/', check_email_api, name='check_email_api'),
    path('save-fortune/<int:user_id>/', save_fortune_view, name='save_fortune'),
    path('history/', history_view, name='history'),
    path('history/delete/<int:fortune_id>/', delete_fortune_view, name='delete_fortune'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
