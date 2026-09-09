import json
import os
from datetime import datetime, date, time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'bazi' / 'data' / 'bazi_database.json'

def load_database():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_database(data):
    global DB
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    DB = data

DB = load_database()

# Element definitions
ELEMENT_NAMES = {
    0: {"th": "ไม้", "en": "Wood", "color": "#315B4A", "class": "elem-wood"},
    1: {"th": "ไฟ", "en": "Fire", "color": "#8F3A4C", "class": "elem-fire"},
    2: {"th": "ดิน", "en": "Earth", "color": "#8A6548", "class": "elem-earth"},
    3: {"th": "ทอง", "en": "Metal", "color": "#69716F", "class": "elem-metal"},
    4: {"th": "น้ำ", "en": "Water", "color": "#4C7080", "class": "elem-water"},
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
    (0, 6), (6, 0),   # ชวด - มะเมีย
    (1, 7), (7, 1),   # ฉลู - มะแม
    (2, 8), (8, 2),   # ขาล - วอก
    (3, 9), (9, 3),   # เถาะ - ระกา
    (4, 10), (10, 4), # มะโรง - จอ
    (5, 11), (11, 5)  # มะเส็ง - กุน
]

def _stem_zh_to_index(zh):
    for idx, s in enumerate(DB["heavenlyStems"]):
        if s.get("chinese") == zh or s.get("zh") == zh:
            return idx
    return 0

def _branch_zh_to_index(zh):
    for idx, b in enumerate(DB["earthlyBranches"]):
        if b.get("chinese") == zh or b.get("zh") == zh:
            return idx
    return 0

def calculate_year_pillar(year, month, day):
    """
    Adhering to ExampleDuduang formula:
    Year changes on February 4th.
    Base anchor is year 1926.
    """
    if year > 2400:
        ce_year = year - 543
    else:
        ce_year = year
        
    birth_date = date(ce_year, month, day)
    year_change_date = date(ce_year, 2, 4)
    
    if birth_date < year_change_date:
        year_cycle = ce_year - 1927
    else:
        year_cycle = ce_year - 1926
        
    year_up_index = ((2 + year_cycle) % 10 + 10) % 10
    year_down_index = ((2 + year_cycle) % 12 + 12) % 12
    return year_up_index, year_down_index

def calculate_day_pillar(year, month, day):
    """
    Adhering to ExampleDuduang formula:
    start_date = date(1926, 12, 1)
    days_passed = (birth_date - start_date).days
    day_up_index = days_passed % 10
    day_down_index = days_passed % 12
    """
    if year > 2400:
        ce_year = year - 543
    else:
        ce_year = year
        
    start_date = date(1926, 12, 1)
    birth_date = date(ce_year, month, day)
    days_passed = (birth_date - start_date).days
    
    day_up_index = ((days_passed % 10) + 10) % 10
    day_down_index = ((days_passed % 12) + 12) % 12
    return day_up_index, day_down_index

def calculate_month_pillar(year_stem_idx, year, month, day):
    """
    Adhering to ExampleDuduang formula:
    Uses table_rasi_month_down and table_rasi_month_up
    with buddhist_year_last_digit = (year + 543) % 10
    """
    if year > 2400:
        ce_year = year - 543
    else:
        ce_year = year
        
    buddhist_year = ce_year + 543
    buddhist_year_last_digit = str(buddhist_year % 10)
    
    month_down_list = DB.get("example_source", {}).get("table_rasi_month_down", [])
    month_up_list = DB.get("example_source", {}).get("table_rasi_month_up", [])
    
    month_down_index = 0
    month_up_index = 0
    
    for index, month_data in enumerate(month_down_list):
        start_month, start_day = month_data["start"]
        end_month, end_day = month_data["end"]
        
        if start_month <= end_month:
            start_point = (start_month, start_day)
            end_point = (end_month, end_day)
            birth_point = (month, day)
            
            if start_point <= birth_point <= end_point:
                month_down_zh = month_data["zh"]
                month_down_index = _branch_zh_to_index(month_down_zh)
                
                row = month_up_list[index]
                month_up_zh = row.get(buddhist_year_last_digit, "甲")
                month_up_index = _stem_zh_to_index(month_up_zh)
                break
        else:
            # Over year boundary, e.g. Dec 8 - Jan 5
            if (
                (month == start_month and day >= start_day) or
                (month == end_month and day <= end_day) or
                (month > start_month) or
                (month < end_month)
            ):
                month_down_zh = month_data["zh"]
                month_down_index = _branch_zh_to_index(month_down_zh)
                
                row = month_up_list[index]
                month_up_zh = row.get(buddhist_year_last_digit, "甲")
                month_up_index = _stem_zh_to_index(month_up_zh)
                break
                
    return month_up_index, month_down_index

