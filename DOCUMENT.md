# Bazi Calculation Specification (ข้อกำหนดระบบและลอจิกการคำนวณ)

This document specifies the variable structures, mathematical logic, and calculation algorithms for Chinese Bazi / Four Pillars of Destiny (ดวงจีนโป๊ยหยี่สี่เถียว) for processing on a web application (สำหรับประมวลผลบนเว็บแอปพลิเคชัน).

---

## 1. System Variables (ตัวแปรของระบบ)

### 1.1 User Inputs (ข้อมูลนำเข้าจากผู้ใช้)
* `birth_day`: Solar birth day (วันเกิดทางสุริยคติ) (1 - 31)
* `birth_month`: Solar birth month (เดือนเกิดทางสุริยคติ) (1 - 12)
* `birth_year`: Birth year in CE / Gregorian or BE (ปีเกิด ค.ศ. หรือ พ.ศ.)
* `birth_time`: Birth time in hours and minutes, e.g., `14:30` (เวลาเกิด ชั่วโมงและนาที เช่น `14:30`)

### 1.2 Constants & Database Reference Tables (ค่าคงที่และตารางอ้างอิง)
* `LIST_HEAVENLY_STEMS_ELEMENT`: 10 Heavenly Stem elements (ธาตุราศีบน 10 ตัว) `['ม+', 'ม-', 'ฟ+', 'ฟ-', 'ด+', 'ด-', 'ท+', 'ท-', 'น+', 'น-']`
* `LIST_HEAVENLY_STEMS_NAME`: 10 Heavenly Stem names (ชื่อราศีบน 10 ตัว) `['กะ', 'อิก', 'เปี้ย', 'เต็ง', 'โบ่ว', 'กี้', 'แก', 'ซิง', 'ยิ้ม', 'กุ่ย']`
* `LIST_EARTHLY_BRANCHES_NAME`: 12 Earthly Branch names (ชื่อราศีล่าง 12 ตัว) `['ชวด', 'ฉลู', 'ขาล', 'เถาะ', 'มะโรง', 'มะเส็ง', 'มะเมีย', 'มะแม', 'วอก', 'ระกา', 'จอ', 'กุน']`
* `LIST_EARTHLY_BRANCHES_ELEM`: 12 Earthly Branch elements (ธาตุราศีล่าง 12 ตัว) `['น+', 'ด-', 'ม+', 'ม-', 'ด+', 'ฟ-', 'ฟ+', 'ด-', 'ท+', 'ท-', 'ด+', 'น-']`
* `MATRIX_FIVE_TIGERS`: Month Stem lookup table of size 12 x 5, row starts from Tiger month (ตารางหาธาตุเดือนบน ขนาด 12 x 5 เริ่มนับแถวจากเดือนขาล)
* `MATRIX_FIVE_RATS`: Hour Stem lookup table of size 12 x 5, row starts from Rat hour (ตารางหายามบน ขนาด 12 x 5 เริ่มนับแถวจากยามชวด)
* `POSITION_WEIGHTS`: Position weight scores for 8 positions (ค่าน้ำหนักคะแนนประจำตำแหน่ง 8 ตำแหน่ง) `[1.0, 0.0, 1.0, 1.0, 1.0, 1.5, 2.0, 1.0]`
* `HALF_SCORE_BRANCHES`: List of storage / late-season Earth branches containing hidden root elements matching Day Master (รายชื่อกิ่งดินคลัง/ดินปลายฤดูที่แฝงพลังตามธาตุดิถี)
* `BRANCH_CLASH_PAIRS`: 6 Earthly Branch clash pairs (คู่ปะทะ [ชง] ราศีล่าง 6 คู่)

