import os
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .calculation import evaluate_bazi_chart, DB, save_database
from .models import FortuneRecord
from .auth_service import auth_service

THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

ENG_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def form_view(request):
    """
    Renders Fortune Teller input form (30% Left / 70% Right Split)
    """
    days_range = list(range(1, 32))
    years_range = list(range(2026, 1939, -1))
    hours_range = list(range(0, 24))
    minutes_range = list(range(0, 60))

    context = {
        'days_range': days_range,
        'years_range': years_range,
        'hours_range': hours_range,
        'minutes_range': minutes_range,
    }
    return render(request, 'form.html', context)


def login_view(request):
    """
    Renders Authentication page (Login/Register tabs) backed by JSON Auth Service
    with future External API integration template.
    """
    error_msg = None
    success_msg = None

    # Handle Logout
    if request.GET.get('logout'):
        request.session.flush()
        return redirect('bazi:login')

    if request.method == 'POST':
        action = request.POST.get('action', 'login')
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if action == 'register':
            full_name = request.POST.get('full_name', '').strip()
            result = auth_service.register(email, password, full_name)
            if result.get('success'):
                u = result['user']
                request.session['user_id'] = u['id']
                request.session['user_email'] = u['email']
                request.session['user_name'] = u['full_name']
                return redirect('bazi:form')
            else:
                error_msg = result.get('error', 'การลงทะเบียนล้มเหลว')
        else:
            # Login
            result = auth_service.authenticate(email, password)
            if result.get('success'):
                u = result['user']
                request.session['user_id'] = u['id']
                request.session['user_email'] = u['email']
                request.session['user_name'] = u['full_name']
                return redirect('bazi:form')
            else:
                error_msg = result.get('error', 'เข้าสู่ระบบไม่สำเร็จ กรุณาตรวจสอบอีเมลและรหัสผ่าน')

    context = {
        'error_msg': error_msg,
        'success_msg': success_msg,
    }
    return render(request, 'login.html', context)


def booking_view(request):
    """
    Renders Private Consultation Booking page with Master Ning profile & packages
    """
    booking_success = False
    if request.method == 'POST':
        # Simulated booking submission
        booking_success = True

    return render(request, 'booking.html', {'booking_success': booking_success})


def history_view(request):
    """
    Renders Calculation History records with search filter
    """
    search_query = request.GET.get('q', '').strip()
    if search_query:
        records = FortuneRecord.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(province__icontains=search_query)
        )
    else:
        records = FortuneRecord.objects.all()[:50]

    context = {
        'records': records,
        'search_query': search_query,
    }
    return render(request, 'history.html', context)


