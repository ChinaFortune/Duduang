import secrets
import urllib.parse
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse


def login_view(request):
    """
    Renders login page and handles standard username/email + password login.
    """
    # If user is already authenticated, redirect to home or next
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    if request.user.is_authenticated:
        return redirect(next_url)

    if request.method == 'POST':
        login_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not login_identifier or not password:
            messages.error(request, 'กรุณากรอกชื่อผู้ใช้/อีเมล และรหัสผ่าน')
        else:
            # Check if login_identifier is an email, resolve to username
            user_by_email = User.objects.filter(email__iexact=login_identifier).first()
            auth_username = user_by_email.username if user_by_email else login_identifier

            user = authenticate(request, username=auth_username, password=password)
            if user is not None:
                login(request, user)
                display_name = user.get_full_name() or user.username
                if user.is_superuser:
                    messages.success(request, f'ยินดีต้อนรับ ผู้ดูแลระบบ (Admin) {display_name}')
                else:
                    messages.success(request, f'ยินดีต้อนรับคุณ {display_name}')
                return redirect(next_url)
            else:
                messages.error(request, 'ชื่อผู้ใช้ หรือรหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง')

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

    # Generate secure random state token for CSRF protection
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
    Receives callback from Google OAuth, retrieves profile,
    and synchronizes with existing user (e.g. admin) or creates new user.
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

    # Exchange authorization code for access token
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

        # Fetch Google user profile
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

        # -------------------------------------------------------------
        # SYNCHRONIZATION WITH PREVIOUSLY CREATED ADMIN / EXISTING USER
        # -------------------------------------------------------------
        # 1. Match by email (e.g. pnatpakalp@gmail.com -> natpakarn)
        user = User.objects.filter(email__iexact=email).first()

        # 2. Match by username if no email match
        if not user:
            user = User.objects.filter(username__iexact=email.split('@')[0]).first()
            if user and not user.email:
                user.email = email
                user.save(update_fields=['email'])

        # 3. Create new user if not found
        if not user:
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
            )
        else:
            # User already exists (e.g. admin superuser): update name if empty
            updated_fields = []
            if not user.first_name and user_info.get('given_name'):
                user.first_name = user_info.get('given_name', '')
                updated_fields.append('first_name')
            if not user.last_name and user_info.get('family_name'):
                user.last_name = user_info.get('family_name', '')
                updated_fields.append('last_name')
            if updated_fields:
                user.save(update_fields=updated_fields)

        # Log in the user into the Django session
        login(request, user)

        display_name = user.get_full_name() or user.username
        if user.is_superuser:
            messages.success(request, f'เข้าสู่ระบบในฐานะ ผู้ดูแลระบบ (Superuser): {display_name}')
        else:
            messages.success(request, f'เข้าสู่ระบบสำเร็จ: {display_name}')

        next_url = request.session.pop('google_oauth_next', 'home') or 'home'
        return redirect(next_url)

    except requests.RequestException:
        messages.error(request, 'เกิดข้อผิดพลาดในการเชื่อมต่อเครือข่ายกับ Google')
        return redirect('login')


def logout_view(request):
    """
    Logs out user and redirects to home.
    """
    logout(request)
    messages.info(request, 'ออกจากระบบเรียบร้อยแล้ว')
    return redirect('home')
