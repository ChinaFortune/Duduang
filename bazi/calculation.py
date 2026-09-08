import json
import os
from datetime import datetime, date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'bazi' / 'data' / 'bazi_database.json'

def load_database():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

DB = load_database()

# English & Thai Reference Maps
ELEMENT_NAMES = {
    0: {"th": "ไม้", "en": "Wood", "color": "#5bc474", "class": "elem-wood"},
    1: {"th": "ไฟ", "en": "Fire", "color": "#f26859", "class": "elem-fire"},
    2: {"th": "ดิน", "en": "Earth", "color": "#dfb743", "class": "elem-earth"},
    3: {"th": "ทอง", "en": "Metal", "color": "#d0d7de", "class": "elem-metal"},
    4: {"th": "น้ำ", "en": "Water", "color": "#58a6ff", "class": "elem-water"},
}

POLARITY_NAMES = {
    "+": {"th": "หยาง", "en": "Yang"},
    "-": {"th": "หยิน", "en": "Yin"},
}

ROLE_INFO = {
    "PEER": {
        "th": "ธาตุคู่ดิถี (มิตรสหาย พี่น้อง หุ้นส่วน)",
        "en": "Peer Element (Friends, Siblings, Partners)",
        "desc_short_th": "ส่งเสริมความมั่นใจ มิตรสหาย และพลังเกื้อหนุนในชีวิต",
        "desc_short_en": "Boosts self-confidence, network of friends, and peer support.",
    },
    "RESOURCE": {
        "th": "ธาตุก่อเกิด (ผู้ใหญ่อุปถัมภ์ วิชาการ มารดา)",
        "en": "Resource Element (Mentors, Academics, Parents)",
        "desc_short_th": "ได้รับการเอ็นดูจากผู้ใหญ่ มีปัญญาดี โดดเด่นทางวิชาการ",
        "desc_short_en": "Blessed with mentor patronage, sharp intellect, and wisdom.",
    },
    "OUTPUT": {
        "th": "ธาตุถ่ายเท (การแสดงออก ฝีมือ การลงทุน)",
        "en": "Output Element (Creativity, Talent, Investment)",
        "desc_short_th": "มีความคิดสร้างสรรค์ เจรจาค้าขายเก่ง ปรับตัวและแสดงออกยอดเยี่ยม",
        "desc_short_en": "High creativity, strong articulation, adaptability, and trade acumen.",
    },
    "WEALTH": {
        "th": "ธาตุโชคลาภ (การเงิน ทรัพย์สิน สิ่งที่ควบคุม)",
        "en": "Wealth Element (Finance, Assets, Control)",
        "desc_short_th": "หาเงินเก่ง มีหัวการค้า มีโอกาสสร้างความมั่งคั่งและมรดก",
        "desc_short_en": "Strong financial instincts, entrepreneurial knack, and wealth-building luck.",
    },
    "POWER": {
        "th": "ธาตุพิฆาต (อำนาจ วินัย กฎเกณฑ์ ตำแหน่ง)",
        "en": "Power Element (Authority, Discipline, Status)",
        "desc_short_th": "มีภาวะผู้นำ มีวินัยสูง เติบโตในตำแหน่งหน้าที่ราชการหรือบริหาร",
        "desc_short_en": "Executive leadership, strong self-discipline, and career advancement.",
    }
}

CLASH_PAIRS = [
    (0, 6), (6, 0),  # ชวด - มะเมีย
    (1, 7), (7, 1),  # ฉลู - มะแม
    (2, 8), (8, 2),  # ขาล - วอก
    (3, 9), (9, 3),  # เถาะ - ระกา
    (4, 10), (10, 4), # มะโรง - จอ
    (5, 11), (11, 5)  # มะเส็ง - กุน
]

def calculate_year_pillar(year, month, day):
    """
    DOCUMENT.md 2.1:
    Boundary: before Feb 4 uses birth_year - 1; from Feb 4 uses birth_year.
    Epoch: BE 2527 (CE 1984) is index 0 (Jia Zi / กะชวด).
    """
    target_year = year
    if month == 1 or (month == 2 and day < 4):
        target_year = year - 1
    
    # Check if year is in Buddhist Era (> 2400) or CE
    if target_year > 2400:
        ce_year = target_year - 543
    else:
        ce_year = target_year
        
    diff_year = ce_year - 1984
    stem_idx = ((diff_year % 10) + 10) % 10
    branch_idx = ((diff_year % 12) + 12) % 12
    return stem_idx, branch_idx

