from datetime import date
from . import data


def _get_up_rasi(index):
    """
    คืนข้อมูลราศีบน พร้อม index และสี
    """

    if index is None:
        return {
            "index": None,
            "result": None,
            "color": None,
        }

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
        return {
            "index": None,
            "result": None,
        }

    result = data.rasi_down[index]

    return {
        "index": index,
        "result": result,
    }


def _get_up_rasi_by_zh(zh):
    """
    ค้นหาราศีบนจาก zh
    """

    for index, rasi in enumerate(data.rasi_up):

        if rasi["zh"] == zh:
            return _get_up_rasi(index)

    return {
        "index": None,
        "result": None,
        "color": None,
    }


def _get_down_rasi_by_zh(zh):
    """
    ค้นหาราศีล่างจาก zh
    """

    for index, rasi in enumerate(data.rasi_down):

        if rasi["zh"] == zh:
            return _get_down_rasi(index)

    return {
        "index": None,
        "result": None,
    }


def calculate_birth_date(user_input):

    # =========================================================
    # ข้อมูลวันเกิด
    # =========================================================

    birth_date = user_input.birth_date
    birth_time = user_input.birth_time

    day = birth_date.day
    month = birth_date.month
    year = birth_date.year

    # =========================================================
    # ข้อมูลเวลาเกิด
    # =========================================================

    hour = None
    minute = None

    if birth_time:
        hour = birth_time.hour
        minute = birth_time.minute

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
    # ความหมายราศีบนของวัน
    #
    # ใช้เฉพาะ day -> up -> result -> zh
    # =========================================================

    day_up_result = day_up["result"]

    if day_up_result:

        day_up_meaning = data.element_meaning.get(
            day_up_result["zh"]
        )

    else:

        day_up_meaning = None

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

    if birth_date < year_change_date:
        year_cycle = year - 1927
    else:
        year_cycle = year - 1926

    # ---------------------------------------------------------
    # ป้องกันค่าติดลบสำหรับข้อมูลก่อนปี 1926
    # ---------------------------------------------------------

    if year_cycle < 0:
        raise ValueError("Year must be >= 1926")

    year_up_index = (2 +year_cycle) % 10
    year_down_index = (2 + year_cycle) % 12

    # =========================================================
    # ผลราศีปี
    # =========================================================

    year_up = _get_up_rasi(year_up_index)
    year_down = _get_down_rasi(year_down_index)

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

    for index, month_data in enumerate(
        data.table_rasi_month_down
    ):

        start_month, start_day = month_data["start"]
        end_month, end_day = month_data["end"]

        # =====================================================
        # กรณีช่วงไม่ข้ามปี
        # =====================================================

        if start_month <= end_month:

            start_point = (
                start_month,
                start_day,
            )

            end_point = (
                end_month,
                end_day,
            )

            birth_point = (
                month,
                day,
            )

            if start_point <= birth_point <= end_point:

                # ---------------------------------------------
                # ราศีเดือนล่าง
                # ---------------------------------------------

                month_down_zh = month_data["zh"]

                month_down_index = None

                for rasi_index, rasi in enumerate(
                    data.rasi_down
                ):

                    if rasi["zh"] == month_down_zh:

                        month_down_index = rasi_index
                        break

                # ---------------------------------------------
                # ราศีเดือนบน
                # ---------------------------------------------

                month_up_zh = data.table_rasi_month_up[index][
                    buddhist_year_last_digit
                ]

                for rasi_index, rasi in enumerate(
                    data.rasi_up
                ):

                    if rasi["zh"] == month_up_zh:

                        month_up_index = rasi_index
                        break

                break

        # =====================================================
        # กรณีช่วงข้ามปี
        # เช่น 12/8 -> 1/5
        # =====================================================

        else:

            if (
                (
                    month == start_month
                    and day >= start_day
                )
                or
                (
                    month == end_month
                    and day <= end_day
                )
                or
                (month > start_month)
                or
                (month < end_month)
            ):

                # ---------------------------------------------
                # ราศีเดือนล่าง
                # ---------------------------------------------

                month_down_zh = month_data["zh"]

                month_down_index = None

                for rasi_index, rasi in enumerate(
                    data.rasi_down
                ):

                    if rasi["zh"] == month_down_zh:

                        month_down_index = rasi_index
                        break

                # ---------------------------------------------
                # ราศีเดือนบน
                # ---------------------------------------------

                month_up_zh = data.table_rasi_month_up[index][
                    buddhist_year_last_digit
                ]

                for rasi_index, rasi in enumerate(
                    data.rasi_up
                ):

                    if rasi["zh"] == month_up_zh:

                        month_up_index = rasi_index
                        break

                break

    # =========================================================
    # ผลราศีเดือน
    # =========================================================

    month_up = _get_up_rasi(month_up_index)
    month_down = _get_down_rasi(month_down_index)

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

                        # -----------------------------------------
                        # ราศียามบน
                        # -----------------------------------------

                        for rasi_index, rasi in enumerate(
                            data.rasi_up
                        ):

                            if rasi["zh"] == hour_up_zh:

                                hour_up_index = rasi_index
                                break

                        # -----------------------------------------
                        # ราศียามล่าง
                        # -----------------------------------------

                        for rasi_index, rasi in enumerate(
                            data.rasi_down
                        ):

                            if rasi["zh"] == hour_down_zh:

                                hour_down_index = rasi_index
                                break

                        break

                # =================================================
                # กรณีช่วงเวลาปกติ
                # =================================================

                else:

                    start_point = (
                        start_hour,
                        start_minute,
                    )

                    end_point = (
                        end_hour,
                        end_minute,
                    )

                    birth_point = (
                        hour,
                        minute,
                    )

                    if start_point <= birth_point <= end_point:

                        hour_up_zh = hour_data["up"]
                        hour_down_zh = hour_data["down"]

                        # -----------------------------------------
                        # ราศียามบน
                        # -----------------------------------------

                        for rasi_index, rasi in enumerate(
                            data.rasi_up
                        ):

                            if rasi["zh"] == hour_up_zh:

                                hour_up_index = rasi_index
                                break

                        # -----------------------------------------
                        # ราศียามล่าง
                        # -----------------------------------------

                        for rasi_index, rasi in enumerate(
                            data.rasi_down
                        ):

                            if rasi["zh"] == hour_down_zh:

                                hour_down_index = rasi_index
                                break

                        break

    # =========================================================
    # ผลราศียาม
    # =========================================================

    hour_up = _get_up_rasi(hour_up_index)
    hour_down = _get_down_rasi(hour_down_index)

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

        "date": {
            "day": day,
            "month": month,
            "year": year,
        },

        # =====================================================
        # ข้อมูลเวลาเกิด
        # =====================================================

        "time": {
            "hour": hour,
            "minute": minute,
        },

        # =====================================================
        # วัน
        # =====================================================

        "day": {
            "up": day_up,
            "down": day_down,
        },

        # =====================================================
        # เดือน
        # =====================================================

        "month": {
            "up": month_up,
            "down": month_down,
        },

        # =====================================================
        # ปี
        # =====================================================

        "year": {
            "up": year_up,
            "down": year_down,
        },

        # =====================================================
        # ยาม
        # =====================================================

        "hour": {
            "up": hour_up,
            "down": hour_down,
        },
    }