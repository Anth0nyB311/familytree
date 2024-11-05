import curses
import calendar
from datetime import datetime


def display_calendar(family_members):
    important_dates = [] # makes a list awating for dates
    for person in family_members: # gets all the people in the family
        dob = person.dob
        if dob.lower() != 'na': # so if the person has a date of birth
            try:
                dob_date = datetime.strptime(dob, '%Y-%m-%d') # get nessary information
                death_date = None
                if person.death_date and person.death_date.lower() != 'na':
                    death_date = datetime.strptime(
                        person.death_date, '%Y-%m-%d') # get the death date if possible
                important_dates.append({
                    'name': person.name,  # start making the list
                    'month': dob_date.month,
                    'day': dob_date.day,
                    'dob': dob_date,
                    'death_date': death_date
                })
            except ValueError:
                pass # skip if there is no valid dob

    def generate_month_calendar(year, month, birthdays):
        month_cal = calendar.monthcalendar(year, month) # get the month calendar
        lines = []
        month_name = calendar.month_name[month]
        header = f"{month_name}".center(16) # tells what month we are in now
        lines.append(header)
        weekdays = "Mo Tu We Th Fr Sa Su" # the days of the week
        lines.append(weekdays)
        for week in month_cal: # build the calendar
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

    def get_ordinal_suffix(day): # get the suffix for the day so the first day will be 1st and the second day will be 2nd
        if 11 <= day <= 13:
            return 'th'
        else:
            return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    def main(stdscr):
        current_month = datetime.now().month # gets the pc month
        year = datetime.now().year # gets the pc year to calculate the ages
        curses.curs_set(0)
        stdscr.keypad(True) # allows the user to use the arrow keys
        try:
            while True:
                stdscr.clear() # clear the screen
                height, width = stdscr.getmaxyx() # get the height and width of the terminal
                birthdays_in_month = {}
                for person in important_dates: # get the birthdays of the people in the month
                    if person['month'] == current_month:
                        day = person['day'] # get the day
                        if day not in birthdays_in_month:
                            birthdays_in_month[day] = [] # make a list of birthdays
                        today = datetime.today()
                        if person['death_date']: # if the person is dead
                            age_at_death = person['death_date'].year - person['dob'].year - (
                                (person['death_date'].month, person['death_date'].day) < (
                                    person['dob'].month, person['dob'].day))
                            birthdays_in_month[day].append({ # add the person to the list
                                'name': person['name'],
                                'age_at_death': age_at_death,
                                'death_date': person['death_date'],
                                'dob': person['dob'],
                                'is_alive': False
                            })
                        else: # if the person is alive
                            age = today.year - person['dob'].year - (
                                (today.month, today.day) < (person['dob'].month, person['dob'].day)
                            )
                            birthdays_in_month[day].append({ # add the person to the list
                                'name': person['name'],
                                'age': age,
                                'dob': person['dob'],
                                'is_alive': True
                            })

                days_with_birthdays = list(birthdays_in_month.keys()) # get the days with birthdays
                cal_lines = generate_month_calendar( # get the calendar
                    year, current_month, days_with_birthdays)

                idx = 0
                for line in cal_lines: # display the calendar
                    if idx < height - 1:
                        stdscr.addstr(idx, 0, line[:width])
                    idx += 1
                idx += 1
                if idx < height - 1:
                    stdscr.addstr(idx, 0, "Birthdays:")

                idx += 1
                for day in sorted(birthdays_in_month): # display the birthdays
                    if idx < height - 1:
                        suffix = get_ordinal_suffix(day)
                        month_name = calendar.month_name[current_month]
                        for person in birthdays_in_month[day]: # display the person
                            if person['is_alive']:
                                birthday_line = f"{day}{suffix} {month_name}: {person['name']} Age {person['age']}"
                            else: # if the person is dead
                                death_suffix = get_ordinal_suffix(
                                    person['death_date'].day)
                                death_month_name = calendar.month_name[person['death_date'].month]
                                death_date_str = f"{person['death_date'].day}{death_suffix} {death_month_name} {person['death_date'].year}"
                                birthday_line = f"{day}{suffix} {month_name}: {person['name']} Age at Death {person['age_at_death']} (Died on the {death_date_str})"
                            stdscr.addstr(idx, 0, birthday_line[:width])
                            idx += 1

                if idx < height - 1: # display the instructions
                    stdscr.addstr(
                        idx + 1, 0, "Use arrow keys to navigate, 'X' to exit.")

                stdscr.refresh()
                key = stdscr.getch() # get the key pressed
                if key == curses.KEY_RIGHT or key == curses.KEY_DOWN: # move to the next month
                    current_month += 1
                    if current_month > 12:
                        current_month = 1
                        year += 1
                elif key == curses.KEY_LEFT or key == curses.KEY_UP: # move to the previous month
                    current_month -= 1
                    if current_month < 1:
                        current_month = 12
                        year -= 1
                elif key in (ord('x'), ord('X')): # exit the program
                    break
        except KeyboardInterrupt:
            pass # if the user presses ctrl+c then exit

    curses.wrapper(main) # run the program