def calculate_day_pillar(year, month, day):
    """
    DOCUMENT.md 2.2:
    Calculate total actual days from epoch date (e.g. 1984-02-02 is Jia Zi, index 0).
    Jan 31, 1984 is Jia Zi (0, 0)
    Let's use verified astronomical anchor: 1984-01-31 was 甲子 (Jia Zi).
    """
    if year > 2400:
        ce_year = year - 543
    else:
        ce_year = year
    
    # Base date: 1984-01-31 was Jia Zi (Stem 0, Branch 0)
    base_date = date(1984, 1, 31)
    target_date = date(ce_year, month, day)
    total_days = (target_date - base_date).days
    
    stem_idx = ((total_days % 10) + 10) % 10
    branch_idx = ((total_days % 12) + 12) % 12
    return stem_idx, branch_idx

def calculate_month_pillar(year_stem_idx, month, day):
    """
    DOCUMENT.md 2.3:
    Solar seasonal month branches start from Tiger=2 in Feb, Rabbit=3 in Mar... Ox=1 in Jan.
    Five Tigers matrix lookup.
    """
    # Solar month branches:
    # Feb (month 2 >= 4): Tiger (2)
    # Mar (month 3 >= 5): Rabbit (3)
    # Apr (month 4 >= 5): Dragon (4)
    # May (month 5 >= 5): Snake (5)
    # Jun (month 6 >= 6): Horse (6)
    # Jul (month 7 >= 7): Goat (7)
    # Aug (month 8 >= 7): Monkey (8)
    # Sep (month 9 >= 7): Rooster (9)
    # Oct (month 10 >= 8): Dog (10)
    # Nov (month 11 >= 7): Pig (11)
    # Dec (month 12 >= 7): Rat (0)
    # Jan (month 1 >= 6): Ox (1)
    
    if (month == 2 and day >= 4) or (month == 3 and day < 5):
        branch_idx = 2  # ขาล Tiger
        month_row = 0
    elif (month == 3 and day >= 5) or (month == 4 and day < 5):
        branch_idx = 3  # เถาะ Rabbit
        month_row = 1
    elif (month == 4 and day >= 5) or (month == 5 and day < 5):
        branch_idx = 4  # มะโรง Dragon
        month_row = 2
    elif (month == 5 and day >= 5) or (month == 6 and day < 6):
        branch_idx = 5  # มะเส็ง Snake
        month_row = 3
    elif (month == 6 and day >= 6) or (month == 7 and day < 7):
        branch_idx = 6  # มะเมีย Horse
        month_row = 4
    elif (month == 7 and day >= 7) or (month == 8 and day < 7):
        branch_idx = 7  # มะแม Goat
        month_row = 5
    elif (month == 8 and day >= 7) or (month == 9 and day < 7):
        branch_idx = 8  # วอก Monkey
        month_row = 6
    elif (month == 9 and day >= 7) or (month == 10 and day < 8):
        branch_idx = 9  # ระกา Rooster
        month_row = 7
    elif (month == 10 and day >= 8) or (month == 11 and day < 7):
        branch_idx = 10 # จอ Dog
        month_row = 8
    elif (month == 11 and day >= 7) or (month == 12 and day < 7):
        branch_idx = 11 # กุน Pig
        month_row = 9
    elif (month == 12 and day >= 7) or (month == 1 and day < 6):
        branch_idx = 0  # ชวด Rat
        month_row = 10
    else:
        branch_idx = 1  # ฉลู Ox
        month_row = 11
        
    year_group = year_stem_idx % 5
    table = DB["fiveTigersMonthLookup"]["table"]
    stem_idx = table[month_row][year_group]
    return stem_idx, branch_idx