def calculate_hour_pillar(day_stem_idx, hour, minute=0):
    """
    Adhering to ExampleDuduang formula:
    Uses table_rasi_hour with day_stem_zh
    If hour is None, returns None, None
    """
    if hour is None:
        return None, None
        
    day_stem_obj = DB["heavenlyStems"][day_stem_idx]
    day_stem_zh = day_stem_obj.get("chinese", "甲")
    
    table_hour = DB.get("example_source", {}).get("table_rasi_hour", {})
    hour_list = table_hour.get(day_stem_zh, [])
    
    for hour_data in hour_list:
        start_h, start_m = hour_data["start"]
        end_h, end_m = hour_data["end"]
        
        if start_h > end_h:
            # Crosses midnight: 23:00 - 00:59
            if (hour > start_h or (hour == start_h and minute >= start_m)) or \
               (hour < end_h or (hour == end_h and minute <= end_m)):
                h_up_zh = hour_data["up"]
                h_down_zh = hour_data["down"]
                return _stem_zh_to_index(h_up_zh), _branch_zh_to_index(h_down_zh)
        else:
            start_point = (start_h, start_m)
            end_point = (end_h, end_m)
            birth_point = (hour, minute)
            if start_point <= birth_point <= end_point:
                h_up_zh = hour_data["up"]
                h_down_zh = hour_data["down"]
                return _stem_zh_to_index(h_up_zh), _branch_zh_to_index(h_down_zh)
                
    return 0, 0

