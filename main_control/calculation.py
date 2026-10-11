
from datetime import date
from . import data


def _get_up_rasi(index):
    """
    คืนข้อมูลราศีบน พร้อม index และสี
    """
    if index is None:
        return {"index": None, "result": None, "color": None}

    result = data.rasi_up[index]
    return {
        "index": index,
        "result": result,
        "color": data.rasi_color.get(result["zh"]),
    }


def _get_down_rasi(index):
    """
    คืนข้อมูลราศีล่าง พร้อม index
    ราศีล่างไม่มีสี
    """
    if index is None:
        return {"index": None, "result": None}

    return {"index": index, "result": data.rasi_down[index]}


def _get_down_element(down_rasi):
    if not down_rasi or not down_rasi.get("result"):
        return None

    rasi_th = down_rasi["result"]["th"]
    return data.element_of_rasi.get(rasi_th)


def _get_rasi_index_by_zh(zh, rasis):
    return next(
        (index for index, rasi in enumerate(rasis) if rasi["zh"] == zh),
        None,
    )


def calculate_secondary_score(
    secondary_elements,
    day_up, day_down,
    month_up, month_down,
    year_up, year_down,
    hour_up, hour_down,
    day_up_num, day_down_num,
    month_up_num, month_down_num,
    year_up_num, year_down_num,
    hour_up_num, hour_down_num,
):
    rasis = [
        (day_up, day_up_num),
        (day_down, day_down_num),
        (month_up, month_up_num),
        (month_down, month_down_num),
        (year_up, year_up_num),
        (year_down, year_down_num),
        (hour_up, hour_up_num),
        (hour_down, hour_down_num),
    ]

    total = 0

    for rasi, num in rasis:
        if not rasi or not rasi.get("result"):
            continue

        th = rasi["result"]["th"]
        element_text = (
            th if "color" in rasi
            else data.element_of_rasi.get(th, "")
        )

        element = next(
            (e for e in data.useful_elements if element_text.startswith(e)),
            None,
        )

        total += (1 if element in secondary_elements else 0) * num

    return total


