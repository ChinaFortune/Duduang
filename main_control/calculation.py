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
    # ขั้นตอน:
    #
    # 1. แปลง ค.ศ. เป็น พ.ศ.
    # 2. ดูเลขท้ายของ พ.ศ.
    # 3. ใช้เลขท้ายเลือกหลักในตารางราศีเดือนบน
    # 4. ใช้วันและเดือนหาแถวจาก table_rasi_month_down
    # 5. ช่องบนของแถวนั้น = ราศีเดือนบน
    # 6. ช่องล่างของแถวนั้น = ราศีเดือนล่าง
    #
    # =========================

    month_up_index = None
    month_up_result = None

    month_down_index = None
    month_down_result = None

    # =========================
    # แปลง ค.ศ. เป็น พ.ศ.
    # =========================

    buddhist_year = year + 543

    # =========================
    # เลขท้ายของปี พ.ศ.
    # =========================

    buddhist_year_last_digit = buddhist_year % 10

    # =========================
    # หาแถวจากวัน / เดือนเกิด
    # =========================

    for index, month_data in enumerate(data.table_rasi_month_down):

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

                # -------------------------
                # ราศีเดือนล่าง
                # -------------------------

                month_down_zh = month_data["zh"]

                for rasi_index, rasi in enumerate(data.rasi_down):

                    if rasi["zh"] == month_down_zh:

                        month_down_index = rasi_index
                        month_down_result = rasi
                        break

                # -------------------------
                # ราศีเดือนบน
                # -------------------------

                month_up_zh = data.table_rasi_month_up[index][
                    buddhist_year_last_digit
                ]

                for rasi_index, rasi in enumerate(data.rasi_up):

                    if rasi["zh"] == month_up_zh:

                        month_up_index = rasi_index
                        month_up_result = rasi
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

                # -------------------------
                # ราศีเดือนล่าง
                # -------------------------

                month_down_zh = month_data["zh"]

                for rasi_index, rasi in enumerate(data.rasi_down):

                    if rasi["zh"] == month_down_zh:

                        month_down_index = rasi_index
                        month_down_result = rasi
                        break

                # -------------------------
                # ราศีเดือนบน
                # -------------------------

                month_up_zh = data.table_rasi_month_up[index][
                    buddhist_year_last_digit
                ]

                for rasi_index, rasi in enumerate(data.rasi_up):

                    if rasi["zh"] == month_up_zh:

                        month_up_index = rasi_index
                        month_up_result = rasi
                        break

                break

    # =========================================================
    # ราศียาม
    #
    # ขั้นตอน:
    #
    # 1. ใช้ day_up ของวันเกิดเพื่อระบุหลัก
    # 2. ใช้เวลาเกิดเพื่อระบุแถว
    # 3. ช่องบน = hour_up
    # 4. ช่องล่าง = hour_down
    #
    # =========================================================

    hour_up_index = None
    hour_up_result = None

    hour_down_index = None
    hour_down_result = None

    if birth_time:

        # =========================
        # ราศีบนของวัน
        # =========================

        day_up_zh = day_up_result["zh"]

        # =========================
        # ตรวจสอบว่า day_up
        # มีอยู่ในตารางราศียามหรือไม่
        # =========================

        if day_up_zh in data.table_rasi_hour:

            hour_table = data.table_rasi_hour[day_up_zh]

            # =========================
            # หาแถวจากเวลาเกิด
            # =========================

            for hour_data in hour_table:

                start_hour, start_minute = hour_data["start"]
                end_hour, end_minute = hour_data["end"]

                # =========================
                # กรณีข้ามวัน
                # 23:00 - 00:59
                # =========================

                if start_hour > end_hour:

                    if (
                        (
                            hour > start_hour
                            or
                            (
                                hour == start_hour
                                and minute >= start_minute
                            )
                        )
                        or
                        (
                            hour < end_hour
                            or
                            (
                                hour == end_hour
                                and minute <= end_minute
                            )
                        )
                    ):

                        hour_up_zh = hour_data["up"]
                        hour_down_zh = hour_data["down"]

                        # -------------------------
                        # ราศียามบน
                        # -------------------------

                        for rasi_index, rasi in enumerate(data.rasi_up):

                            if rasi["zh"] == hour_up_zh:

                                hour_up_index = rasi_index
                                hour_up_result = rasi
                                break

                        # -------------------------
                        # ราศียามล่าง
                        # -------------------------

                        for rasi_index, rasi in enumerate(data.rasi_down):

                            if rasi["zh"] == hour_down_zh:

                                hour_down_index = rasi_index
                                hour_down_result = rasi
                                break

                        break

                # =========================
                # กรณีช่วงเวลาปกติ
                # =========================

                else:

                    start_point = (start_hour, start_minute)
                    end_point = (end_hour, end_minute)
                    birth_point = (hour, minute)

                    if start_point <= birth_point <= end_point:

                        hour_up_zh = hour_data["up"]
                        hour_down_zh = hour_data["down"]

                        # -------------------------
                        # ราศียามบน
                        # -------------------------

                        for rasi_index, rasi in enumerate(data.rasi_up):

                            if rasi["zh"] == hour_up_zh:

                                hour_up_index = rasi_index
                                hour_up_result = rasi
                                break

                        # -------------------------
                        # ราศียามล่าง
                        # -------------------------

                        for rasi_index, rasi in enumerate(data.rasi_down):

                            if rasi["zh"] == hour_down_zh:

                                hour_down_index = rasi_index
                                hour_down_result = rasi
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

        "month_up_index": month_up_index,
        "month_up": month_up_result,

        "month_down_index": month_down_index,
        "month_down": month_down_result,

        # -------------------------
        # Hour
        # -------------------------

        "hour_up_index": hour_up_index,
        "hour_up": hour_up_result,

        "hour_down_index": hour_down_index,
        "hour_down": hour_down_result,

        # -------------------------
        # Year
        # -------------------------

        "year_up_index": year_up_index,
        "year_up": year_up_result,

        "year_down_index": year_down_index,
        "year_down": year_down_result,
    }