def result_view(request):
    """
    Renders Bazi Fortune Result Dashboard (Strictly 8-Cell Chart + Strength Panel + 5 Roles + 4 Pillars)
    Now matches ExampleDuduang 100% and displays Master avatar on the left.
    """
    if request.method == 'POST':
        data = request.POST
    else:
        data = request.GET

    first_name = data.get('first_name', 'กฤษณะ').strip() or 'กฤษณะ'
    last_name = data.get('last_name', 'แสงทอง').strip() or 'แสงทอง'
    gender = data.get('gender', 'male')
    
    # Birth Place
    birth_place = data.get('birth_place', '').strip()
    province = birth_place or data.get('province', 'กรุงเทพมหานคร')
    country = data.get('country', 'ประเทศไทย')

    try:
        birth_day = int(data.get('birth_day', 14))
    except (ValueError, TypeError):
        birth_day = 14

    try:
        birth_month = int(data.get('birth_month', 2))
    except (ValueError, TypeError):
        birth_month = 2

    try:
        birth_year = int(data.get('birth_year', 1995))
    except (ValueError, TypeError):
        birth_year = 1995

    # Check unknown birth time
    birth_time_unknown = data.get('birth_time_unknown') in ['1', 'true', True]

    hour = None
    minute = 0

    if not birth_time_unknown:
        birth_time = data.get('birth_time', '09:30')
        if birth_time and ':' in birth_time:
            parts = birth_time.split(':')
            try:
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
            except ValueError:
                hour, minute = 9, 30
        else:
            try:
                h_val = data.get('birth_hour')
                m_val = data.get('birth_minute')
                if h_val is not None:
                    hour = int(h_val)
                    minute = int(m_val or 0)
                else:
                    hour, minute = 9, 30
            except (ValueError, TypeError):
                hour, minute = 9, 30

        if hour is not None:
            hour = max(0, min(23, hour))
            minute = max(0, min(59, minute))

    # Ensure range boundaries
    birth_day = max(1, min(31, birth_day))
    birth_month = max(1, min(12, birth_month))

    # Evaluate Bazi Chart adhering to ExampleDuduang
    chart_result = evaluate_bazi_chart(birth_year, birth_month, birth_day, hour, minute)

    # Save or update in database
    try:
        record, created = FortuneRecord.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            birth_day=birth_day,
            birth_month=birth_month,
            birth_year=birth_year,
            defaults={
                'birth_hour': hour if hour is not None else 0,
                'birth_minute': minute if minute is not None else 0,
                'gender': gender,
                'province': province,
                'country': country,
                'chart_data': chart_result,
            }
        )
        if not created:
            record.birth_hour = hour if hour is not None else 0
            record.birth_minute = minute if minute is not None else 0
            record.gender = gender
            record.province = province
            record.country = country
            record.chart_data = chart_result
            record.save()
    except Exception:
        pass

    # Build Header date strings
    th_month_str = THAI_MONTHS[birth_month - 1]
    en_month_str = ENG_MONTHS[birth_month - 1]
    buddhist_year = birth_year + 543 if birth_year < 2400 else birth_year
    ce_year = birth_year if birth_year < 2400 else birth_year - 543

    if hour is not None:
        hour_animal_th = chart_result.get('hour_animal_th', 'มะเส็ง')
        hour_animal_en = chart_result.get('hour_animal_en', 'Snake')
        birth_header_th = f"เกิด: {birth_day} {th_month_str} {buddhist_year} เวลา {hour:02d}:{minute:02d} น. (ยาม{hour_animal_th})"
        birth_header_en = f"Born: {birth_day} {en_month_str} {ce_year} at {hour:02d}:{minute:02d} ({hour_animal_en} Hour)"
        birth_time_str = f"{hour:02d}:{minute:02d}"
    else:
        birth_header_th = f"เกิด: {birth_day} {th_month_str} {buddhist_year} (ไม่ระบุเวลาเกิด)"
        birth_header_en = f"Born: {birth_day} {en_month_str} {ce_year} (Unknown Hour)"
        birth_time_str = "ไม่ระบุเวลาเกิด"

    context = {
        'first_name': first_name,
        'last_name': last_name,
        'user_full_name': f"{first_name} {last_name}",
        'gender': gender,
        'birth_day': birth_day,
        'birth_month': birth_month,
        'birth_year': birth_year,
        'birth_time': birth_time_str,
        'birth_time_unknown': birth_time_unknown,
        'birth_place': province,
        'province': province,
        'country': country,
        'birth_header_th': birth_header_th,
        'birth_header_en': birth_header_en,
        'chart': chart_result,
    }
    return render(request, 'result.html', context)


