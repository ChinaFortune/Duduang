import django
from django.shortcuts import render, redirect
from .models import UserInput


def home(request):

    if request.method == "POST":

        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        gender = request.POST.get("gender")
        birth_date = request.POST.get("birthDate")
        birth_time = request.POST.get("birthTime")

        UserInput.objects.create(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            birth_date=birth_date,
            birth_time=birth_time or None,
        )

        return redirect("result")

    context = {
        'django_version': django.get_version(),
    }

    return render(request, 'home.html', context)


def intro(request):

    context = {
        'django_version': django.get_version(),
    }

    return render(request, 'intro.html', context)


def result(request):

    context = {
        'django_version': django.get_version(),
    }

    return render(request, 'result.html', context)