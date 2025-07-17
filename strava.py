import sys
import os
import datetime
import pytz
import base64

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QSpinBox, QPushButton,
    QCheckBox, QFormLayout, QHBoxLayout, QVBoxLayout, QCalendarWidget, QToolButton,
    QTableView
)
from PyQt6.QtCore import QLocale, Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QTextCharFormat, QColor, QFont

# --- KONFIGURACJA ---
CONFIG_FILE = 'config.cfg'
DEFAULT_TIMEZONE = 'Europe/Warsaw'
# Wtorek = 2, Czwartek = 4 (standard PyQt: poniedziałek=1)
TRENING_DNI_TYGODNIA = [2, 4] 
WEEKDAY_TEXT_COLOR = "#e0e0e0"
WEEKEND_TEXT_COLOR = "#ff6347" # Czerwono-pomarańczowy dla weekendów

# --- IKONY (ZAKODOWANE W BASE64) ---
LEFT_ARROW_B64 = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAAAdklEQVRo3u3XwQkAIAwEwX6iH6iP6jgkKJH4L03gfuED83s2BkSICEiSBGxJgEwSgKQE4ElC4P8s4Anx+fCe0wTQFQMYfQEw/gIw/gCAWQBYBoBVADANADMAkADQASAB8HvzXzZgB4gIAcnS5QE20y8q43YxGQAAAABJRU5ErkJggg=="
RIGHT_ARROW_B64 = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAAAd0lEQVRo3u3XQQoAIAwEwPz/02kHdGGQ5hQyq3vRkge92QIiQgQkScCWBExJgEwSgKQE4ElCoH8W8AR5+vC+0wTQFQMYfQEw/gIw/gCAWQBYBoBVADANADMAkADQASABcPt7Mxs1AQkRkCRJlp4BYBwzYSPw9xMAAAAASUVORK5CYII="
CHECKMARK_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABmJLR0QA/wD/AP+gvaeTAAABHklEQVR4nO3aMUoDURhF4d9gIYiNjaVg8wNYWfgOFr6AhYWNYi8k2HgFNjb2BiGFYGMhNBCSBJck7uBu5jH/ne+EcO7cWQgAAAAAAIC/wni8fOa122kAx3E0eY6zbY/X22mASZKkKSLNsa633QzgAsA6gAcAZgA4A/AfgF8AzgC4AHAXwD+AbwD8C7BnAM4A/AfgG4A/AOcA/gH4BWDPAPwEcAfAdQBfAO8A+ArgO4A7AN8A7gC8A7gD8A3gDuAPAP8A3AG8A+AOwDeAOwDvAG4A/AI4A3AG4BvAGYA/AOcAfgK4A/ANwBmA/wBcAdgH8A9g3wC8AdgD8AfgHcAbgD8A7gA8A/gGcATgC8AZgK8ANgC8AVgD8AfgHcAbgH8A/gAAAADAc/kA2a/c3jXM9W4AAAAASUVORK5CYII="


# --- LOGIKA PROGRAMU (BEZ ZMIAN) ---
def load_config():
    if not os.path.exists(CONFIG_FILE): return {'base_name': 'Muay Thai', 'last_number': 59}
    config = {}
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            if '=' in line: config[line.strip().split('=', 1)[0]] = line.strip().split('=', 1)[1]
    config['last_number'] = int(config.get('last_number', 0))
    return config

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        f.write(f"base_name={config_data['base_name']}\n")
        f.write(f"last_number={config_data['last_number']}\n")

def find_next_training_day(start_date):
    next_day = start_date + datetime.timedelta(days=1)
    while next_day.isoweekday() not in TRENING_DNI_TYGODNIA:
        next_day += datetime.timedelta(days=1)
    return next_day

