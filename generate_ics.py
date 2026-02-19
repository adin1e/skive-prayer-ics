from playwright.sync_api import sync_playwright
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import re

URL = "https://skiveprayertimes.dk/"

def fetch_html():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")
        html = page.content()
        browser.close()
        return html

def extract_times(html):
    prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    times = {}

    for prayer in prayers:
        match = re.search(rf"{prayer}.*?(\d{{1,2}}:\d{{2}})", html, re.IGNORECASE)
        if match:
            times[prayer] = match.group(1)

    return times

def main():
    html = fetch_html()
    times = extract_times(html)

    cal = Calendar()
    cal.add('prodid', '-//Prayer Times//')
    cal.add('version', '2.0')

    today = datetime.now().date()

    for name, time in times.items():
        hour, minute = map(int, time.split(":"))
        start = datetime(today.year, today.month, today.day, hour, minute)

        event = Event()
        event.add('summary', name)
        event.add('dtstart', start)
        event.add('dtend', start + timedelta(minutes=10))
        cal.add_component(event)

    with open("prayer.ics", "wb") as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    main()
