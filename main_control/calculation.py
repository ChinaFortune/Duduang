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
    # Index วัน
    # =========================

    day_up_index = days_passed % 10
    day_down_index = days_passed % 12

    # =========================
    # ข้อมูลราศีวัน
    # =========================

    day_up_result = data.rasi_up[day_up_index]
    day_down_result = data.rasi_down[day_down_index]

    # =========================
    # Index ปี
    # =========================
    #
    # ปี 1926 = (2, 2)
    # ปีถัดไป index เพิ่มทีละ 1
    #
    # rasi_up   มี 10 ตัว
    # rasi_down มี 12 ตัว
    # =========================

    if year < 1926:
        raise ValueError("Year must be >= 1926")

    years_passed = year - 1926

    year_up_index = (2 + years_passed) % 10
    year_down_index = (2 + years_passed) % 12

    # =========================
    # ข้อมูลราศีปี
    # =========================

    year_up_result = data.rasi_up[year_up_index]
    year_down_result = data.rasi_down[year_down_index]

    # =========================
    # Index เดือน
    # =========================
    #
    # ตรวจสอบวันเดือนเกิดกับ
    # data.table_rasi_month
    #
    # ตัวอย่าง:
    #
    # start = (12, 8)
    # end   = (1, 5)
    #
    # หมายถึง:
    # 8 ธันวาคม ถึง 5 มกราคม
    #
    # =========================

    month_down_index = None
    month_down_result = None

    for month_data in data.table_rasi_month:

        start_month, start_day = month_data["start"]
        end_month, end_day = month_data["end"]

        # =========================
        # กรณีช่วงไม่ข้ามปี
        # เช่น 1/6 -> 2/3
        # =========================

        if start_month <= end_month:

            start_point = (start_month, start_day)
            end_point = (end_month, end_day)
            birth_point = (month, day)

            if start_point <= birth_point <= end_point:

                month_down_zh = month_data["zh"]

                for index, rasi in enumerate(data.rasi_down):

                    if rasi["zh"] == month_down_zh:

                        month_down_index = index
                        month_down_result = rasi
                        break

                break

        # =========================
        # กรณีช่วงข้ามปี
        # เช่น 12/8 -> 1/5
        # =========================

        else:

            if (
                (month == start_month and day >= start_day)
                or
                (month == end_month and day <= end_day)
                or
                (month > start_month)
                or
                (month < end_month)
            ):

                month_down_zh = month_data["zh"]

                for index, rasi in enumerate(data.rasi_down):

                    if rasi["zh"] == month_down_zh:

                        month_down_index = index
                        month_down_result = rasi
                        break

                break

    # =========================
    # ผลลัพธ์
    # =========================

    return {
        "day": day,
        "month": month,
        "year": year,

        "hour": hour,
        "minute": minute,

        # -------------------------
        # Day
        # -------------------------

        "day_up_index": day_up_index,
        "day_up": day_up_result,

        "day_down_index": day_down_index,
        "day_down": day_down_result,

        # -------------------------
        # Month
        # -------------------------

        "month_down_index": month_down_index,
        "month_down": month_down_result,

        # -------------------------
        # Year
        # -------------------------

        "year_up_index": year_up_index,
        "year_up": year_up_result,

        "year_down_index": year_down_index,
        "year_down": year_down_result,
    }
