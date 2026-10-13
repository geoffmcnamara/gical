# 📅 gical.py

A lightweight, beautiful command-line calendar viewer written in Python. It fetches your iCal feed (such as Google Calendar) and renders a clean, multi-day terminal block layout complete with event times, titles, and optional weather reports.

---

## ✨ Features

- 🖥️ **Terminal-Optimized Layout:** Dynamically calculates terminal columns to display a clean side-by-side card view of your upcoming schedule.
- 🔄 **Recurring Event Support:** Fully parses recurring iCal rules using `recurring_ical_events`.
- 🌤️ **Weather Integration:** Optional weather forecasting pulled straight via `wttr.in`.
- 🛠️ **Developer Friendly:** Built-in test harness and robust argument parsing using `docopt`.

---

## ⚙️ Prerequisites & Dependencies

`gical.py` relies on a few Python packages, including your custom helper module `gtoolz` hosted on GitHub.

- Python 3.8+
- `docopt`
- `requests`
- `icalendar`
- `recurring_ical_events`
- `gtoolz` (automatically installed via GitHub)

---

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gical.git
   cd gical
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 Usage

Run the script directly from your terminal:

```bash
gical.py
```

### Options

- `-h`, `--help`: Show the help message and available options.
- `-d <DAYS>`: Number of days to display in the grid (default is `7`).
- `-w`, `--weather`: Display a current weather report below your schedule.

Example showing 10 days with weather:
```bash
gical.py -d 10 -w
```

---

## 📝 Configuration

`gical.py` looks for a configuration file to grab your private iCal URL and weather location. It checks the following paths:

- `~/.config/gical/gical.ini`
- `~/.config/gical/gical.conf`
- `~/.config/gical/config.ini`
- `~/.config/gical/config.conf`

Example `config.ini` structure:
```ini
[settings]
secret_ics_url = https://calendar.google.com/calendar/ical/.../basic.ics
weather_location = Your+City,ST
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.