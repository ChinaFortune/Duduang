import django
from django.shortcuts import render

def home(request):
    context = {
        'django_version': django.get_version(),
    }
    return render(request, 'home.html', context)

def intro(request):
    context = {
        'django_version': django.get_version(),
    }
    return render(request, 'intro.html', context)
