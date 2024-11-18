"""Family calendar"""

import curses
import sys
import subprocess
import calendar
from datetime import datetime


def generate_month_calendar(year, month, birthdays):
    """Get the correct day and month format"""
    month_cal = calendar.monthcalendar(year, month)
    lines = []
    month_name = calendar.month_name[month]
    header = f"{month_name}".center(16)
    lines.append(header)
    weekdays = "Mo Tu We Th Fr Sa Su"
    lines.append(weekdays)
    for week in month_cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "   "
            else:
                if day in birthdays:
                    day_str = f"{day:2}*"
                else:
                    day_str = f"{day:2} "
                week_str += day_str + " "
        lines.append(week_str.rstrip())
    return lines


def get_ordinal_suffix(day):
    """Get the suffix for the day so first day will be 1st and the second day will be 2nd."""
    if 11 <= day <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def get_birthdays_in_month(important_dates, current_month, current_year):
    """Process important_dates to get birthdays in the current month."""
    birthdays_in_month = {}
    current_date = datetime(current_year, current_month, 1)
    for person in important_dates:
        if person["month"] == current_month:
            day = person["day"]
            if day not in birthdays_in_month:
                birthdays_in_month[day] = []
            if person["death_date"]:
                age_at_death = (
                    person["death_date"].year
                    - person["dob"].year
                    - (
                        (person["death_date"].month, person["death_date"].day)
                        < (person["dob"].month, person["dob"].day)
                    )
                )
                birthdays_in_month[day].append(
                    {
                        "name": person["name"],
                        "age_at_death": age_at_death,
                        "death_date": person["death_date"],
                        "dob": person["dob"],
                        "is_alive": False,
                    }
                )
            else:
                age = (
                    current_date.year
                    - person["dob"].year
                    - (
                        (current_date.month, current_date.day)
                        < (person["dob"].month, person["dob"].day)
                    )
                )
                birthdays_in_month[day].append(
                    {
                        "name": person["name"],
                        "age": age,
                        "dob": person["dob"],
                        "is_alive": True,
                    }
                )
    return birthdays_in_month


def format_birthday_line(day, person, current_month):
    """Format the birthday line for display."""
    suffix = get_ordinal_suffix(day)
    month_name = calendar.month_name[current_month]
    if person["is_alive"]:
        birthday_line = (
            f"{day}{suffix} {month_name}: {person['name']} " f"Age {person['age']}"
        )
    else:
        death_suffix = get_ordinal_suffix(person["death_date"].day)
        death_month_name = calendar.month_name[person["death_date"].month]
        death_date_str = (
            f"{person['death_date'].day}{death_suffix} "
            f"{death_month_name} {person['death_date'].year}"
        )
        birthday_line = (
            f"{day}{suffix} {month_name}: {person['name']} "
            f"Age at Death {person['age_at_death']} "
            f"(Died on the {death_date_str})"
        )
    return birthday_line


def handle_user_input(key, current_month, year):
    """Handles user input for navigation."""
    if key in (curses.KEY_RIGHT, curses.KEY_DOWN):
        current_month += 1
        if current_month > 12:
            current_month = 1
            year += 1
    elif key in (curses.KEY_LEFT, curses.KEY_UP):
        current_month -= 1
        if current_month < 1:
            current_month = 12
            year -= 1
    elif key in (ord("x"), ord("X")):
        return False, current_month, year  # Signal to exit
    return True, current_month, year


def render_calendar(stdscr, cal_lines, birthdays_in_month, current_month):
    """Renders the calendar and birthdays to the screen."""
    height, width = stdscr.getmaxyx()
    idx = 0
    for line in cal_lines:
        if idx < height - 1:
            stdscr.addstr(idx, 0, line[:width])
        idx += 1

    idx += 1
    if idx < height - 1:
        stdscr.addstr(idx, 0, "Birthdays:")
    idx += 1

    for day in sorted(birthdays_in_month):
        for person in birthdays_in_month[day]:
            if idx < height - 1:
                birthday_line = format_birthday_line(day, person, current_month)
                stdscr.addstr(idx, 0, birthday_line[:width])
                idx += 1

    if idx < height - 1:
        stdscr.addstr(idx + 1, 0, "Use arrow keys to navigate, 'X' to exit.")


def display_calendar(family_members):
    """Display the family calendar."""
    important_dates = []
    for person in family_members:
        dob = person.dob
        if dob.lower() != "na":
            try:
                dob_date = datetime.strptime(dob, "%Y-%m-%d")
                death_date = None
                if person.death_date and person.death_date.lower() != "na":
                    death_date = datetime.strptime(person.death_date, "%Y-%m-%d")
                important_dates.append(
                    {
                        "name": person.name,
                        "month": dob_date.month,
                        "day": dob_date.day,
                        "dob": dob_date,
                        "death_date": death_date,
                    }
                )
            except ValueError:
                pass  # skip if there is no valid dob

    def main(stdscr):
        """Main function for curses."""
        current_month = datetime.now().month
        year = datetime.now().year
        curses.curs_set(0)
        stdscr.keypad(True)
        try:
            while True:
                stdscr.clear()
                birthdays_in_month = get_birthdays_in_month(
                    important_dates, current_month, year
                )
                days_with_birthdays = list(birthdays_in_month.keys())
                cal_lines = generate_month_calendar(
                    year, current_month, days_with_birthdays
                )

                render_calendar(stdscr, cal_lines, birthdays_in_month, current_month)

                stdscr.refresh()
                key = stdscr.getch()
                continue_loop, current_month, year = handle_user_input(
                    key, current_month, year
                )
                if not continue_loop:
                    break
        except KeyboardInterrupt:
            pass  # Exit on Ctrl+C

    curses.wrapper(main)
if __name__ == "__main__":
    subprocess.run([sys.executable, "start.py"],check=True)
