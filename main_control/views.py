import django
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .auth_views import (
    check_email_api,
    delete_fortune_view,
    google_callback,
    google_login,
    history_view,
    login_view,
    logout_view,
    register_view,
    save_fortune_view,
)
from .calculation import calculate_birth_date
from .models import UserInput, UserProfile


def home(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        gender = request.POST.get("gender")
        birth_date = request.POST.get("birthDate")
        birth_time = request.POST.get("birthTime")

        user_input = UserInput.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            birth_date=birth_date,
            birth_time=birth_time or None,
        )

        return redirect("result", user_id=user_input.id)

    context = {
        "django_version": django.get_version(),
        "user_profile": user_profile,
    }

    return render(request, "home.html", context)


def intro(request):
    context = {
        "django_version": django.get_version(),
    }
    return render(request, "intro.html", context)


def result(request, user_id):
    user_input = get_object_or_404(UserInput, id=user_id)

    # If user arrived with auto_save flag after login/signup
    if request.user.is_authenticated and request.GET.get('auto_save') == '1':
        if not user_input.is_saved or user_input.user != request.user:
            user_input.user = request.user
            user_input.is_saved = True
            user_input.save()
            messages.success(request, 'บันทึกผลดวงชะตาเข้าสู่ประวัติของคุณเรียบร้อยแล้ว!')

    is_saved = bool(user_input.is_saved and user_input.user == request.user)

    birth_result = calculate_birth_date(user_input)

    context = {
        "user_input": user_input,
        "birth_result": birth_result,
        "is_saved": is_saved,
    }

    return render(
        request,
        "result.html",
        context
    )
