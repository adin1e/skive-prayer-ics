import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Copenhagen")

MOSQUE_ID = "skive"

def get_prayer_times():
    url = f"https://api.mawaqit.net/api/2.0/mosque/{MOSQUE_ID}"
    data = requests.get(url).json()

    # Mawaqit giver dagens tider her:
    times = data["data"]["times"]["today"]

    return {
        "Fajr": times[0],
        "Dhuhr": times[2],
        "Asr": times[3],
        "Maghrib": times[5],
        "Isha": times[6],
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
