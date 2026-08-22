import django
from django.shortcuts import render, redirect
from .models import UserInput
from .calculation import calculate_birth_date
from . import data


def home(request):

    if request.method == "POST":

        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        gender = request.POST.get("gender")
        birth_date = request.POST.get("birthDate")
        birth_time = request.POST.get("birthTime")

        user_input = UserInput.objects.create(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            birth_date=birth_date,
            birth_time=birth_time or None,
        )

        return redirect("result", user_id=user_input.id)

    context = {
        "django_version": django.get_version(),
    }

    return render(request, "home.html", context)


def intro(request):

    context = {
        "django_version": django.get_version(),
    }

    return render(request, "intro.html", context)


def result(request, user_id):

    user_input = UserInput.objects.get(id=user_id)

    # =========================
    # คำนวณดวง
    # =========================

    birth_result = calculate_birth_date(user_input)

    # =========================
    # ราศีวัน
    # =========================

    day_up = birth_result.get("day_up")
    day_down = birth_result.get("day_down")

    # =========================
    # ราศีปี
    # =========================

    year_up = birth_result.get("year_up")
    year_down = birth_result.get("year_down")

    # =========================
    # หาความหมายจากราศีบนของวัน
    # =========================

    element_meaning = None

    if day_up:

        rasi_up = day_up.get("zh")

        if rasi_up:

            element_meaning = data.element_meaning.get(
                rasi_up
            )

    # =========================
    # Context
    # =========================

    context = {
        "user_input": user_input,
        "birth_result": birth_result,

        # ราศีวัน
        "day_up": day_up,
        "day_down": day_down,

        # ราศีปี
        "year_up": year_up,
        "year_down": year_down,

        # ความหมายราศีบน
        "element_meaning": element_meaning,
    }

    return render(
        request,
        "result.html",
        context
    )
