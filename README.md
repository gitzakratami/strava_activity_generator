# Strava Activity Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](https://opensource.org/licenses/MIT)

A sleek, dark-themed desktop application designed to quickly generate GPX files for manual Strava activities like gym workouts, yoga, or any GPS-less training. This tool eliminates the tedious process of adding activities one by one on the Strava website, allowing you to create and upload them in bulk.

![App Screenshot]([https://raw.githubusercontent.com/Kratax/strava-activity-generator/main/screenshot.png](https://github.com/gitzakratami/strava_activity_generator/blob/main/screenshots/scr1.png))
> **Note:** To update the screenshot, upload a new image to your repository and replace the URL above.

## Why This App Exists

Manually adding indoor or non-GPS activities to Strava can be a repetitive and time-consuming task. This application was built to solve that problem by providing a fast and intuitive interface to generate multiple activity files at once, which can then be batch-uploaded to Strava.

## Features

-   **Intuitive GUI:** A clean, user-friendly interface built with PyQt6.
-   **Strava-Themed Design:** A dark mode aesthetic inspired by the Strava color palette.
-   **Automatic Workout Numbering:** The app remembers your last workout number and automatically suggests the next one.
-   **Full Calendar View:** Easily select the date of your workout from a persistent calendar.
-   **Smart Date Advancement:** Automatically jumps to the next typical training day (e.g., Tuesday/Thursday) after generating a file.
-   **Organized Output:** All generated GPX files are saved in a dedicated `Strava Activity Generator` folder in your Documents.
-   **Quick Access:** An "Open Folder" button gives you immediate access to your generated files.
-   **Standalone & Installable:** Can be run as a portable `.exe` or installed on Windows using a professional installer.

## Installation

There are two ways to get the application.

#### 1. For Regular Users (Recommended)

Download the official installer from the latest **[Releases](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/releases)** page.

The installer will:
-   Place the application in your Program Files.
-   Create shortcuts on your Desktop and in the Start Menu.
-   Add an entry in "Add or remove programs" for easy uninstallation.

#### 2. Portable Version

If you prefer not to install, you can download the standalone `Strava_Activity_Generator.exe` file from the **[Releases](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/releases)** page and run it from any location.

## How to Use

1.  **Launch** the application.
2.  **Fill in the details:**
    -   `Base name`: The main title of your activity (e.g., "Gym Session", "Muay Thai").
    -   `Workout number`: The app will suggest the next number. You can override it if needed.
    -   `Time (HH:MM)`: The start time of your workout.
    -   `Duration (min)`: The total duration in minutes.
3.  **Select the Date** from the calendar on the right.
4.  Click **Generate GPX File**. A success message will appear.
5.  Repeat the process for all your other workouts.
6.  Click the **Open Folder** button. This will open the `Documents\Strava Activity Generator` folder.
7.  Go to [**strava.com/upload/select**](https://strava.com/upload/select), click "Choose files", and select all the `.gpx` files you just created.
8.  Edit the details for each activity on Strava and save. You're done!

## For Developers

Interested in building the project from the source? Here’s how.

#### Prerequisites

-   Python 3.x
-   Inno Setup (for creating the installer)

#### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
    cd YOUR_REPOSITORY
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    *(Create a `requirements.txt` file with `pyqt6` and `pytz` first)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application from source:**
    ```bash
    python your_script_name.py
    ```

#### Building

1.  **To create the standalone `.exe` file:**
    Use PyInstaller with the recommended settings. Make sure your icon file is in the same directory.
    ```bash
    pyinstaller --onefile --windowed --icon="strava_icon.ico" your_script_name.py
    ```
    The final `.exe` will be in the `dist` folder.

2.  **To create the Windows installer:**
    -   Install **[Inno Setup](https://jrsoftware.org/isdl.php)**.
    -   Open the `.iss` script file included in this repository with Inno Setup.
    -   Update the `Source` paths in the `[Files]` section to point to your generated `.exe` and `.ico` files.
    -   Click **Build -> Compile** (F9).

## Technologies Used

-   **Python:** Core application logic.
-   **PyQt6:** For the graphical user interface.
-   **PyInstaller:** To package the application into a standalone executable.
-   **Inno Setup:** To create the Windows installer.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