### 1.3 Calculated Outputs (ค่าผลลัพธ์จากการคำนวณ)
* `chart_stems[4]`: 4 Heavenly Stems array (อาเรย์ราศีบน 4 หลัก) `[Hour Stem / ยามบน, Day Stem / วันบน, Month Stem / เดือนบน, Year Stem / ปีบน]`
* `chart_branches[4]`: 4 Earthly Branches array (อาเรย์ราศีล่าง 4 หลัก) `[Hour Branch / ยามล่าง, Day Branch / วันล่าง, Month Branch / เดือนล่าง, Year Branch / ปีล่าง]`
* `day_master_element`: Day Master element (ธาตุดิถีประจำตัว) (0=Wood / ไม้, 1=Fire / ไฟ, 2=Earth / ดิน, 3=Metal / ทอง, 4=Water / น้ำ)
* `element_relationships`: Five element relationships relative to Day Master (ความสัมพันธ์ของธาตุทั้ง 5 เทียบกับดิถี) (Peer / คู่ธาตุ, Resource / ก่อเกิด, Output / ถ่ายเท, Wealth / โชคลาภ, Power / พิฆาต)
* `total_score`: Day Master strength score (คะแนนพลังความแข็งแรงของดิถี)
* `chart_strength`: Day Master strength level (ระดับพลังดิถี) (`WEAK` / อ่อน, `BALANCED` / สมดุล, `STRONG` / แข็งแรง)
* `favorable_elements`: List of favorable elements / like (รายการธาตุที่ให้คุณ [ชอบ])
* `unfavorable_elements`: List of unfavorable elements / dislike (รายการธาตุที่ให้โทษ [ไม่ชอบ])

---

## 2. Calculation Steps and Logic (ขั้นตอนและลอจิกการคำนวณ)

### 2.1 Year Pillar Calculation (คำนวณหลักปี)
* **Year Change Boundary (เกณฑ์เปลี่ยนปี)**: Birth date before February 4 uses `birth_year - 1`; birth date on or after February 4 uses `birth_year` (วันเกิดก่อน 4 กุมภาพันธ์ ใช้ `birth_year - 1` ตั้งแต่วันที่ 4 กุมภาพันธ์ขึ้นไป ใช้ `birth_year`)
* **Reference Epoch (จุดอ้างอิง)**: Year BE 2527 / CE 1984 is index 0 - Jia Zi / Yang Wood Rat (ปี พ.ศ. 2527 / ค.ศ. 1984 เป็นลำดับ 0 [ปี กะชวด / 甲子])
* **Calculation Formula (สูตรคำนวณ)**:
  * `diff_year = target_year - 2527`
  * `year_stem_index = ((diff_year % 10) + 10) % 10`
  * `year_branch_index = ((diff_year % 12) + 12) % 12`
* **Recorded Values (บันทึกค่า)**: `chart_stems[3] = year_stem_index`, `chart_branches[3] = year_branch_index`

### 2.2 Day Pillar Calculation (คำนวณหลักวัน)
* **Day Change Boundary (เกณฑ์เปลี่ยนวัน)**: Day resets at 00:00 (รีเซ็ตวันใหม่เวลา 00:00 น.)
* **Calculation Formula (สูตรคำนวณ)**: Calculate actual day difference (`total_days`) from reference epoch date (คำนวณผลต่างจำนวนวันจริง `total_days` ห่างจากจุดอ้างอิง [Epoch Date]):
  * `day_stem_index = ((total_days % 10) + 10) % 10`
  * `day_branch_index = ((total_days % 12) + 12) % 12`
* **Recorded Values (บันทึกค่า)**: `chart_stems[1] = day_stem_index` (Day Master position / ตำแหน่งดิถี), `chart_branches[1] = day_branch_index`