def evaluate_bazi_chart(year, month, day, hour=None, minute=0):
    """
    Comprehensive BaZi Evaluation:
    Adheres 100% to ExampleDuduang 4 pillars calculation while preserving
    all advanced evaluation metrics: Day Master strength scoring, 5 element roles,
    favorable/unfavorable elements, and full personality & destiny meaning.
    """
    year_stem_idx, year_branch_idx = calculate_year_pillar(year, month, day)
    day_stem_idx, day_branch_idx = calculate_day_pillar(year, month, day)
    month_stem_idx, month_branch_idx = calculate_month_pillar(year_stem_idx, year, month, day)
    hour_stem_idx, hour_branch_idx = calculate_hour_pillar(day_stem_idx, hour, minute)
    
    chart_stems = [hour_stem_idx, day_stem_idx, month_stem_idx, year_stem_idx]
    chart_branches = [hour_branch_idx, day_branch_idx, month_branch_idx, year_branch_idx]
    
    # Stem objects
    stem_objs = []
    for s_idx in chart_stems:
        if s_idx is not None:
            obj = dict(DB["heavenlyStems"][s_idx])
            obj["zh"] = obj.get("chinese", "")
            obj["color"] = DB.get("rasiColor", {}).get(obj["zh"], "#315B4A")
            e_idx = obj.get("elementIndex", 0)
            pol = obj.get("polarity", "+")
            pol_sign = "+" if pol == "+" else "-"
            pol_label = "บวก" if pol == "+" else "ลบ"
            e_name = ELEMENT_NAMES.get(e_idx, {"th": "ไม่ระบุ", "en": "Unknown", "class": "elem-none", "color": "#888"})
            obj["elem_th"] = e_name["th"]
            obj["elem_en"] = e_name["en"]
            obj["elem_class"] = e_name["class"]
            obj["elem_polarity_th"] = f"ธาตุ{e_name['th']}{pol_label} ({pol_sign})"
            obj["elem_polarity_en"] = f"{e_name['en']} ({pol_sign})"
            obj["polarity_sign"] = pol_sign
            obj["polarity_label"] = pol_label
            stem_objs.append(obj)
        else:
            stem_objs.append({
                "index": None,
                "code": "-",
                "thaiName": "ไม่ระบุ",
                "chinese": "-",
                "zh": "-",
                "elementIndex": -1,
                "polarity": "-",
                "polarity_sign": "-",
                "polarity_label": "-",
                "symbol": "ไม่ระบุเวลาเกิด",
                "pros": "-",
                "cons": "-",
                "advice": "-",
                "elem_class": "elem-none",
                "elem_th": "ไม่ระบุ",
                "elem_en": "Unknown",
                "elem_polarity_th": "ไม่ระบุ",
                "elem_polarity_en": "Unknown",
                "line2_th": "-",
                "line2_en": "-",
                "line3_th": "-",
                "line3_en": "-",
                "is_dm": False,
                "color": "#888888"
            })
            
    # Branch objects
    branch_objs = []
    for b_idx in chart_branches:
        if b_idx is not None:
            b_obj = dict(DB["earthlyBranches"][b_idx])
            b_obj["zh"] = b_obj.get("chinese", "")
            e_idx = b_obj.get("elementIndex", 0)
            pol = b_obj.get("polarity", "+")
            pol_sign = "+" if pol == "+" else "-"
            pol_label = "บวก" if pol == "+" else "ลบ"
            e_name = ELEMENT_NAMES.get(e_idx, {"th": "ไม่ระบุ", "en": "Unknown", "class": "elem-none", "color": "#888"})
            b_obj["elem_th"] = e_name["th"]
            b_obj["elem_en"] = e_name["en"]
            b_obj["elem_class"] = e_name["class"]
            b_obj["elem_polarity_th"] = f"ธาตุ{e_name['th']}{pol_label} ({pol_sign})"
            b_obj["elem_polarity_en"] = f"{e_name['en']} ({pol_sign})"
            b_obj["polarity_sign"] = pol_sign
            b_obj["polarity_label"] = pol_label
            branch_objs.append(b_obj)
        else:
            branch_objs.append({
                "index": None,
                "thaiName": "ไม่ระบุ",
                "animal": "-",
                "chinese": "-",
                "zh": "-",
                "elementIndex": -1,
                "polarity": "-",
                "polarity_sign": "-",
                "polarity_label": "-",
                "group": "-",
                "standardHour": "-",
                "trait": "-",
                "elem_class": "elem-none",
                "elem_th": "ไม่ระบุ",
                "elem_en": "Unknown",
                "elem_polarity_th": "ไม่ระบุ",
                "elem_polarity_en": "Unknown",
                "line2_th": "-",
                "line2_en": "-",
                "line3_th": "-",
                "line3_en": "-"
            })
            
    # Day Master
    dm_stem = stem_objs[1]
    dm_elem = dm_stem["elementIndex"] # 0=Wood, 1=Fire, 2=Earth, 3=Metal, 4=Water
    dm_zh = dm_stem.get("chinese", "甲")
    
    # Meaning from ExampleDuduang
    meaning_data = DB.get("elementMeaning", {}).get(dm_zh, {})
    dm_meaning = {
        "title": meaning_data.get("title", dm_stem.get("thaiName", "")),
        "good": meaning_data.get("good", dm_stem.get("pros", "")),
        "bad": meaning_data.get("bad", dm_stem.get("cons", "")),
        "advice": meaning_data.get("advice", dm_stem.get("advice", ""))
    }
    
    # 5 Element Relationships
    peer_elem = dm_elem
    resource_elem = (dm_elem - 1 + 5) % 5
    output_elem = (dm_elem + 1) % 5
    wealth_elem = (dm_elem + 2) % 5
    power_elem = (dm_elem + 3) % 5
    
    # Scoring (Hour, Day, Month, Year)
    half_branches = DB["scoringRules"]["halfScoreBranchesBySelfElement"].get(str(dm_elem), [])
    total_score = 0.0
    max_score = 8.5 if hour_stem_idx is not None else 6.5
    
    # Stems scoring
    stems_to_score = []
    if hour_stem_idx is not None:
        stems_to_score.append((0, 1.0))
    stems_to_score.extend([(2, 1.0), (3, 1.0)])
    
    for idx, pos_weight in stems_to_score:
        elem = stem_objs[idx]["elementIndex"]
        if elem in [peer_elem, resource_elem]:
            total_score += pos_weight
            
    # Branches scoring
    branches_to_score = []
    if hour_branch_idx is not None:
        branches_to_score.append((0, branch_objs[0], 1.0))
    branches_to_score.extend([
        (1, branch_objs[1], 1.5),
        (2, branch_objs[2], 2.0),
        (3, branch_objs[3], 1.0),
    ])
    
    for b_idx, b_obj, pos_weight in branches_to_score:
        b_elem = b_obj["elementIndex"]
        b_num = b_obj["index"]
        
        if b_elem in [peer_elem, resource_elem]:
            score = pos_weight
        elif b_num is not None and b_num in half_branches:
            score = pos_weight / 2.0
        else:
            score = 0.0
            
        # Clash penalty
        if score > 0 and b_num is not None:
            has_clash = False
            if b_idx > 0 and chart_branches[b_idx - 1] is not None and (b_num, chart_branches[b_idx - 1]) in CLASH_PAIRS:
                has_clash = True
            if b_idx < 3 and chart_branches[b_idx + 1] is not None and (b_num, chart_branches[b_idx + 1]) in CLASH_PAIRS:
                has_clash = True
                
            if has_clash and not (dm_elem == 2 and b_elem == 2):
                score = max(0.0, score - 0.5)
                
        total_score += score
        
    score_ratio = total_score / max_score
    if score_ratio < 0.50:
        strength_code = "WEAK"
        strength_th = "อ่อน"
        strength_en = "Weak"
        strength_badge_class = "status-weak"
        fav_elems = [peer_elem, resource_elem]
        unfav_elems = [output_elem, wealth_elem, power_elem]
    elif score_ratio < 0.60:
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
            "full_en": "Represents allies, business partners, and peer strength.",
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
            "full_en": "Channels wisdom outward into creative output, persuasive speech, and strategy.",
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
            "full_en": "Governs financial instincts, wealth generation, resource management, and tangible assets.",
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
            "full_en": "Controls leadership presence, social status, organizational prestige, and self-discipline.",
            "is_favorable": power_elem in fav_elems
        }
    ]
    
    # Hour animal
    hour_animal_th = branch_objs[0].get("animal", "-") if hour_branch_idx is not None else "ไม่ระบุ"
    hour_animal_en = branch_objs[0].get("elem_en", "-") if hour_branch_idx is not None else "Unknown"
    
    # Day Master personality
    core_personality_th = dm_meaning.get("good", "")
    core_personality_en = dm_stem.get("pros", "")
    
    return {
        "chart_stems": chart_stems,
        "chart_branches": chart_branches,
        "stem_objs": stem_objs,
        "branch_objs": branch_objs,
        "hour_animal_th": hour_animal_th,
        "hour_animal_en": hour_animal_en,
        "day_master": {
            "stem": dm_stem,
            "elem_index": dm_elem,
            "elem_name_th": ELEMENT_NAMES[dm_elem]["th"],
            "elem_name_en": ELEMENT_NAMES[dm_elem]["en"],
            "meaning": dm_meaning,
            "personality_th": core_personality_th,
            "personality_en": core_personality_en,
        },
        "total_score": round(total_score, 1),
        "score_percent": min(100, int((total_score / max_score) * 100)),
        "strength_code": strength_code,
        "strength_th": strength_th,
        "strength_en": strength_en,
        "strength_badge_class": strength_badge_class,
        "favorable_elements": [
            {
                "index": e,
                "name_th": ELEMENT_NAMES[e]["th"],
                "name_en": ELEMENT_NAMES[e]["en"],
                "color": ELEMENT_NAMES[e]["color"],
                "class": ELEMENT_NAMES[e]["class"]
            } for e in fav_elems
        ],
        "unfavorable_elements": [
            {
                "index": e,
                "name_th": ELEMENT_NAMES[e]["th"],
                "name_en": ELEMENT_NAMES[e]["en"],
                "color": ELEMENT_NAMES[e]["color"],
                "class": ELEMENT_NAMES[e]["class"]
            } for e in unfav_elems
        ],
        "element_roles": element_roles_data,
        "pillar_interpretations": DB.get("pillarInterpretations", {}),
    }
