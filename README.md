# Duduang

A modern Chinese BaZi (Four Pillars of Destiny) fortune calculation and consultation web platform developed for Sikarn Pattarasirimongkol, integrating precise solar-astronomical algorithms, client record management, and personalized destiny consultations.

## Tech Stack

### Languages
* Python
* JavaScript
* HTML5
* CSS3

### Frontend
* Vanilla JavaScript (ES6+)
* Vanilla CSS (Modern Chinese Minimalist Design System)
* Google Fonts ('Inter' Latin Typography, 'Noto Sans Thai' Thai Typography, 'Cinzel', 'Ma Shan Zheng')
* Django Template Engine

### Backend & Database
* Django 5.2
* SQLite3
* JSON Data Store (User Store & BaZi Wisdom Grimoire)

### Tools & Libraries
* asgiref
* sqlparse
* tzdata

## Active Features

* **Authentic BaZi Four Pillars Engine** — Computes Heavenly Stems and Earthly Branches for Year, Month, Day, and Hour based on solar seasonal terms, matching reference calculations 100%.
* **Global Inter & Noto Sans Thai Typography** — Unified international font stack with enlarged scale (16px base) for exceptional legibility across both Thai and English.
* **3-Layer 50/50 Split Home Page** — Balanced full-screen dual box layout with left Yin and right Yang color panels, revolving central Yin-Yang layer, vertical decorative Chinese calligraphy, and prominent bottom-center title paired with an intuitive birth data input form.
* **Matching 50/50 Split Consultation Booking** — Harmonious dual-panel consultation template featuring Master Ning's photo, credentials, direct call/LINE action buttons, and consultation packages.
* **5-Row Grid BaZi Result Showcase** — Structured 5-row destiny layout featuring user metadata, an expansive Box 8 BaZi Elements with prominent calligraphy and explicit (+/-) polarities, Day Master strength and balance, personality analysis, and the Five Elemental Roles.
* **Admin Dashboard with 4 Clean Tabs** — Streamlined overview tab showing exactly two vital metrics (active users and total calculations), a user accounts tab with full CRUD (Add, Edit, Delete), a calculation history tab, and a BaZi wisdom book tab with editing and deletion capabilities.
* **Animated Yin-Yang Brand & Ambient Dynamics** — Rotating Yin-Yang brand logo with orbital rings and high-contrast ambient Yin-Yang background animation.
* **Bilingual & Theme Switching** — Instant client-side Thai/English language toggle and Dark/Light visual theme switching.

## Directory Structure

```text
Duduang/
├── .git/                                   # ⚠️ DO NOT TOUCH - Git version control
├── .gitignore                              # Git ignore specifications
├── DOCUMENT.md                             # Technical BaZi formula specification
├── README.md                               # Public project documentation (English)
├── manage.py                               # Django CLI entrypoint
├── requirements.txt                        # Python dependencies
├── db.sqlite3                              # ⚠️ SQLite database file
├── ExampleDuduang/                         # ⚠️ Reference prototype directory
├── docs/
│   └── private/
│       ├── setup_Duduang.md                # Setup guide and complete file map (Thai)
│       └── knowledge_Duduang.md            # Comprehensive codebase knowledge (Thai)
├── config/
│   ├── __init__.py                         # Python package marker
│   ├── asgi.py                             # ⚠️ ASGI deployment entry
│   ├── settings.py                         # Core Django application configuration
│   ├── urls.py                             # Root routing configuration
│   ├── views.py                            # Root view handlers
│   └── wsgi.py                             # ⚠️ WSGI deployment entry
├── bazi/
│   ├── __init__.py                         # Python package marker
│   ├── admin.py                            # Django admin registration
│   ├── apps.py                             # Bazi application configuration
│   ├── auth_service.py                     # User management service with CRUD (Create, Read, Update, Delete)
│   ├── calculation.py                      # BaZi astronomical calculation engine with +/- polarity badges
│   ├── models.py                           # Database schema (FortuneRecord)
│   ├── tests.py                            # Unit tests
│   ├── urls.py                             # Bazi app URL routes
│   ├── views.py                            # View controllers (Form, Result, Booking, History, Admin actions)
│   ├── data/
│   │   ├── bazi_database.json              # Adapted reference calendar & editable wisdom grimoire
│   │   └── users_database.json             # User accounts JSON database
│   └── migrations/
│       ├── 0001_initial.py                 # ⚠️ Initial database migration
│       └── __init__.py                     # Python package marker
├── static/
│   ├── .gitkeep                            # Directory placeholder
│   ├── css/                                # Custom stylesheets
│   │   ├── admin.css                       # Admin tabs, metric cards, and CRUD modals
│   │   ├── common.css                      # Global font stack (Inter + Noto Sans Thai) and reset
│   │   ├── dashboard.css                   # Dashboard statistical styles
│   │   ├── form.css                        # 3-layer 50/50 split layout
│   │   ├── login.css                       # Authentication card styles
│   │   ├── result.css                      # 5-row destiny layout with prominent Box 8 Elements
│   │   └── theme.css                       # Design tokens, enlarged typography, and Yin-Yang orb
│   ├── js/
│   │   └── main.js                         # Client-side interactivity and controllers
│   └── images/                             # Static visual assets (Master Ning photo, icons)
└── templates/
    ├── navbar.html                         # Top navigation bar with spinning Yin-Yang brand logo
    ├── form.html                           # 3-layer 50/50 split home page
    ├── booking.html                        # 3-layer 50/50 split consultation booking template
    ├── history.html                        # Calculation history template
    ├── login.html                          # Centered user authentication card
    ├── result.html                         # 5-row destiny result layout
    └── admin_dashboard.html                # 4-tab admin portal with user & wisdom CRUD
```

## Environment Variables

```env
# Admin PIN Authentication Code (default: 8888)
ADMIN_PIN=8888

# Django Security Settings
DEBUG=True
SECRET_KEY=your_secret_key_here
```
