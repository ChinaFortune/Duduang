/**
 * Bazi Application Client Logic
 * Handles Language detection & toggle (TH/EN), Theme toggle (Light/Dark),
 * Calendar picker sync, and Result page description switches.
 */

(function() {
    'use strict';

    // 1. LANGUAGE MANAGER
    const LangManager = {
        currentLang: 'th',
        
        init() {
            const savedLang = localStorage.getItem('bazi_lang');
            if (savedLang) {
                this.currentLang = savedLang;
            } else {
                // Auto-detect browser language
                const browserLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
                this.currentLang = browserLang.startsWith('th') ? 'th' : 'en';
                localStorage.setItem('bazi_lang', this.currentLang);
            }
            this.applyLanguage(this.currentLang);
            this.bindEvents();
        },

        applyLanguage(lang) {
            this.currentLang = lang;
            document.documentElement.setAttribute('lang', lang);
            
            // Update all elements with data-th and data-en
            const translatable = document.querySelectorAll('[data-th][data-en]');
            translatable.forEach(el => {
                const text = el.getAttribute(`data-${lang}`);
                if (text) {
                    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                        if (el.hasAttribute('placeholder')) {
                            el.placeholder = text;
                        }
                    } else {
                        el.innerHTML = text;
                    }
                }
            });

            // Update language toggle button text
            const langLabel = document.getElementById('current-lang-label');
            if (langLabel) {
                langLabel.textContent = lang === 'th' ? 'TH' : 'EN';
            }
        },

        toggle() {
            const nextLang = this.currentLang === 'th' ? 'en' : 'th';
            localStorage.setItem('bazi_lang', nextLang);
            this.applyLanguage(nextLang);
        },

        bindEvents() {
            const langBtn = document.getElementById('btn-lang-toggle');
            if (langBtn) {
                langBtn.addEventListener('click', () => this.toggle());
            }
        }
    };

    // 2. THEME MANAGER (Light / Dark)
    const ThemeManager = {
        currentTheme: 'dark',

        init() {
            const savedTheme = localStorage.getItem('bazi_theme');
            if (savedTheme) {
                this.currentTheme = savedTheme;
            } else {
                // Default to dark as requested, or match system
                this.currentTheme = 'dark';
            }
            this.applyTheme(this.currentTheme);
            this.bindEvents();
        },

        applyTheme(theme) {
            this.currentTheme = theme;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('bazi_theme', theme);

            const themeIcon = document.getElementById('theme-icon');
            if (themeIcon) {
                themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
            }
        },

        toggle() {
            const nextTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
            this.applyTheme(nextTheme);
        },

        bindEvents() {
            const themeBtn = document.getElementById('btn-theme-toggle');
            if (themeBtn) {
                themeBtn.addEventListener('click', () => this.toggle());
            }
        }
    };

    // 3. FORM CALENDAR & TIME CONTROLS
    const FormControls = {
        init() {
            const calBtn = document.getElementById('btn-calendar-trigger');
            const hiddenDatePicker = document.getElementById('hidden-date-picker');
            const daySelect = document.getElementById('birth_day');
            const monthSelect = document.getElementById('birth_month');
            const yearSelect = document.getElementById('birth_year');

            // Trigger calendar picker
            if (calBtn && hiddenDatePicker) {
                calBtn.addEventListener('click', () => {
                    try {
                        hiddenDatePicker.showPicker();
                    } catch (e) {
                        hiddenDatePicker.focus();
                        hiddenDatePicker.click();
                    }
                });

                hiddenDatePicker.addEventListener('change', (e) => {
                    if (!e.target.value) return;
                    const [y, m, d] = e.target.value.split('-').map(num => parseInt(num, 10));
                    if (daySelect) daySelect.value = d;
                    if (monthSelect) monthSelect.value = m;
                    if (yearSelect) yearSelect.value = y;
                });
            }

            // Sync Hour & Minute to hidden/full time
            const hourInput = document.getElementById('birth_hour');
            const minuteInput = document.getElementById('birth_minute');
            const fullTimeInput = document.getElementById('birth_time');

            const syncTime = () => {
                if (hourInput && minuteInput && fullTimeInput) {
                    const h = String(hourInput.value || '09').padStart(2, '0');
                    const m = String(minuteInput.value || '30').padStart(2, '0');
                    fullTimeInput.value = `${h}:${m}`;
                }
            };

            if (hourInput) hourInput.addEventListener('change', syncTime);
            if (minuteInput) minuteInput.addEventListener('change', syncTime);
        }
    };

    // 4. RESULT PAGE TOGGLES (Short vs Full description switchers)
    const ResultToggles = {
        init() {
            // Description toggle buttons
            const toggleBtns = document.querySelectorAll('.btn-desc-toggle');
            toggleBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const targetId = btn.getAttribute('data-target');
                    const container = document.getElementById(targetId);
                    if (!container) return;

                    const shortView = container.querySelector('.view-short');
                    const fullView = container.querySelector('.view-full');
                    const isShortActive = shortView.style.display !== 'none';

                    if (isShortActive) {
                        shortView.style.display = 'none';
                        fullView.style.display = 'block';
                        btn.textContent = LangManager.currentLang === 'th' ? 'ย่อสรุป' : 'Show Short';
                    } else {
                        shortView.style.display = 'block';
                        fullView.style.display = 'none';
                        btn.textContent = LangManager.currentLang === 'th' ? 'อ่านละเอียด' : 'Show Detailed';
                    }
                });
            });

            // Interpretation Dropdown / Accordion Toggles
            const accordions = document.querySelectorAll('.accordion-header');
            accordions.forEach(header => {
                header.addEventListener('click', () => {
                    const body = header.nextElementSibling;
                    const isOpen = body.style.display === 'block';
                    body.style.display = isOpen ? 'none' : 'block';
                    const icon = header.querySelector('.accordion-chevron');
                    if (icon) {
                        icon.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
                    }
                });
            });
        }
    };

    // 5. LOGIN / REGISTER TAB TOGGLE
    const AuthTabs = {
        init() {
            const tabLogin = document.getElementById('tab-btn-login');
            const tabRegister = document.getElementById('tab-btn-register');
            const formLogin = document.getElementById('form-login-pane');
            const formRegister = document.getElementById('form-register-pane');

            if (tabLogin && tabRegister && formLogin && formRegister) {
                tabLogin.addEventListener('click', () => {
                    tabLogin.classList.add('active');
                    tabRegister.classList.remove('active');
                    formLogin.style.display = 'block';
                    formRegister.style.display = 'none';
                });

                tabRegister.addEventListener('click', () => {
                    tabRegister.classList.add('active');
                    tabLogin.classList.remove('active');
                    formRegister.style.display = 'block';
                    formLogin.style.display = 'none';
                });
            }
        }
    };

    // Document Ready
    document.addEventListener('DOMContentLoaded', () => {
        LangManager.init();
        ThemeManager.init();
        FormControls.init();
        ResultToggles.init();
        AuthTabs.init();
    });

    // Expose for external calls if needed
    window.BaziApp = {
        LangManager,
        ThemeManager
    };

})();
