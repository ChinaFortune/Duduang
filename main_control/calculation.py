from datetime import date
from . import data


def calculate_birth_date(user_input):

    # =========================
    # ข้อมูลวันเกิด
    # =========================

    birth_date = user_input.birth_date
    birth_time = user_input.birth_time

    # วัน / เดือน / ปี
    day = birth_date.day
    month = birth_date.month
    year = birth_date.year

    # =========================
    # ข้อมูลเวลาเกิด
    # =========================

    hour = None
    minute = None

    if birth_time:
        hour = birth_time.hour
        minute = birth_time.minute

    # =========================
    # วันที่เริ่มต้น
    # =========================

    start_date = date(1926, 12, 1)

    # =========================
    # จำนวนวันที่ผ่านไป
    # =========================

    days_passed = (birth_date - start_date).days

    # =========================
    # Index
    # =========================

    rasi_up_index = days_passed % 10
    rasi_down_index = days_passed % 12

    # =========================
    # ข้อมูลราศี
    # =========================

    rasi_up_result = data.rasi_up[rasi_up_index]
    rasi_down_result = data.rasi_down[rasi_down_index]

    # =========================
    # ผลลัพธ์
    # =========================

    return {
        "day": day,
        "month": month,
        "year": year,

        "hour": hour,
        "minute": minute,

        "rasi_up_index": rasi_up_index,
        "rasi_up": rasi_up_result,

        "rasi_down_index": rasi_down_index,
        "rasi_down": rasi_down_result,
    }
