import sys
import os
import datetime
import pytz
import base64

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QSpinBox, QPushButton,
    QCheckBox, QFormLayout, QHBoxLayout, QVBoxLayout, QCalendarWidget, QToolButton
)
from PyQt6.QtCore import QLocale, Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QTextCharFormat, QColor, QFont

# --- CONFIGURATION ---
APP_DATA_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'StravaActivityGenerator')
CONFIG_FILE_PATH = os.path.join(APP_DATA_PATH, 'config.cfg')
OUTPUT_FOLDER_PATH = os.path.join(os.path.expanduser('~/Documents'), 'Strava Activity Generator')

DEFAULT_TIMEZONE = 'Europe/Warsaw'
TRAINING_DAYS = [2, 4] # Tuesday and Thursday
WEEKDAY_TEXT_COLOR = "#e0e0e0"
WEEKEND_TEXT_COLOR = "#ff6347"

# --- ICONS (BASE64 ENCODED) ---
LEFT_ARROW_B64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgAQMAAABJtOi3AAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAZQTFRF/EwC7UsGq+ltZgAAABNJREFUeJxjZAACxsFJNDQwMAAADnABIU6p3/gAAAAASUVORK5CYII="
RIGHT_ARROW_B64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgAQMAAABJtOi3AAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAZQTFRF/EwC7UsGq+ltZgAAABNJREFUeJxjZAACxsFJNDQwMAAADnABIU6p3/gAAAAASUVORK5CYII="

# --- CORE LOGIC FUNCTIONS ---
def load_config():
    os.makedirs(APP_DATA_PATH, exist_ok=True)
    if not os.path.exists(CONFIG_FILE_PATH): 
        # Default last_number is 0, so the first workout starts at #1
        return {'base_name': 'Muay Thai', 'last_number': 0}
    
    config = {}
    with open(CONFIG_FILE_PATH, 'r') as f:
        for line in f:
            if '=' in line: config[line.strip().split('=', 1)[0]] = line.strip().split('=', 1)[1]
    config['last_number'] = int(config.get('last_number', 0))
    return config

def save_config(config_data):
    os.makedirs(APP_DATA_PATH, exist_ok=True)
    with open(CONFIG_FILE_PATH, 'w') as f:
        f.write(f"base_name={config_data['base_name']}\n")
        f.write(f"last_number={config_data['last_number']}\n")

def find_next_training_day(start_date):
    next_day = start_date + datetime.timedelta(days=1)
    while next_day.isoweekday() not in TRAINING_DAYS:
        next_day += datetime.timedelta(days=1)
    return next_day

def create_gpx_file(start_datetime, duration_minutes, workout_name, timezone_str):
    try:
        os.makedirs(OUTPUT_FOLDER_PATH, exist_ok=True)
        
        local_tz = pytz.timezone(timezone_str)
        start_time_local = local_tz.localize(start_datetime)
        end_time_local = start_time_local + datetime.timedelta(minutes=duration_minutes)
        start_time_utc = start_time_local.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_utc = end_time_local.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        safe_filename = workout_name.replace(' ', '_').replace('#', '') + '.gpx'
        
        full_path = os.path.join(OUTPUT_FOLDER_PATH, safe_filename)
        
        gpx_template = f"""<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1" creator="Workout Generator" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"><metadata><time>{start_time_utc}</time></metadata><trk><name>{workout_name}</name><trkseg><trkpt lat="0" lon="0"><time>{start_time_utc}</time></trkpt><trkpt lat="0" lon="0"><time>{end_time_utc}</time></trkpt></trkseg></trk></gpx>"""
        with open(full_path, 'w') as f:
            f.write(gpx_template)
        return safe_filename, None
    except Exception as e:
        return None, str(e)

# --- STYLESHEET (QSS) ---
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
    
    QPushButton#GenerateButton {{
        background-color: {STRAVA_ORANGE}; color: white; font-weight: bold;
        border: none; border-radius: 4px; padding: 8px 16px;
    }}
    QPushButton#GenerateButton:hover {{ background-color: #e04402; }}
    QPushButton#GenerateButton:pressed {{ background-color: #c73c02; }}
    
    QPushButton#OpenFolderButton {{
        background-color: {LIGHT_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
        font-weight: bold;
        border-radius: 4px; padding: 6px 12px;
    }}
    QPushButton#OpenFolderButton:hover {{ background-color: #4a4a4a; }}
    QPushButton#OpenFolderButton:disabled {{ color: #707070; }}

    QCheckBox::indicator:unchecked {{
        background-color: {LIGHT_BACKGROUND}; border: 1px solid {BORDER_COLOR};
        border-radius: 3px;
    }}
    QCheckBox::indicator:checked {{
        background-color: {STRAVA_ORANGE}; border: 1px solid {STRAVA_ORANGE};
        border-radius: 3px;
    }}
    
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {STRAVA_ORANGE}; border-radius: 4px;
    }}
    QCalendarWidget QToolButton {{
        color: white; font-size: 14px; font-weight: bold;
        background-color: transparent; border: none;
    }}
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