def create_gpx_file(start_datetime, duration_minutes, workout_name, timezone_str):
    try:
        local_tz = pytz.timezone(timezone_str)
        start_time_local = local_tz.localize(start_datetime)
        end_time_local = start_time_local + datetime.timedelta(minutes=duration_minutes)
        start_time_utc = start_time_local.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_utc = end_time_local.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        safe_filename = workout_name.replace(' ', '_').replace('#', '') + '.gpx'
        gpx_template = f"""<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1" creator="Workout Generator" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"><metadata><time>{start_time_utc}</time></metadata><trk><name>{workout_name}</name><trkseg><trkpt lat="0" lon="0"><time>{start_time_utc}</time></trkpt><trkpt lat="0" lon="0"><time>{end_time_utc}</time></trkpt></trkseg></trk></gpx>"""
        with open(safe_filename, 'w') as f:
            f.write(gpx_template)
        return safe_filename, None
    except Exception as e:
        return None, str(e)


# --- ARKUSZ STYLÓW QSS ---
STRAVA_ORANGE = "#FC4C02"
DARK_BACKGROUND = "#282828"
LIGHT_BACKGROUND = "#3a3a3a"
TEXT_COLOR = "#f0f0f0"
BORDER_COLOR = "#505050"


STYLESHEET = f"""
    QWidget {{
        background-color: {DARK_BACKGROUND}; color: {TEXT_COLOR};
        font-family: Arial; font-size: 13px;
    }}
    QLabel {{ padding-top: 2px; }}
    QLineEdit, QSpinBox {{
        background-color: {LIGHT_BACKGROUND}; border: 1px solid {BORDER_COLOR};
        border-radius: 4px; padding: 5px;
    }}
    QLineEdit:focus, QSpinBox:focus {{ border: 1px solid {STRAVA_ORANGE}; }}
    QSpinBox::up-button, QSpinBox::down-button {{ width: 18px; }}
    
    QPushButton {{
        background-color: {STRAVA_ORANGE}; color: white; font-weight: bold;
        border: none; border-radius: 4px; padding: 8px 16px;
    }}
    QPushButton:hover {{ background-color: #e04402; }}
    QPushButton:pressed {{ background-color: #c73c02; }}
    
    QCheckBox::indicator:unchecked {{
        background-color: {LIGHT_BACKGROUND}; border: 1px solid {BORDER_COLOR};
        border-radius: 3px;
    }}
    QCheckBox::indicator:checked {{
        background-color: {STRAVA_ORANGE}; border: 1px solid {STRAVA_ORANGE};
        border-radius: 3px;
        image: url(data:image/png;base64,{CHECKMARK_PNG_B64});
    }}
    
    /* --- KALENDARZ --- */
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {STRAVA_ORANGE}; border-radius: 4px;
    }}
    QCalendarWidget QToolButton {{
        color: white; font-size: 14px; font-weight: bold;
        background-color: transparent; border: none;
    }}
    /* POPRAWKA: Ukrycie strzałki przy nazwie miesiąca */
    QCalendarWidget QToolButton#qt_calendar_monthbutton::menu-indicator {{
        image: none;
    }}
    QCalendarWidget QTableView {{
        background-color: {LIGHT_BACKGROUND};
        selection-background-color: {STRAVA_ORANGE};
    }}
    QCalendarWidget QAbstractItemView:enabled {{ color: {TEXT_COLOR}; }}
    QCalendarWidget QAbstractItemView:disabled {{ color: #707070; }}
    
    QCalendarWidget QMenu {{ background-color: {LIGHT_BACKGROUND}; }}
    QCalendarWidget QSpinBox {{
        color: white; background-color: transparent; border: none;
    }}
"""

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.init_ui()
        self.setStyleSheet(STYLESHEET)

    def init_ui(self):
        self.setWindowTitle("Strava Activity Generator")
        
        # ... (reszta UI jest taka sama)
        form_layout = QFormLayout()
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(12)
        self.name_entry = QLineEdit(self.config.get('base_name', 'Muay Thai'))
        self.number_spinbox = QSpinBox(minimum=1, maximum=9999, value=self.config['last_number'] + 1)
        time_layout = QHBoxLayout()
        self.hour_spinbox = QSpinBox(minimum=0, maximum=23, value=20)
        self.minute_spinbox = QSpinBox(minimum=0, maximum=59, value=30)
        self.minute_spinbox.setSpecialValueText("00")
        time_layout.addWidget(self.hour_spinbox)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.minute_spinbox)
        time_layout.addStretch()
        self.duration_entry = QLineEdit("90")
        self.duration_entry.setFixedWidth(50)
        form_layout.addRow("Nazwa bazowa:", self.name_entry)
        form_layout.addRow("Numer treningu:", self.number_spinbox)
        form_layout.addRow("Godzina (GG:MM):", time_layout)
        form_layout.addRow("Czas trwania (min):", self.duration_entry)
        left_vbox = QVBoxLayout()
        left_vbox.addLayout(form_layout)
        self.auto_advance_check = QCheckBox("Automatycznie ustaw następny termin (Wt/Czw)")
        self.auto_advance_check.setChecked(True)
        left_vbox.addWidget(self.auto_advance_check)
        self.generate_button = QPushButton("Generuj plik GPX")
        left_vbox.addWidget(self.generate_button)
        self.status_label = QLabel("")
        left_vbox.addWidget(self.status_label)
        left_vbox.addStretch(1)

        self.calendar = QCalendarWidget()
        # Wyłączenie bocznej kolumny z numerami tygodni
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        # Wyłączenie rozwijanej listy miesięcy (czyni przycisk nieklikalnym)
        self.calendar.findChild(QToolButton, "qt_calendar_monthbutton").setEnabled(False)
        
        self.calendar.setLocale(QLocale(QLocale.Language.Polish))
        self.calendar.setGridVisible(True)
        
        # Stylizacja kolorów tekstu dni tygodnia
        weekday_format = QTextCharFormat()
        weekday_format.setForeground(QColor(WEEKDAY_TEXT_COLOR))
        weekday_format.setBackground(QColor(LIGHT_BACKGROUND)) 
        weekday_format.setFontWeight(QFont.Weight.Bold)
        
        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor(WEEKEND_TEXT_COLOR))
        weekend_format.setBackground(QColor(LIGHT_BACKGROUND))
        weekend_format.setFontWeight(QFont.Weight.Bold)

        for day in range(1, 6): # Poniedziałek - Piątek
            self.calendar.setWeekdayTextFormat(Qt.DayOfWeek(day), weekday_format)
        
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)

        # Ustawienie ikon strzałek
        left_pixmap = QPixmap()
        left_pixmap.loadFromData(base64.b64decode(LEFT_ARROW_B64))
        right_pixmap = QPixmap()
        right_pixmap.loadFromData(base64.b64decode(RIGHT_ARROW_B64))
        prev_button = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        next_button = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if prev_button and next_button:
            prev_button.setIcon(QIcon(left_pixmap))
            prev_button.setIconSize(QSize(16, 16))
            next_button.setIcon(QIcon(right_pixmap))
            next_button.setIconSize(QSize(16, 16))

        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_vbox)
        main_layout.addWidget(self.calendar)
        self.generate_button.clicked.connect(self.generate)

    def generate(self):
        try:
            base_name = self.name_entry.text().strip()
            if not base_name: raise ValueError("Nazwa bazowa nie może być pusta.")
            workout_number = self.number_spinbox.value()
            workout_name = f"{base_name} #{workout_number}"
            date_val = self.calendar.selectedDate().toPyDate()
            hour, minute, duration = self.hour_spinbox.value(), self.minute_spinbox.value(), int(self.duration_entry.text())
            start_datetime = datetime.datetime(date_val.year, date_val.month, date_val.day, hour, minute)
            filename, error = create_gpx_file(start_datetime, duration, workout_name, DEFAULT_TIMEZONE)
            if error: raise Exception(error)
            
            self.config.update({'base_name': base_name, 'last_number': workout_number})
            save_config(self.config)
            
            self.number_spinbox.setValue(workout_number + 1)
            self.status_label.setText(f"Sukces! Stworzono plik: {filename}")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

            if self.auto_advance_check.isChecked():
                next_date = find_next_training_day(date_val)
                self.calendar.setSelectedDate(next_date)
                self.calendar.setCurrentPage(next_date.year, next_date.month)
                
        except (ValueError, TypeError) as e:
            self.status_label.setText(f"Błąd: Sprawdź wprowadzone dane. {e}")
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")
        except Exception as e:
            self.status_label.setText(f"Wystąpił błąd: {e}")
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())