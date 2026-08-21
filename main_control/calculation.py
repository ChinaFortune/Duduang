rasi_up = [
    {"zh": "甲", "th": "ไม้หยาง", "symbol": "ม+"},
    {"zh": "乙", "th": "ไม้หยิน", "symbol": "ม-"},
    {"zh": "丙", "th": "ไฟหยาง", "symbol": "ฟ+"},
    {"zh": "丁", "th": "ไฟหยิน", "symbol": "ฟ-"},
    {"zh": "戊", "th": "ดินหยาง", "symbol": "ด+"},
    {"zh": "己", "th": "ดินหยิน", "symbol": "ด-"},
    {"zh": "庚", "th": "ทองหยาง", "symbol": "ท+"},
    {"zh": "辛", "th": "ทองหยิน", "symbol": "ท-"},
    {"zh": "壬", "th": "น้ำหยาง", "symbol": "น+"},
    {"zh": "癸", "th": "น้ำหยิน", "symbol": "น-"},
]

rasi_down = [
    {"zh": "子", "th": "ชวด"},
    {"zh": "丑", "th": "ฉลู"},
    {"zh": "寅", "th": "ขาล"},
    {"zh": "卯", "th": "เถาะ"},
    {"zh": "辰", "th": "มะโรง"},
    {"zh": "巳", "th": "มะเส็ง"},
    {"zh": "午", "th": "มะเมีย"},
    {"zh": "未", "th": "มะแม"},
    {"zh": "申", "th": "วอก"},
    {"zh": "酉", "th": "ระกา"},
    {"zh": "戌", "th": "จอ"},
    {"zh": "亥", "th": "กุน"},
]

def calculate_birth_date(user_input):
    """
    รับข้อมูล UserInput
    แล้วแยกวัน เดือน ปี และเวลาเกิดออกมา
    """

    birth_date = user_input.birth_date
    birth_time = user_input.birth_time

    # แยก วัน / เดือน / ปี
    day = birth_date.day
    month = birth_date.month
    year = birth_date.year

    # แยกเวลา
    hour = None
    minute = None

    if birth_time:
        hour = birth_time.hour
        minute = birth_time.minute

    return {
        "day": day,
        "month": month,
        "year": year,
        "hour": hour,
        "minute": minute,
    }