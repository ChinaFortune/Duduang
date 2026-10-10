import secrets
import urllib.parse
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import UserInput, UserProfile


def login_view(request):
    """
    Renders login page and handles standard username/email + password login.
    If email does not exist in the database, seamlessly redirects to registration.
    """
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    if request.user.is_authenticated:
        return redirect(next_url)

    if request.method == 'POST':
        login_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not login_identifier or not password:
            messages.error(request, 'กรุณากรอกชื่อผู้ใช้หรืออีเมล และรหัสผ่าน')
        else:
            # Check if this user exists by username or email
            user_match = User.objects.filter(
                models.Q(username__iexact=login_identifier) | models.Q(email__iexact=login_identifier)
            ).first()

            if not user_match:
                # Per user requirement: if email does not exist, redirect to registration page
                messages.info(
                    request,
                    'ไม่พบบัญชีนี้ในระบบ เราได้นำคุณมายังหน้าลงทะเบียน กรุณากรอกข้อมูลส่วนตัวเพื่อเริ่มต้นใช้งาน'
                )
                reg_url = f"{reverse('register')}?email={urllib.parse.quote(login_identifier)}&next={urllib.parse.quote(next_url)}"
                return redirect(reg_url)

            # User exists, authenticate password
            user = authenticate(request, username=user_match.username, password=password)
            if user is not None:
                login(request, user)
                display_name = user.get_full_name() or user.username
                messages.success(request, f'ยินดีต้อนรับคุณ {display_name}')
                return redirect(next_url)
            else:
                messages.error(request, 'รหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง')

    is_google_configured = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    context = {
        'next_url': next_url,
        'is_google_configured': is_google_configured,
        'google_client_id': settings.GOOGLE_CLIENT_ID,
    }
    return render(request, 'login.html', context)