### 2.3 Month Pillar Calculation (คำนวณหลักเดือน)
* Check birth date range to find Earthly Branch of the month (`month_branch_index`) according to solar terms / seasonal order, starting from Tiger=2 to Ox=1 (ตรวจสอบช่วงวันที่เกิดเพื่อหาราศีล่างของเดือน `month_branch_index` ตามลำดับสารทฤดูกาล เริ่มนับ ขาล=2 ถึง ฉลู=1)
* Group Year Stem (`year_stem_index`) into 5 groups (จัดกลุ่มราศีบนของปี `year_stem_index` ออกเป็น 5 กลุ่ม):
  * Group 0 (กลุ่ม 0): Jia / กะ (0), Ji / กี้ (5)
  * Group 1 (กลุ่ม 1): Yi / อิก (1), Geng / แก (6)
  * Group 2 (กลุ่ม 2): Bing / เปี้ย (2), Xin / ซิง (7)
  * Group 3 (กลุ่ม 3): Ding / เต็ง (3), Ren / ยิ้ม (8)
  * Group 4 (กลุ่ม 4): Wu / โบ่ว (4), Gui / กุ่ย (9)
* Retrieve `month_stem_index` from `MATRIX_FIVE_TIGERS[month_branch_row][year_group]` (ดึงค่า `month_stem_index` จาก `MATRIX_FIVE_TIGERS[month_branch_row][year_group]`)
* **Recorded Values (บันทึกค่า)**: `chart_stems[2] = month_stem_index`, `chart_branches[2] = month_branch_index`

### 2.4 Hour Pillar Calculation (คำนวณหลักยาม)
* Convert birth time into 12 Earthly Branch hour periods (`hour_branch_index`) (แปลงเวลาเกิดเป็นช่วงราศีล่าง 12 ยาม [`hour_branch_index`]):

| Time Range (ช่วงเวลา) | Earthly Branch (ราศีล่าง) | Index (ลำดับ Index) |
| :--- | :--- | :--- |
| 23:00 - 00:59 | Rat / ชวด (子) | 0 |
| 01:00 - 02:59 | Ox / ฉลู (丑) | 1 |
| 03:00 - 04:59 | Tiger / ขาล (寅) | 2 |
| 05:00 - 06:59 | Rabbit / เถาะ (卯) | 3 |
| 07:00 - 08:59 | Dragon / มะโรง (辰) | 4 |
| 09:00 - 10:59 | Snake / มะเส็ง (巳) | 5 |
| 11:00 - 12:59 | Horse / มะเมีย (午) | 6 |
| 13:00 - 14:59 | Goat / มะแม (未) | 7 |
| 15:00 - 16:59 | Monkey / วอก (申) | 8 |
| 17:00 - 18:59 | Rooster / ระกา (酉) | 9 |
| 19:00 - 20:59 | Dog / จอ (戌) | 10 |
| 21:00 - 22:59 | Pig / กุน (亥) | 11 |

* Group Day Stem (`day_stem_index`) into 5 groups following the same formula as Section 2.3 (จัดกลุ่มราศีบนของวัน `day_stem_index` เป็น 5 กลุ่มตามสูตรเดียวกับข้อ 2.3)
* Retrieve `hour_stem_index` from `MATRIX_FIVE_RATS[hour_branch_row][day_group]` (ดึงค่า `hour_stem_index` จาก `MATRIX_FIVE_RATS[hour_branch_row][day_group]`)
* **Recorded Values (บันทึกค่า)**: `chart_stems[0] = hour_stem_index`, `chart_branches[0] = hour_branch_index`

---

## 3. Five Elements Cycle & Day Master Strength Evaluation (การวิเคราะห์วงจรธาตุและการนับคะแนนดิถี)

### 3.1 Five Element Relationships (วงจรธาตุสัมพันธ์)
Defined 5 element codes: 0=Wood, 1=Fire, 2=Earth, 3=Metal, 4=Water (กำหนดรหัสธาตุ 5 ชนิด: 0=ไม้, 1=ไฟ, 2=ดิน, 3=ทอง, 4=น้ำ)
* Day Master Element (`Self` / ธาตุดิถี): `Self = day_stem_index % 5`
* Five Element relationships relative to Day Master (วงจรธาตุทั้ง 5 สัมพันธ์กับดิถี):
  * **Peer Element (ธาตุคู่ดิถี)**: `Self`
  * **Resource Element (ธาตุก่อเกิด)**: `(Self - 1 + 5) % 5`
  * **Output Element (ธาตุถ่ายเท)**: `(Self + 1) % 5`
  * **Wealth Element (ธาตุโชคลาภ)**: `(Self + 2) % 5`
  * **Power Element (ธาตุพิฆาต)**: `(Self + 3) % 5`