def calculate_birth_date(user_input):

    # =========================================================
    # ข้อมูลวันเกิด
    # =========================================================

    birth_date = user_input.birth_date
    birth_time = user_input.birth_time

    day, month, year = birth_date.day, birth_date.month, birth_date.year

    # =========================================================
    # ข้อมูลเวลาเกิด
    # =========================================================

    hour = birth_time.hour if birth_time else None
    minute = birth_time.minute if birth_time else None

    # =========================================================
    # วันที่เริ่มต้น
    # =========================================================

    start_date = date(1926, 12, 1)

    # =========================================================
    # จำนวนวันที่ผ่านไป
    # =========================================================

    days_passed = (birth_date - start_date).days

    # =========================================================
    # Index วัน
    # =========================================================

    day_up_index = days_passed % 10
    day_down_index = days_passed % 12

    # =========================================================
    # ผลราศีวัน
    # =========================================================

    day_up = _get_up_rasi(day_up_index)
    day_down = _get_down_rasi(day_down_index)

    # =========================================================
    # คะแนนราศีวัน
    # =========================================================

    day_up_num = 1
    day_down_num = 1.5

    # =========================================================
    # ความหมายราศีบนของวัน
    #
    # ใช้เฉพาะ day -> up -> result -> zh
    # =========================================================

    day_up_result = day_up["result"]
    day_up_meaning = (
        data.element_meaning.get(day_up_result["zh"])
        if day_up_result else None
    )
    day_up["meaning"] = day_up_meaning

    # =========================================================
    # Index ปี
    #
    # ปีจะเปลี่ยน index ในวันที่ 4 กุมภาพันธ์
    #
    # เช่น
    # 1926-02-03 -> 0
    # 1926-02-04 -> 0
    # 1927-02-03 -> 0
    # 1927-02-04 -> 1
    # 1928-02-03 -> 1
    # 1928-02-04 -> 2
    #
    # ใช้ปี 1926 เป็นฐาน index 0
    # =========================================================

    if year < 1926:
        raise ValueError("Year must be >= 1926")

    # ---------------------------------------------------------
    # กำหนดวันที่เปลี่ยนปีตามระบบนี้
    # ---------------------------------------------------------

    year_change_date = date(year, 2, 4)

    # ---------------------------------------------------------
    # ถ้ายังไม่ถึงวันที่ 4 กุมภาพันธ์
    # ให้ใช้รอบปีเดิม
    #
    # เช่น 1927-02-03
    # จะยังนับเป็นปี 1926
    # ---------------------------------------------------------

    year_cycle = year - 1927 if birth_date < year_change_date else year - 1926

    # ---------------------------------------------------------
    # ป้องกันค่าติดลบสำหรับข้อมูลก่อนปี 1926
    # ---------------------------------------------------------

    if year_cycle < 0:
        raise ValueError("Year must be >= 1926")

    year_up_index = (2 + year_cycle) % 10
    year_down_index = (2 + year_cycle) % 12

    # =========================================================
    # ผลราศีปี
    # =========================================================

    year_up = _get_up_rasi(year_up_index)
    year_down = _get_down_rasi(year_down_index)

    # =========================================================
    # คะแนนราศีปี
    # =========================================================

    year_up_num = 1
    year_down_num = 1

    # =========================================================
    # Index เดือน
    # =========================================================

    month_up_index = None
    month_down_index = None

    # =========================================================
    # แปลง ค.ศ. เป็น พ.ศ.
    # =========================================================

    buddhist_year = year + 543

    # =========================================================
    # เลขท้ายของปี พ.ศ.
    # =========================================================

    buddhist_year_last_digit = buddhist_year % 10

    # =========================================================
    # หาแถวจากวัน / เดือนเกิด
    # =========================================================

    for index, month_data in enumerate(data.table_rasi_month_down):
        start_month, start_day = month_data["start"]
        end_month, end_day = month_data["end"]

        # =====================================================
        # กรณีช่วงไม่ข้ามปี
        # =====================================================

        if start_month <= end_month:
            start_point = (start_month, start_day)
            end_point = (end_month, end_day)
            birth_point = (month, day)

            if start_point <= birth_point <= end_point:
                # ---------------------------------------------
                # ราศีเดือนล่าง
                # ---------------------------------------------

                month_down_zh = month_data["zh"]
                month_down_index = _get_rasi_index_by_zh(
                    month_down_zh, data.rasi_down
                )

                # ---------------------------------------------
                # ราศีเดือนบน
                # ---------------------------------------------

                month_up_zh = data.table_rasi_month_up[index][
                    buddhist_year_last_digit
                ]
                month_up_index = _get_rasi_index_by_zh(
                    month_up_zh, data.rasi_up
                )
                break

        # =====================================================
        # กรณีช่วงข้ามปี
        # เช่น 12/8 -> 1/5
        # =====================================================

        else:
            if (
                (month == start_month and day >= start_day)
                or (month == end_month and day <= end_day)
                or (month > start_month)
                or (month < end_month)
            ):
                # ---------------------------------------------
                # ราศีเดือนล่าง
                # ---------------------------------------------

                month_down_zh = month_data["zh"]
                month_down_index = _get_rasi_index_by_zh(
                    month_down_zh, data.rasi_down
                )

                # ---------------------------------------------
                # ราศีเดือนบน
                # ---------------------------------------------

                month_up_zh = data.table_rasi_month_up[index][
                    buddhist_year_last_digit
                ]
                month_up_index = _get_rasi_index_by_zh(
                    month_up_zh, data.rasi_up
                )
                break

    # =========================================================
    # ผลราศีเดือน
    # =========================================================

    month_up = _get_up_rasi(month_up_index)
    month_down = _get_down_rasi(month_down_index)

    # =========================================================
    # คะแนนราศีเดือน
    # =========================================================

    month_up_num = 1
    month_down_num = 2

    # =========================================================
    # ราศียาม
    #
    # ใช้ day_up เป็นตัวกำหนดหลัก
    # =========================================================

    hour_up_index = None
    hour_down_index = None

    if birth_time:
        day_up_zh = day_up["result"]["zh"]

        # =====================================================
        # ตรวจสอบว่ามีตารางราศียามหรือไม่
        # =====================================================

        if day_up_zh in data.table_rasi_hour:
            hour_table = data.table_rasi_hour[day_up_zh]

            # =================================================
            # หาแถวจากเวลาเกิด
            # =================================================

            for hour_data in hour_table:
                start_hour, start_minute = hour_data["start"]
                end_hour, end_minute = hour_data["end"]

                # =================================================
                # กรณีข้ามวัน
                # 23:00 - 00:59
                # =================================================

                if start_hour > end_hour:
                    if (
                        (
                            hour > start_hour
                            or (
                                hour == start_hour
                                and minute >= start_minute
                            )
                        )
                        or (
                            hour < end_hour
                            or (
                                hour == end_hour
                                and minute <= end_minute
                            )
                        )
                    ):
                        hour_up_zh = hour_data["up"]
                        hour_down_zh = hour_data["down"]

                        # -----------------------------------------
                        # ราศียามบน
                        # -----------------------------------------

                        hour_up_index = _get_rasi_index_by_zh(
                            hour_up_zh, data.rasi_up
                        )

                        # -----------------------------------------
                        # ราศียามล่าง
                        # -----------------------------------------

                        hour_down_index = _get_rasi_index_by_zh(
                            hour_down_zh, data.rasi_down
                        )
                        break

                # =================================================
                # กรณีช่วงเวลาปกติ
                # =================================================

                else:
                    start_point = (start_hour, start_minute)
                    end_point = (end_hour, end_minute)
                    birth_point = (hour, minute)

                    if start_point <= birth_point <= end_point:
                        hour_up_zh = hour_data["up"]
                        hour_down_zh = hour_data["down"]

                        # -----------------------------------------
                        # ราศียามบน
                        # -----------------------------------------

                        hour_up_index = _get_rasi_index_by_zh(
                            hour_up_zh, data.rasi_up
                        )

                        # -----------------------------------------
                        # ราศียามล่าง
                        # -----------------------------------------

                        hour_down_index = _get_rasi_index_by_zh(
                            hour_down_zh, data.rasi_down
                        )
                        break

    # =========================================================
    # ผลราศียาม
    # =========================================================

    hour_up = _get_up_rasi(hour_up_index)
    hour_down = _get_down_rasi(hour_down_index)

    # =========================================================
    # คะแนนราศียาม
    # =========================================================

    hour_up_num = 1
    hour_down_num = 1

    # =========================================================
    # คำนวณคะแนนรวม
    # =========================================================

    day_up_element = day_up["result"]["th"] if day_up["result"] else ""
    day_up_element = next(
        (e for e in data.useful_elements if day_up_element.startswith(e)),
        None,
    )

    useful_elements = data.useful_elements.get(day_up_element, [])

    score = calculate_secondary_score(
        useful_elements,
        day_up, day_down,
        month_up, month_down,
        year_up, year_down,
        hour_up, hour_down,
        day_up_num, day_down_num,
        month_up_num, month_down_num,
        year_up_num, year_down_num,
        hour_up_num, hour_down_num,
    )

    # =========================================================
    # ผลลัพธ์
    #
    # day.up จะมี:
    #
    # result["day"]["up"]["index"]
    # result["day"]["up"]["result"]
    # result["day"]["up"]["color"]
    # result["day"]["up"]["meaning"]
    #
    # โดย meaning จะมีเฉพาะราศีบนของวัน
    #
    # ส่วน month / year / hour จะมี:
    #
    # index
    # result
    # color
    #
    # ราศีล่างจะมี:
    #
    # index
    # result
    # =========================================================

    return {
        # =====================================================
        # ข้อมูลวันเกิด
        # =====================================================

        "date": {"day": day, "month": month, "year": year},

        # =====================================================
        # ข้อมูลเวลาเกิด
        # =====================================================

        "time": {"hour": hour, "minute": minute},

        # =====================================================
        # วัน
        # =====================================================

        "day": {
            "up": day_up,
            "down": day_down,
            "down_element": _get_down_element(day_down),
        },

        # =====================================================
        # เดือน
        # =====================================================

        "month": {
            "up": month_up,
            "down": month_down,
            "down_element": _get_down_element(month_down),
        },

        # =====================================================
        # ปี
        # =====================================================

        "year": {
            "up": year_up,
            "down": year_down,
            "down_element": _get_down_element(year_down),
        },

        # =====================================================
        # ยาม
        # =====================================================

        "hour": {
            "up": hour_up,
            "down": hour_down,
            "down_element": _get_down_element(hour_down),
        },

        "total": score,
    }