def google_login(request):
    """
    Initiates Google OAuth 2.0 flow.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        messages.error(
            request,
            'ระบบ Google Login ยังไม่ได้ตั้งค่า GOOGLE_CLIENT_ID หรือ GOOGLE_CLIENT_SECRET ในไฟล์ .env'
        )
        return redirect('login')

    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state
    request.session['google_oauth_next'] = request.GET.get('next', 'home')

    redirect_uri = request.build_absolute_uri(reverse('google_callback'))

    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'offline',
        'prompt': 'select_account',
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return redirect(google_auth_url)


def google_callback(request):
    """
    Receives callback from Google OAuth.
    If the account already exists and has complete profile: logs in immediately.
    If the account is new or has incomplete profile: redirects to registration page
    with Google email locked (readonly) and pre-filled info.
    """
    error = request.GET.get('error')
    if error:
        messages.warning(request, f'ยกเลิกการเข้าสู่ระบบผ่าน Google ({error})')
        return redirect('login')

    code = request.GET.get('code')
    state = request.GET.get('state')
    session_state = request.session.pop('google_oauth_state', None)

    if not state or state != session_state:
        messages.error(request, 'การตรวจสอบความปลอดภัยล้มเหลว (State Mismatch) กรุณาลองใหม่อีกครั้ง')
        return redirect('login')

    if not code:
        messages.error(request, 'ไม่ได้รับ Authorization Code จาก Google')
        return redirect('login')

    redirect_uri = request.build_absolute_uri(reverse('google_callback'))
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }

    try:
        token_resp = requests.post(token_url, data=token_data, timeout=12)
        if not token_resp.ok:
            messages.error(request, 'ไม่สามารถแลกเปลี่ยน Token กับ Google ได้ กรุณาลองใหม่อีกครั้ง')
            return redirect('login')

        token_json = token_resp.json()
        access_token = token_json.get('access_token')
        if not access_token:
            messages.error(request, 'ไม่ได้รับ Access Token จาก Google')
            return redirect('login')

        userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        userinfo_resp = requests.get(
            userinfo_url,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=12,
        )
        if not userinfo_resp.ok:
            messages.error(request, 'ไม่สามารถดึงข้อมูลโปรไฟล์จาก Google ได้')
            return redirect('login')

        user_info = userinfo_resp.json()
        email = (user_info.get('email') or '').strip().lower()
        if not email:
            messages.error(request, 'ไม่พบบัญชีอีเมลที่ผูกกับ Google บัญชีนี้')
            return redirect('login')

        next_url = request.session.pop('google_oauth_next', 'home') or 'home'

        # Check if user already exists
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.filter(username__iexact=email.split('@')[0]).first()

        # If user exists AND has already completed their profile
        if user:
            profile = getattr(user, 'profile', None)
            if not profile:
                profile = UserProfile.objects.create(user=user)

            if profile.is_profile_complete:
                login(request, user)
                display_name = user.get_full_name() or user.username
                messages.success(request, f'เข้าสู่ระบบสำเร็จ: {display_name}')
                return redirect(next_url)

        # User is new OR profile is incomplete: redirect to register page
        request.session['google_register_data'] = {
            'email': email,
            'first_name': user_info.get('given_name', ''),
            'last_name': user_info.get('family_name', ''),
        }

        messages.info(request, 'เชื่อมต่อกับ Google สำเร็จ กรุณากรอกข้อมูลดวงชะตาของคุณเพื่อเสร็จสิ้นการลงทะเบียน')
        reg_url = f"{reverse('register')}?from_google=1&next={urllib.parse.quote(next_url)}"
        return redirect(reg_url)

    except requests.RequestException:
        messages.error(request, 'เกิดข้อผิดพลาดในการเชื่อมต่อเครือข่ายกับ Google')
        return redirect('login')


def register_view(request):
    """
    Handles user registration:
    - Pre-fills from Google if redirected from Google (email locked/readonly).
    - Regular registration with editable email, password, and duplicate check.
    - Captures: first name, last name, email, gender, birth date, birth time,
      unknown birth time checkbox, birth place, and terms agreement.
    """
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    is_from_google = (request.GET.get('from_google') == '1' or request.POST.get('from_google') == '1')
    google_data = request.session.get('google_register_data', {})

    if is_from_google and not google_data:
        # Fallback if session expired
        is_from_google = False

    default_email = google_data.get('email') if is_from_google else request.GET.get('email', '')
    default_first_name = google_data.get('first_name', '')
    default_last_name = google_data.get('last_name', '')

    email_already_exists = False

    if request.method == 'POST':
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = (google_data.get('email') if is_from_google else request.POST.get('email', '')).strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        gender = request.POST.get('gender', 'female')
        birth_date = request.POST.get('birthDate', '')
        unknown_birth_time = request.POST.get('unknownBirthTime') == '1'
        birth_time = None if unknown_birth_time else (request.POST.get('birthTime') or None)
        birth_place = request.POST.get('birthPlace', '').strip()
        agree_terms = request.POST.get('agreeTerms') == '1'

        # Validations
        if not agree_terms:
            messages.error(request, 'กรุณากดยืนยันยอมรับข้อตกลงและเงื่อนไขการใช้งานก่อนลงทะเบียน')
        elif not first_name or not last_name or not email or not birth_date:
            messages.error(request, 'กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน (ชื่อ, นามสกุล, อีเมล, วันเดือนปีเกิด)')
        else:
            # Check for existing email if non-google
            if not is_from_google:
                if User.objects.filter(email__iexact=email).exists():
                    email_already_exists = True
                    messages.error(request, 'อีเมลนี้มีอยู่ในระบบแล้ว กรุณาเข้าสู่ระบบด้วยบัญชีเดิม')
                elif not password or len(password) < 6:
                    messages.error(request, 'รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร')
                elif password != confirm_password:
                    messages.error(request, 'รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน')

            if not messages.get_messages(request) and not email_already_exists:
                # Create or get user
                user = User.objects.filter(email__iexact=email).first()
                if not user:
                    base_username = email.split('@')[0]
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}_{counter}"
                        counter += 1

                    if is_from_google:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                        )
                    else:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=first_name,
                            last_name=last_name,
                        )
                else:
                    user.first_name = first_name
                    user.last_name = last_name
                    if not is_from_google and password:
                        user.set_password(password)
                    user.save()

                # Create or update profile
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.gender = gender
                profile.birth_date = birth_date
                profile.birth_time = birth_time
                profile.unknown_birth_time = unknown_birth_time
                profile.birth_place = birth_place
                profile.agreed_terms = True
                profile.is_profile_complete = True
                profile.oauth_provider = 'google' if is_from_google else 'local'
                profile.save()

                # Clean up session
                request.session.pop('google_register_data', None)

                # Log the user in
                login(request, user)
                messages.success(request, f'ลงทะเบียนสำเร็จ ยินดีต้อนรับคุณ {user.first_name}!')
                return redirect(next_url)

    context = {
        'next_url': next_url,
        'is_from_google': is_from_google,
        'default_email': default_email,
        'default_first_name': default_first_name,
        'default_last_name': default_last_name,
        'email_already_exists': email_already_exists,
        'form_data': request.POST if request.method == 'POST' else {},
    }
    return render(request, 'register.html', context)


def check_email_api(request):
    """
    API for checking if an email is already registered in the system.
    """
    email = request.GET.get('email', '').strip().lower()
    if not email:
        return JsonResponse({'exists': False})

    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists, 'email': email})


def logout_view(request):
    """
    Logs out user and redirects to home.
    """
    logout(request)
    messages.info(request, 'ออกจากระบบเรียบร้อยแล้ว')
    return redirect('home')


@login_required
def save_fortune_view(request, user_id):
    """
    Saves a calculated fortune result to the authenticated user's account.
    """
    user_input = get_object_or_404(UserInput, id=user_id)
    user_input.user = request.user
    user_input.is_saved = True
    user_input.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'success': True, 'message': 'บันทึกผลดวงสำเร็จเรียบร้อยแล้ว'})

    messages.success(request, 'บันทึกผลดวงชะตาเข้าสู่ประวัติของคุณเรียบร้อยแล้ว!')
    return redirect('result', user_id=user_id)


@login_required
def history_view(request):
    """
    Displays saved fortunes history for the authenticated user.
    """
    saved_fortunes = UserInput.objects.filter(user=request.user, is_saved=True).order_by('-created_at')
    context = {
        'saved_fortunes': saved_fortunes,
    }
    return render(request, 'history.html', context)


@login_required
def delete_fortune_view(request, fortune_id):
    """
    Deletes a saved fortune from the user's history.
    """
    fortune = get_object_or_404(UserInput, id=fortune_id, user=request.user)
    fortune.is_saved = False
    fortune.save()
    messages.info(request, 'นำผลการทำนายออกจากประวัติเรียบร้อยแล้ว')
    return redirect('history')