### 3.2 Position Weights (น้ำหนักคะแนนประจำตำแหน่ง)
Referencing all 8 positions in the chart (อ้างอิงตำแหน่งทั้ง 8 ช่องของรูปดวง):
* Heavenly Stems (ราศีบน): Hour Stem (ยามบน) = 1.0, Day Stem / Day Master (วันบน [ดิถี]) = 0.0, Month Stem (เดือนบน) = 1.0, Year Stem (ปีบน) = 1.0
* Earthly Branches (ราศีล่าง): Hour Branch (ยามล่าง) = 1.0, Day Branch / Spouse Palace (วันล่าง [ฐานคู่ครอง]) = 1.5, Month Branch / Season (เดือนล่าง [ฤดูกาล]) = 2.0, Year Branch (ปีล่าง) = 1.0

### 3.3 Scoring Rules & Conditions (เงื่อนไขการคำนวณคะแนน)
Iterate and evaluate across the 7 surrounding positions, skipping Day Stem position (วนลูปตรวจสอบทั้ง 7 ตำแหน่งแวดล้อม [ข้ามตำแหน่งวันบน]):
1. **Full Score (คะแนนเต็ม)**: When that position matches **Peer Element (ธาตุคู่ดิถี)** or **Resource Element (ธาตุก่อเกิด)**, add full position weight score (เมื่อตำแหน่งนั้นมีธาตุตรงกับ ธาตุคู่ดิถี หรือ ธาตุก่อเกิด ให้บวกคะแนนเต็มประจำตำแหน่ง)
2. **Half Score (คะแนนครึ่งหนึ่ง)**: If that position is a storage / late-season Earth branch containing hidden root energy matching Day Master element (according to `HALF_SCORE_BRANCHES` table), add only half position score (หากตำแหน่งนั้นเป็นกิ่งดินคลัง/ดินปลายฤดูที่แฝงพลังธาตุดิถี [ตามตาราง `HALF_SCORE_BRANCHES`] ให้บวกคะแนนเพียงครึ่งเดียว):
   * Day Branch (วันล่าง): `1.5 / 2 = 0.75`
   * Month Branch (เดือนล่าง): `2.0 / 2 = 1.0`
   * Other positions (ตำแหน่งอื่นๆ): `1.0 / 2 = 0.5`
3. **Zero Score (คะแนนศูนย์)**: If it is Output Element, Wealth Element, or Power Element, award 0 points (หากเป็นธาตุถ่ายเท, ธาตุโชคลาภ หรือธาตุพิฆาต ได้ 0 คะแนน)
4. **Clash Penalty Deduction (หักคะแนนกรณีปะทะ [ชง])**: If an Earthly Branch supporting the Day Master directly neighbors its clash pair, deduct 0.5 points from that position (except if Day Master is Earth element and Earth branches clash with each other, no points are deducted) (หากราศีล่างที่เป็นตัวช่วยดิถีอยู่ติดกับคู่ชงโดยตรง ให้หักคะแนนตำแหน่งนั้นออก 0.5 คะแนน [ยกเว้นดิถีธาตุดินแล้วดินชงกันเอง จะไม่หักคะแนน])

### 3.4 Strength Evaluation Criteria & Favorable/Unfavorable Elements (เกณฑ์ตัดสินความแข็งแรงและธาตุให้คุณ-ให้โทษ)

* Total Score (คะแนนรวม) < 4.5  -->  Weak Day Master (ดิถีอ่อน / WEAK)
* Total Score (คะแนนรวม) 4.5 - 4.99  -->  Balanced Day Master (ดิถีสมดุล / BALANCED)
* Total Score (คะแนนรวม) >= 5.0  -->  Strong Day Master (ดิถีแข็งแรง / STRONG)

