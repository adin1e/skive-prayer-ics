from playwright.sync_api import sync_playwright
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

URL = "https://skiveprayertimes.dk/"
TZ = ZoneInfo("Europe/Copenhagen")

def get_text():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded")

        # Vent lidt så iframe loader
        page.wait_for_timeout(5000)

        # Hent AL tekst fra ALLE frames
        all_text = ""

        for frame in page.frames:
            try:
                all_text += frame.locator("body").inner_text()
            except:
                pass

        browser.close()
        return all_text


def extract_times(text):
    prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    times = {}

    for prayer in prayers:
        match = re.search(rf"{prayer}.*?(\d{{1,2}}:\d{{2}})", text, re.IGNORECASE)
        if match:
            times[prayer] = match.group(1)

    return times


def main():
    text = get_text()
    times = extract_times(text)

    if len(times) < 3:
        raise Exception(f"Kunne ikke finde tider. Fandt: {times}")

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