def calculate_hour_pillar(day_stem_idx, hour, minute=0):
    """
    DOCUMENT.md 2.4:
    Convert hour into 12 Earthly Branches periods.
    Five Rats matrix lookup.
    """
    total_minutes = hour * 60 + minute
    
    # 23:00 - 00:59 -> Rat (0)
    if total_minutes >= 23 * 60 or total_minutes < 1 * 60:
        branch_idx = 0
    elif total_minutes < 3 * 60:
        branch_idx = 1
    elif total_minutes < 5 * 60:
        branch_idx = 2
    elif total_minutes < 7 * 60:
        branch_idx = 3
    elif total_minutes < 9 * 60:
        branch_idx = 4
    elif total_minutes < 11 * 60:
        branch_idx = 5
    elif total_minutes < 13 * 60:
        branch_idx = 6
    elif total_minutes < 15 * 60:
        branch_idx = 7
    elif total_minutes < 17 * 60:
        branch_idx = 8
    elif total_minutes < 19 * 60:
        branch_idx = 9
    elif total_minutes < 21 * 60:
        branch_idx = 10
    else:
        branch_idx = 11
        
    day_group = day_stem_idx % 5
    table = DB["fiveRatsHourLookup"]["table"]
    stem_idx = table[branch_idx][day_group]
    return stem_idx, branch_idx

