from playwright.sync_api import sync_playwright
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

URL = "https://skiveprayertimes.dk/"
TZ = ZoneInfo("Europe/Copenhagen")

PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

def fetch_text_from_page_or_iframe():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)

        # Prøv at finde Mawaqit-iframe (tiderne ligger typisk der)
        frame = None
        for f in page.frames:
            if "mawaqit" in (f.url or ""):
                frame = f
                break

        if frame:
            # Hent synlig tekst fra iframe
            frame.wait_for_load_state("networkidle", timeout=60000)
            text = frame.locator("body").inner_text()
        else:
            # Fallback: prøv at læse fra hovedsiden
            text = page.locator("body").inner_text()

        browser.close()
        return text

def extract_times(text: str):
    times = {}
    # Matcher fx: "Fajr · 05:20" eller "Fajr 05:20"
    for name in PRAYERS:
        m = re.search(rf"\b{name}\b\s*(?:·|-|:)?\s*(\d{{1,2}}:\d{{2}})", text, re.IGNORECASE)
        if m:
            times[name] = m.group(1)
    return times

def main():
    text = fetch_text_from_page_or_iframe()
    times = extract_times(text)

    if len(times) < 3:
        raise SystemExit(f"Kunne ikke finde bønnetider. Fandt kun: {times}")

    cal = Calendar()
    cal.add("prodid", "-//Skive Prayer Times//")
    cal.add("version", "2.0")

    today = datetime.now(TZ).date()

    for name in PRAYERS:
        if name not in times:
            continue
        hhmm = times[name]
        hour, minute = map(int, hhmm.split(":"))
        start = datetime(today.year, today.month, today.day, hour, minute, tzinfo=TZ)

        e = Event()
        e.add("summary", name)
        e.add("dtstart", start)
        e.add("dtend", start + timedelta(minutes=10))
        e.add("dtstamp", datetime.now(TZ))
        e.add("uid", f"{today.isoformat()}-{name}@skiveprayertimes")
        cal.add_component(e)

    with open("prayer.ics", "wb") as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    main()