* **Weak Day Master Case / Low energy, needs replenishing (กรณีดิถีอ่อน [พลังน้อย ต้องเติมพลัง])**:
  * Favorable Elements / Like (ธาตุให้คุณ [ชอบ]): Peer Element (ธาตุคู่ดิถี), Resource Element (ธาตุก่อเกิด)
  * Unfavorable Elements / Dislike (ธาตุให้โทษ [ไม่ชอบ]): Output Element (ธาตุถ่ายเท), Wealth Element (ธาตุโชคลาภ), Power Element (ธาตุพิฆาต)
* **Strong Day Master Case / Excess energy, needs venting or controlling (กรณีดิถีแข็งแรง [พลังล้น ต้องระบายหรือกดข่ม])**:
  * Favorable Elements / Like (ธาตุให้คุณ [ชอบ]): Wealth Element (ธาตุโชคลาภ), Output Element (ธาตุถ่ายเท), Power Element (ธาตุพิฆาต)
  * Unfavorable Elements / Dislike (ธาตุให้โทษ [ไม่ชอบ]): Peer Element (ธาตุคู่ดิถี), Resource Element (ธาตุก่อเกิด)
* **Balanced Day Master Case (กรณีดิถีสมดุล)**:
  * Favorable Elements / Like (ธาตุให้คุณ [ชอบ]): Resource Element (ธาตุก่อเกิด), Wealth Element (ธาตุโชคลาภ)
  * Unfavorable Elements / Dislike (ธาตุให้โทษ [ไม่ชอบ]): Peer Element (ธาตุคู่ดิถี [โดยเฉพาะคู่แข่ง/เกียบไช้])

---

## 4. Web Display Structure (โครงสร้างการแสดงผลหน้าเว็บ / Result Display)

### 4.1 Above the Fold Section (ข้อมูลส่วนหน้าแรก / Above the fold)
* 8-Cell Bazi Chart Table displaying element names, Chinese characters, Yin-Yang polarity, and zodiac animal images (ตารางรูปดวง 8 ช่อง แสดงชื่อธาตุ ตัวอักษรจีน ขั้วหยิน-หยาง และรูปสัตว์ประจำนักษัตร)
* Day Master Status Summary: Weak / Balanced / Strong along with energy score progress bar (สรุปสถานะดิถี: อ่อน / สมดุล / แข็งแรง พร้อมแถบคะแนนพลัง)
* Favorable Elements (Like) and Unfavorable Elements (Dislike) Summary Box (กล่องสรุปธาตุที่ให้คุณ [ชอบ] และธาตุที่ให้โทษ [ไม่ชอบ])
* Core Personality Analysis: Decoded from Day Master / Day Stem combined with the energy of birth month / Month Branch (บทวิเคราะห์บุคลิกภาพหลัก: ถอดรหัสจากธาตุดิถี [วันบน] ผสานกับพลังของเดือนเกิด [เดือนล่าง])

### 4.2 Deep Analysis Section (ข้อมูลส่วนวิเคราะห์เชิงลึก / Deep Analysis)
* 4 Pillars Predictions (Year, Month, Day, Hour) based on favorable/unfavorable element conditions (คำทำนายประจำ 4 เสา [ปี, เดือน, วัน, ยาม] ตามเงื่อนไขธาตุให้คุณ/ให้โทษ)
* Detection of Combinations (He / ภาคี) and Clashes (Chong / ปะทะ) within the chart (การตรวจจับคู่ภาคี [ฮะ] และคู่ปะทะ [ชง] ภายในรูปดวง)
* Career directions, businesses, auspicious colors, and fortune enhancements based on favorable element groups (ทิศทางอาชีพ ธุรกิจ สีสัน และการเสริมดวงชะตาตามกลุ่มธาตุที่ให้คุณ)