# --- MAIN APPLICATION CLASS ---
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.init_ui()
        self.setStyleSheet(STYLESHEET)

    def init_ui(self):
        self.setWindowTitle("Strava Activity Generator")
        self.resize(630, 275)
        
        # Left Panel: Form Layout
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
        
        form_layout.addRow("Base name:", self.name_entry)
        form_layout.addRow("Workout number:", self.number_spinbox)
        form_layout.addRow("Time (HH:MM):", time_layout)
        form_layout.addRow("Duration (min):", self.duration_entry)
        
        left_vbox = QVBoxLayout()
        left_vbox.addLayout(form_layout)
        
        self.auto_advance_check = QCheckBox("Automatically set next date (Tue/Thu)")
        self.auto_advance_check.setChecked(True)
        left_vbox.addWidget(self.auto_advance_check)
        
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate GPX File")
        self.generate_button.setObjectName("GenerateButton")
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.setObjectName("OpenFolderButton")
        self.open_folder_button.setEnabled(os.path.exists(OUTPUT_FOLDER_PATH))
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.open_folder_button)
        left_vbox.addLayout(button_layout)
        
        self.status_label = QLabel("")
        left_vbox.addWidget(self.status_label)
        left_vbox.addStretch(1)

        # Right Panel: Calendar Widget
        self.calendar = QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.findChild(QToolButton, "qt_calendar_monthbutton").setEnabled(False)
        self.calendar.setLocale(QLocale(QLocale.Language.English))
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.calendar.setGridVisible(True)
        
        weekday_format = QTextCharFormat()
        weekday_format.setForeground(QColor(WEEKDAY_TEXT_COLOR))
        weekday_format.setBackground(QColor(LIGHT_BACKGROUND)) 
        weekday_format.setFontWeight(QFont.Weight.Bold)
        
        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor(WEEKEND_TEXT_COLOR))
        weekend_format.setBackground(QColor(LIGHT_BACKGROUND))
        weekend_format.setFontWeight(QFont.Weight.Bold)

        for day in range(1, 6): # Monday - Friday
            self.calendar.setWeekdayTextFormat(Qt.DayOfWeek(day), weekday_format)
        
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)

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

        # Main Layout
        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_vbox)
        main_layout.addWidget(self.calendar)
        
        # Connect signals to methods
        self.generate_button.clicked.connect(self.generate)
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.number_spinbox.valueChanged.connect(self.on_config_changed)
        self.name_entry.textChanged.connect(self.on_config_changed)

    # --- ACTION METHODS ---
    def on_config_changed(self):
        base_name = self.name_entry.text().strip()
        current_number_for_next_workout = self.number_spinbox.value()
        
        self.config['base_name'] = base_name
        self.config['last_number'] = current_number_for_next_workout - 1
        
        save_config(self.config)

    def open_output_folder(self):
        try:
            os.startfile(os.path.realpath(OUTPUT_FOLDER_PATH))
        except Exception as e:
            self.status_label.setText(f"Error opening folder: {e}")
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")
    
    def generate(self):
        try:
            base_name = self.name_entry.text().strip()
            if not base_name: raise ValueError("Base name cannot be empty.")
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
            self.status_label.setText(f"Success! Created file: {filename}")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.open_folder_button.setEnabled(True)

            if self.auto_advance_check.isChecked():
                next_date = find_next_training_day(date_val)
                self.calendar.setSelectedDate(next_date)
                self.calendar.setCurrentPage(next_date.year, next_date.month)
                
        except (ValueError, TypeError) as e:
            self.status_label.setText(f"Error: Please check the input data. {e}")
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")
        except Exception as e:
            self.status_label.setText(f"An error occurred: {e}")
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")

# --- APPLICATION LAUNCHER ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    if os.path.exists("icon.ico"):
        app.setWindowIcon(QIcon("icon.ico"))
    window.show()
    sys.exit(app.exec())