def admin_dashboard_view(request):
    """
    PIN-protected Admin Dashboard
    Now displays:
    1. Overview Statistics Dashboard
    2. Registered Users (from JSON Auth Database)
    3. Fortune Analysis History
    4. BaZi Wisdom Book / Grimoire (ดึงจาก bazi_database.json ที่ adapt มาจาก data.py)
    """
    admin_pin = os.environ.get('ADMIN_PIN', '8888')
    pin_error = None

    # Handle Logout
    if request.GET.get('logout'):
        request.session['admin_authenticated'] = False
        return redirect('bazi:admin_dashboard')

    # Handle PIN submission
    if request.method == 'POST' and request.POST.get('action') == 'pin_auth':
        entered_pin = request.POST.get('pin', '').strip()
        if entered_pin == admin_pin:
            request.session['admin_authenticated'] = True
        else:
            pin_error = "รหัส PIN ไม่ถูกต้อง (Invalid PIN)"

    is_authenticated = request.session.get('admin_authenticated', False)

    if not is_authenticated:
        return render(request, 'admin_dashboard.html', {
            'is_authenticated': False,
            'pin_error': pin_error,
        })

    # Handle Authenticated Admin Actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # User CRUD
        if action == 'add_user':
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            role = request.POST.get('role', 'member').strip()
            auth_service.create_user(email, password, full_name, role)
            return redirect(f"{request.path}?tab=users")

        elif action == 'edit_user':
            user_id = request.POST.get('user_id', '').strip()
            email = request.POST.get('email', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            role = request.POST.get('role', 'member').strip()
            password = request.POST.get('password', '').strip()
            auth_service.update_user(user_id, email=email or None, full_name=full_name, role=role, password=password if password else None)
            return redirect(f"{request.path}?tab=users")

        elif action == 'delete_user':
            user_id = request.POST.get('user_id', '').strip()
            auth_service.delete_user(user_id)
            return redirect(f"{request.path}?tab=users")

        # Wisdom Grimoire CRUD
        elif action == 'edit_wisdom':
            zh = request.POST.get('chinese', '').strip()
            title = request.POST.get('title', '').strip()
            good = request.POST.get('good', '').strip()
            bad = request.POST.get('bad', '').strip()
            advice = request.POST.get('advice', '').strip()
            if zh:
                if 'elementMeaning' not in DB:
                    DB['elementMeaning'] = {}
                DB['elementMeaning'][zh] = {
                    'title': title,
                    'good': good,
                    'bad': bad,
                    'advice': advice
                }
                for stem in DB.get('heavenlyStems', []):
                    if stem.get('chinese') == zh:
                        stem['pros'] = good
                        stem['cons'] = bad
                        stem['advice'] = advice
                        break
                save_database(DB)
            return redirect(f"{request.path}?tab=wisdom")

        elif action == 'delete_wisdom':
            zh = request.POST.get('chinese', '').strip()
            if zh:
                if 'elementMeaning' in DB and zh in DB['elementMeaning']:
                    del DB['elementMeaning'][zh]
                for stem in DB.get('heavenlyStems', []):
                    if stem.get('chinese') == zh:
                        stem['pros'] = "ไม่มีข้อมูล"
                        stem['cons'] = "ไม่มีข้อมูล"
                        stem['advice'] = "ไม่มีข้อมูล"
                        break
                save_database(DB)
            return redirect(f"{request.path}?tab=wisdom")

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        records_qs = FortuneRecord.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(province__icontains=search_query) |
            Q(gender__icontains=search_query)
        )
    else:
        records_qs = FortuneRecord.objects.all()

    total_records = FortuneRecord.objects.count()
    today_records = FortuneRecord.objects.filter(
        last_analyzed_at__date=timezone.now().date()
    ).count()

    # User Accounts from JSON database
    users_list = auth_service.list_users()

    # Book / Grimoire reference data from adapted database
    wisdom_stems = []
    element_meanings = DB.get('elementMeaning', {})
    for stem in DB.get('heavenlyStems', []):
        zh = stem.get('chinese', '')
        m_info = element_meanings.get(zh, {})
        wisdom_stems.append({
            'chinese': zh,
            'th_name': stem.get('thaiName', ''),
            'title': m_info.get('title', stem.get('thaiName', '')),
            'good': m_info.get('good', stem.get('pros', '')),
            'bad': m_info.get('bad', stem.get('cons', '')),
            'advice': m_info.get('advice', stem.get('advice', '')),
            'color': DB.get('rasiColor', {}).get(zh, '#315B4A')
        })

    wisdom_branches = DB.get('earthlyBranches', [])
    solar_months = DB.get('example_source', {}).get('table_rasi_month_down', [])

    # Ajax details endpoint
    if request.GET.get('record_id'):
        rec_id = request.GET.get('record_id')
        try:
            r = FortuneRecord.objects.get(id=rec_id)
            return JsonResponse({
                'id': r.id,
                'name': f"{r.first_name} {r.last_name}",
                'first_name': r.first_name,
                'last_name': r.last_name,
                'gender': r.gender,
                'birth_date': f"{r.birth_day}/{r.birth_month}/{r.birth_year}",
                'birth_time': f"{r.birth_hour:02d}:{r.birth_minute:02d}" if r.birth_hour is not None else "ไม่ระบุ",
                'location': f"{r.province}, {r.country}",
                'chart_data': r.chart_data,
                'last_analyzed': r.last_analyzed_at.strftime('%d/%m/%Y %H:%M'),
            })
        except FortuneRecord.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)

    context = {
        'is_authenticated': True,
        'records': records_qs[:100],
        'total_records': total_records,
        'today_records': today_records,
        'users_list': users_list,
        'users_count': len(users_list),
        'wisdom_stems': wisdom_stems,
        'wisdom_branches': wisdom_branches,
        'solar_months': solar_months,
        'search_query': search_query,
        'active_tab': request.GET.get('tab', 'overview'),
    }
    return render(request, 'admin_dashboard.html', context)
