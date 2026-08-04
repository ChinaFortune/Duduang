import django
from django.shortcuts import render

def home(request):
    context = {
        'django_version': django.get_version(),
    }
    return render(request, 'index.html', context)
