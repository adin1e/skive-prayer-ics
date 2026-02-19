import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Copenhagen")

# Mawaqit ID for Skive (samme som hjemmesiden bruger)
MOSQUE_ID = "skive"

def get_prayer_times():
    url = f"https://api.mawaqit.net/api/2.0/mosque/{MOSQUE_ID}"
    data = requests.get(url).json()

    today = datetime.now().strftime("%Y-%m-%d")
    times = data["data"]["times"][today]

    return {
        "Fajr": times["Fajr"],
        "Dhuhr": times["Dhuhr"],
        "Asr": times["Asr"],
        "Maghrib": times["Maghrib"],
        "Isha": times["Isha"],
    }


def main():
    times = get_prayer_times()

    cal = Calendar()
    cal.add("prodid", "-//Prayer Times//")
    cal.add("version", "2.0")

    today = datetime.now(TZ).date()

    for name, time in times.items():
        hour, minute = map(int, time.split(":"))
        start = datetime(today.year, today.month, today.day, hour, minute, tzinfo=TZ)

        event = Event()
        event.add("summary", name)
        event.add("dtstart", start)
        event.add("dtend", start + timedelta(minutes=10))
        cal.add_component(event)

    with open("prayer.ics", "wb") as f:
        f.write(cal.to_ical())


if __name__ == "__main__":
    main()