def evaluate_bazi_chart(year, month, day, hour, minute=0):
    """
    Comprehensive Bazi evaluation adhering to DOCUMENT.md:
    Returns full stems, branches, Day Master element, relationships, scoring,
    strength (WEAK, BALANCED, STRONG), and favorable/unfavorable elements.
    """
    year_stem_idx, year_branch_idx = calculate_year_pillar(year, month, day)
    day_stem_idx, day_branch_idx = calculate_day_pillar(year, month, day)
    month_stem_idx, month_branch_idx = calculate_month_pillar(year_stem_idx, month, day)
    hour_stem_idx, hour_branch_idx = calculate_hour_pillar(day_stem_idx, hour, minute)
    
    chart_stems = [hour_stem_idx, day_stem_idx, month_stem_idx, year_stem_idx]
    chart_branches = [hour_branch_idx, day_branch_idx, month_branch_idx, year_branch_idx]
    
    # Stems & Branches DB lookups
    stem_objs = [DB["heavenlyStems"][s] for s in chart_stems]
    branch_objs = [DB["earthlyBranches"][b] for b in chart_branches]
    
    # Day Master
    dm_stem = stem_objs[1]
    dm_elem = dm_stem["elementIndex"] # 0=Wood, 1=Fire, 2=Earth, 3=Metal, 4=Water
    
    # 3.1 Five Elements Relationships
    peer_elem = dm_elem
    resource_elem = (dm_elem - 1 + 5) % 5
    output_elem = (dm_elem + 1) % 5
    wealth_elem = (dm_elem + 2) % 5
    power_elem = (dm_elem + 3) % 5
    
    # 3.2 Scoring
    # Positions: HourStem, DayStem, MonthStem, YearStem, HourBranch, DayBranch, MonthBranch, YearBranch
    weights = [1.0, 0.0, 1.0, 1.0, 1.0, 1.5, 2.0, 1.0]
    half_branches = DB["scoringRules"]["halfScoreBranchesBySelfElement"].get(str(dm_elem), [])
    
    total_score = 0.0
    
    # Stems scoring (Hour, Month, Year - skipping Day Master)
    for idx, pos_weight in [(0, 1.0), (2, 1.0), (3, 1.0)]:
        elem = stem_objs[idx]["elementIndex"]
        if elem in [peer_elem, resource_elem]:
            total_score += pos_weight
            
    # Branches scoring
    # Positions: 0=Hour(1.0), 1=Day(1.5), 2=Month(2.0), 3=Year(1.0)
    for b_idx, (b_obj, pos_weight) in enumerate([
        (branch_objs[0], 1.0),
        (branch_objs[1], 1.5),
        (branch_objs[2], 2.0),
        (branch_objs[3], 1.0),
    ]):
        b_elem = b_obj["elementIndex"]
        b_num = b_obj["index"]
        
        if b_elem in [peer_elem, resource_elem]:
            score = pos_weight
        elif b_num in half_branches:
            score = pos_weight / 2.0
        else:
            score = 0.0
            
        # Clash penalty
        if score > 0:
            # Check adjacent branches for clash
            has_clash = False
            if b_idx > 0 and (b_num, chart_branches[b_idx - 1]) in CLASH_PAIRS:
                has_clash = True
            if b_idx < 3 and (b_num, chart_branches[b_idx + 1]) in CLASH_PAIRS:
                has_clash = True
                
            if has_clash and not (dm_elem == 2 and b_elem == 2):
                score = max(0.0, score - 0.5)
                
        total_score += score
        
    # 3.4 Strength Criteria
    if total_score < 4.5:
        strength_code = "WEAK"
        strength_th = "อ่อน"
        strength_en = "Weak"
        strength_badge_class = "status-weak"
        fav_elems = [peer_elem, resource_elem]
        unfav_elems = [output_elem, wealth_elem, power_elem]
    elif total_score < 5.0:
        strength_code = "BALANCED"
        strength_th = "สมดุล"
        strength_en = "Balanced"
        strength_badge_class = "status-balanced"
        fav_elems = [resource_elem, wealth_elem]
        unfav_elems = [peer_elem]
    else:
        strength_code = "STRONG"
        strength_th = "แข็งแรง"
        strength_en = "Strong"
        strength_badge_class = "status-strong"
        fav_elems = [wealth_elem, output_elem, power_elem]
        unfav_elems = [peer_elem, resource_elem]
        
    # Core personality description from Day Master
    core_personality_th = dm_stem["symbol"] + " " + dm_stem["pros"]
    core_personality_en = f"Symbolized by {dm_stem['symbol']}. Virtues: {dm_stem['pros']}"
    
    # Element roles bilingual list
    element_roles_data = [
        {
            "role_key": "PEER",
            "elem_index": peer_elem,
            "elem_name_th": ELEMENT_NAMES[peer_elem]["th"],
            "elem_name_en": ELEMENT_NAMES[peer_elem]["en"],
            "title_th": ROLE_INFO["PEER"]["th"],
            "title_en": ROLE_INFO["PEER"]["en"],
            "short_th": ROLE_INFO["PEER"]["desc_short_th"],
            "short_en": ROLE_INFO["PEER"]["desc_short_en"],
            "full_th": DB["pillarInterpretations"]["PEER"].get("monthStem", {}).get("fav", ""),
            "full_en": "Represents allies, business partners, and peer strength. When in harmony, promotes teamwork and great synergy.",
            "is_favorable": peer_elem in fav_elems
        },
        {
            "role_key": "RESOURCE",
            "elem_index": resource_elem,
            "elem_name_th": ELEMENT_NAMES[resource_elem]["th"],
            "elem_name_en": ELEMENT_NAMES[resource_elem]["en"],
            "title_th": ROLE_INFO["RESOURCE"]["th"],
            "title_en": ROLE_INFO["RESOURCE"]["en"],
            "short_th": ROLE_INFO["RESOURCE"]["desc_short_th"],
            "short_en": ROLE_INFO["RESOURCE"]["desc_short_en"],
            "full_th": DB["pillarInterpretations"]["RESOURCE"].get("monthStem", {}).get("fav", ""),
            "full_en": "Nourishes the Day Master with patron support, noble mentors, and intellectual pursuits.",
            "is_favorable": resource_elem in fav_elems
        },
        {
            "role_key": "OUTPUT",
            "elem_index": output_elem,
            "elem_name_th": ELEMENT_NAMES[output_elem]["th"],
            "elem_name_en": ELEMENT_NAMES[output_elem]["en"],
            "title_th": ROLE_INFO["OUTPUT"]["th"],
            "title_en": ROLE_INFO["OUTPUT"]["en"],
            "short_th": ROLE_INFO["OUTPUT"]["desc_short_th"],
            "short_en": ROLE_INFO["OUTPUT"]["desc_short_en"],
            "full_th": DB["pillarInterpretations"]["OUTPUT"].get("monthStem", {}).get("fav", ""),
            "full_en": "Showcases natural talent, expressive skills, entrepreneurship, and visionary innovations.",
            "is_favorable": output_elem in fav_elems
        },
        {
            "role_key": "WEALTH",
            "elem_index": wealth_elem,
            "elem_name_th": ELEMENT_NAMES[wealth_elem]["th"],
            "elem_name_en": ELEMENT_NAMES[wealth_elem]["en"],
            "title_th": ROLE_INFO["WEALTH"]["th"],
            "title_en": ROLE_INFO["WEALTH"]["en"],
            "short_th": ROLE_INFO["WEALTH"]["desc_short_th"],
            "short_en": ROLE_INFO["WEALTH"]["desc_short_en"],
            "full_th": DB["pillarInterpretations"]["WEALTH"].get("monthStem", {}).get("fav", ""),
            "full_en": "Governs wealth generation, strategic resource management, and commercial mastery.",
            "is_favorable": wealth_elem in fav_elems
        },
        {
            "role_key": "POWER",
            "elem_index": power_elem,
            "elem_name_th": ELEMENT_NAMES[power_elem]["th"],
            "elem_name_en": ELEMENT_NAMES[power_elem]["en"],
            "title_th": ROLE_INFO["POWER"]["th"],
            "title_en": ROLE_INFO["POWER"]["en"],
            "short_th": ROLE_INFO["POWER"]["desc_short_th"],
            "short_en": ROLE_INFO["POWER"]["desc_short_en"],
            "full_th": DB["pillarInterpretations"]["POWER"].get("monthStem", {}).get("fav", ""),
            "full_en": "Reflects leadership authority, legal discipline, honor, and administrative standing.",
            "is_favorable": power_elem in fav_elems
        }
    ]

    # Enrich stems & branches for pristine 8-cell table rendering
    elem_abbr_map = {0: "ม", 1: "ฟ", 2: "ด", 3: "ท", 4: "น"}
    enriched_stems = []
    for idx, s in enumerate(stem_objs):
        s_copy = dict(s)
        elem_idx = s_copy["elementIndex"]
        s_copy["elem_class"] = ELEMENT_NAMES[elem_idx]["class"]
        s_copy["elem_th"] = ELEMENT_NAMES[elem_idx]["th"]
        s_copy["elem_en"] = ELEMENT_NAMES[elem_idx]["en"]
        pol_th = POLARITY_NAMES[s_copy["polarity"]]["th"]
        pol_en = POLARITY_NAMES[s_copy["polarity"]]["en"]
        if idx == 1:  # Day Master
            s_copy["line2_th"] = f"{s_copy['thaiName']} ({s_copy['code']}) ★"
            s_copy["line2_en"] = f"{s_copy['chinese']} ({s_copy['thaiName']}) ★"
            s_copy["line3_th"] = f"ดิถีธาตุ{s_copy['elem_th']}{pol_th}"
            s_copy["line3_en"] = f"DM: {pol_en} {s_copy['elem_en']}"
            s_copy["is_dm"] = True
        else:
            s_copy["line2_th"] = f"{s_copy['thaiName']} ({s_copy['code']})"
            s_copy["line2_en"] = f"{s_copy['chinese']} ({s_copy['thaiName']})"
            s_copy["line3_th"] = f"ธาตุ{s_copy['elem_th']}{pol_th}"
            s_copy["line3_en"] = f"{pol_en} {s_copy['elem_en']}"
            s_copy["is_dm"] = False
        enriched_stems.append(s_copy)

    enriched_branches = []
    for idx, b in enumerate(branch_objs):
        b_copy = dict(b)
        elem_idx = b_copy["elementIndex"]
        b_copy["elem_class"] = ELEMENT_NAMES[elem_idx]["class"]
        b_copy["elem_th"] = ELEMENT_NAMES[elem_idx]["th"]
        b_copy["elem_en"] = ELEMENT_NAMES[elem_idx]["en"]
        pol_th = POLARITY_NAMES[b_copy["polarity"]]["th"]
        pol_en = POLARITY_NAMES[b_copy["polarity"]]["en"]
        abbr = f"{elem_abbr_map.get(elem_idx, '')}{b_copy['polarity']}"
        b_copy["line2_th"] = f"{b_copy['thaiName']} ({b_copy['animal']})"
        b_copy["line2_en"] = f"{b_copy['chinese']} ({b_copy['animal']})"
        b_copy["line3_th"] = f"ธาตุ{b_copy['elem_th']} ({abbr})"
        b_copy["line3_en"] = f"{pol_en} {b_copy['elem_en']}"
        enriched_branches.append(b_copy)

    hour_animal_th = branch_objs[0]["thaiName"]
    hour_animal_en = branch_objs[0]["animal"]

    return {
        "chart_stems": chart_stems,
        "chart_branches": chart_branches,
        "stem_objs": enriched_stems,
        "branch_objs": enriched_branches,
        "hour_animal_th": hour_animal_th,
        "hour_animal_en": hour_animal_en,
        "day_master": {
            "stem": dm_stem,
            "element_index": dm_elem,
            "element_th": ELEMENT_NAMES[dm_elem]["th"],
            "element_en": ELEMENT_NAMES[dm_elem]["en"],
            "polarity_th": POLARITY_NAMES[dm_stem["polarity"]]["th"],
            "polarity_en": POLARITY_NAMES[dm_stem["polarity"]]["en"],
            "badge_title_th": f"ดิถีธาตุ{ELEMENT_NAMES[dm_elem]['th']}{POLARITY_NAMES[dm_stem['polarity']]['th']} ({dm_stem['thaiName']} / {dm_stem['chinese']})",
            "badge_title_en": f"Day Master: {POLARITY_NAMES[dm_stem['polarity']]['en']} {ELEMENT_NAMES[dm_elem]['en']} ({dm_stem['chinese']})",
            "personality_th": core_personality_th,
            "personality_en": core_personality_en,
            "advice_th": dm_stem["advice"],
            "advice_en": "Cultivate specialized expertise and engage genuinely with peers.",
        },
        "total_score": round(total_score, 2),
        "score_percent": min(100, int((total_score / 8.5) * 100)),
        "strength_code": strength_code,
        "strength_th": strength_th,
        "strength_en": strength_en,
        "strength_badge_class": strength_badge_class,
        "favorable_elements": [ELEMENT_NAMES[e] for e in fav_elems],
        "unfavorable_elements": [ELEMENT_NAMES[e] for e in unfav_elems],
        "element_roles": element_roles_data,
        "pillar_interpretations": {
            "year": {
                "title_th": "หลักปี (Year Pillar) - บรรพบุรุษ & วัยเยาว์ (อายุ 1-16 ปี)",
                "title_en": "Year Pillar - Ancestry & Youth (Ages 1-16)",
                "desc_short_th": "สะท้อนรากฐานครอบครัว การสนับสนุนจากผู้ใหญ่ และความสุขสบายในวัยเยาว์",
                "desc_short_en": "Reflects ancestral foundations, early childhood comfort, and elder patronage.",
                "desc_full_th": "เป็นคนกตัญญู ผู้ใหญ่เอ็นดูเมตตา วัยเด็กสุขสบาย มีวิสัยทัศน์ค้าขายแดนไกล ความคิดสร้างสรรค์ดีและมีเกียรติ",
                "desc_full_en": "Blessed with elder care and family protection in early years, setting a firm launchpad for life."
            },
            "month": {
                "title_th": "หลักเดือน (Month Pillar) - วัยทำงาน & สังคม (อายุ 17-32 ปี)",
                "title_en": "Month Pillar - Career & Society (Ages 17-32)",
                "desc_short_th": "สะท้อนเส้นทางอาชีพ ความก้าวหน้าทางการงาน และความสัมพันธ์กับเพื่อนร่วมงาน",
                "desc_short_en": "Reflects career momentum, organizational growth, and interpersonal network.",
                "desc_full_th": "ชอบเข้าสังคม ช่วยเหลือเพื่อนฝูง วัยรุ่นเจริญก้าวหน้า เก่งงานบริการ งานบริหาร และการเจรจาการค้า",
                "desc_full_en": "Shows active social life, rapid career elevation, executive tact, and commercial success."
            },
            "day": {
                "title_th": "หลักวัน (Day Pillar) - ตัวตน & คู่ครอง (อายุ 33-48 ปี)",
                "title_en": "Day Pillar - Self & Spouse (Ages 33-48)",
                "desc_short_th": "สะท้อนจิตวิญญาณตัวตนที่แท้จริง และชีวิตคู่ครอบครัว",
                "desc_short_en": "Reflects inner self, core constitution, and marital harmony.",
                "desc_full_th": "คู่ครองเป็นเหมือนเพื่อนคู่คิด ร่วมทุกข์ร่วมสุข ช่วยเหลือเกื้อกูลกันดี ส่งเสริมความเจริญมั่นคงในครอบครัว",
                "desc_full_en": "Spouse serves as a steadfast life partner and wise confidant, fostering mutual flourishing."
            },
            "hour": {
                "title_th": "หลักยาม (Hour Pillar) - บั้นปลาย & บริวาร (อายุ 49 ปีขึ้นไป)",
                "title_en": "Hour Pillar - Later Life & Legacy (Ages 49+)",
                "desc_short_th": "สะท้อนความสำเร็จในบั้นปลายชีวิต ลูกหลาน และบริวาร",
                "desc_short_en": "Reflects legacy, fruitful descendants, subordinates, and comfort in later years.",
                "desc_full_th": "เอาใจใส่บริวาร ได้ลูกน้องดี บั้นปลายชีวิตมีความสุขตามฝัน สุขภาพแข็งแรง มีมรดกมั่นคง",
                "desc_full_en": "Enjoyable and fulfilling later years, loyal subordinates, strong health, and enduring legacy."
            }
        }
    }
