import os
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .calculation import evaluate_bazi_chart
from .models import FortuneRecord

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
    Renders Welcome Back / Authentication page (Login/Register tabs)
    """
    return render(request, 'login.html')


def result_view(request):
    """
    Renders Bazi Fortune Result Dashboard (Strictly 8-Cell Chart + Strength Panel + 5 Roles + 4 Pillars)
    """
    if request.method == 'POST':
        data = request.POST
    else:
        data = request.GET

    first_name = data.get('first_name', 'กฤษณะ').strip() or 'กฤษณะ'
    last_name = data.get('last_name', 'แสงทอง').strip() or 'แสงทอง'
    gender = data.get('gender', 'male')
    province = data.get('province', 'กรุงเทพมหานคร')
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

    # Handle birth time (supports '09:30' or birth_hour & birth_minute)
    birth_time = data.get('birth_time', '09:30')
    if ':' in birth_time:
        parts = birth_time.split(':')
        try:
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            hour, minute = 9, 30
    else:
        try:
            hour = int(data.get('birth_hour', 9))
            minute = int(data.get('birth_minute', 30))
        except (ValueError, TypeError):
            hour, minute = 9, 30

    # Ensure range boundaries
    birth_day = max(1, min(31, birth_day))
    birth_month = max(1, min(12, birth_month))
    hour = max(0, min(23, hour))
    minute = max(0, min(59, minute))

    # Evaluate Bazi Chart
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
                'birth_hour': hour,
                'birth_minute': minute,
                'gender': gender,
                'province': province,
                'country': country,
                'chart_data': chart_result,
            }
        )
        if not created:
            record.birth_hour = hour
            record.birth_minute = minute
            record.gender = gender
            record.province = province
            record.country = country
            record.chart_data = chart_result
            record.save()
    except Exception as e:
        # Failsafe if DB write has unexpected schema constraint
        pass

    # Build Header date strings matching user cropped screenshot
    th_month_str = THAI_MONTHS[birth_month - 1]
    en_month_str = ENG_MONTHS[birth_month - 1]
    buddhist_year = birth_year + 543 if birth_year < 2400 else birth_year
    ce_year = birth_year if birth_year < 2400 else birth_year - 543

    hour_animal_th = chart_result.get('hour_animal_th', 'มะเส็ง')
    hour_animal_en = chart_result.get('hour_animal_en', 'Snake')

    birth_header_th = f"เกิด: {birth_day} {th_month_str} {buddhist_year} เวลา {hour:02d}:{minute:02d} น. (ยาม{hour_animal_th})"
    birth_header_en = f"Born: {birth_day} {en_month_str} {ce_year} at {hour:02d}:{minute:02d} ({hour_animal_en} Hour)"

    context = {
        'first_name': first_name,
        'last_name': last_name,
        'user_full_name': f"{first_name} {last_name}",
        'gender': gender,
        'birth_day': birth_day,
        'birth_month': birth_month,
        'birth_year': birth_year,
        'birth_time': f"{hour:02d}:{minute:02d}",
        'province': province,
        'country': country,
        'birth_header_th': birth_header_th,
        'birth_header_en': birth_header_en,
        'chart': chart_result,
    }
    return render(request, 'result.html', context)


def admin_dashboard_view(request):
    """
    PIN-protected Admin Dashboard (Fallback PIN '8888' or ADMIN_PIN env)
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

    # If not authenticated, render PIN entry modal / gate
    if not is_authenticated:
        return render(request, 'admin_dashboard.html', {
            'is_authenticated': False,
            'pin_error': pin_error,
        })

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

    # JSON detail endpoint for interactive modal
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
                'birth_time': f"{r.birth_hour:02d}:{r.birth_minute:02d}",
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
        'search_query': search_query,
    }
    return render(request, 'admin_dashboard.html', context)
