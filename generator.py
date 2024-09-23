import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tzlocal import get_localzone

from utils import read_json
from classes import Event
from constants import SCOPES, CALENDAR_NAME, COLORS_KEY


class Generator:
    def __init__(self, steps):
        self.steps = steps
        self.settings = read_json('config.json')

        self.creds = None
        self.service = None

        self.horizon = dt.datetime.today()

        self.timezone = str(get_localzone())

    def generate(self):
        # Set up connection and builds service with Google Calendar API
        self.service, service_fail = self.get_service()
        if service_fail:
            return None, f'ERROR while getting service: {service_fail}'

        # Gets or creates the calendar API, also deleting all the events in it
        cal_id, cal_fail = self.get_calendar()
        if cal_fail:
            return None, f'ERROR while getting calendar: {cal_fail}'

        # Generates the new events in the calendar
        success, events_fail = self.generate_events(cal_id)
        return success, f'ERROR while generating events: {events_fail}'

    def get_service(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json')

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        try:
            return build('calendar', 'v3', credentials=self.creds), None

        except HttpError as er:
            return None, er

    def get_calendar(self):
        try:
            cals = self.service.calendarList().list().execute().get('items', [])
            cal_bp = {'summary': CALENDAR_NAME, 'timeZone': self.timezone}

            cal_id = None

            for cal in cals:
                if cal.get('summary') == CALENDAR_NAME:
                    cal_id = cal['id']

            if not cal_id:
                cal_id = self.service.calendars().insert(body=cal_bp).execute()['id']

            events_result = self.service.events().list(calendarId=cal_id).execute()
            events = events_result.get('items', [])

            # Iterate over the events and delete each one
            for event in events:
                event_id = event['id']
                self.service.events().delete(calendarId=cal_id, eventId=event_id).execute()

            return cal_id, None
        except Exception as er:
            return None, er

    def generate_events(self, cal_id):
        events = []

        # Compile all tasks into a single event
        events += self.combine_tasks([step for step in self.steps if step.step_type == 'task'])

        # Iterates through the focuses and plots them onto horizon
        events += self.iterate_focuses([step for step in self.steps if step.step_type == 'focus'])

        try:
            for i, event in enumerate(events):
                print(f'GENERATING EVENT {i+1} OUT OF {len(events)}: ', event)

                event_table = {
                    'summary': event.summary,
                    'description': event.description,
                    'start': {'dateTime': event.start.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': self.timezone},
                    'end': {'dateTime': event.end.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': self.timezone},
                    'colorId': event.color_id,
                }

                self.service.events().insert(calendarId=cal_id, body=event_table).execute()

            return True, None
        except Exception as er:
            return None, er

    def combine_tasks(self, tasks):
        if not tasks: return []

        all_task_event = Event(tasks[0].name, tasks[0].content, '', '', COLORS_KEY[tasks[0].color])
        tasks.remove(tasks[0])
        for a in tasks:
            all_task_event.summary += f', {a.name}'
            all_task_event.description += f'\n{a.content}'

        dur = dt.timedelta(hours=self.settings['task_duration'])
        all_task_event.start = self.horizon
        all_task_event.end = self.horizon + dur

        return [all_task_event]

    def iterate_focuses(self, focuses):
        if not focuses: return []
        focuses.sort(key=lambda focus: focus.time_end)

        events = []
        horizon_end = self.settings['horizon']
        focus_idx = 0
        focuses_buffer = []

        while (self.horizon - dt.datetime.now()).days < horizon_end:
            poten_step = focuses[focus_idx]
            print('potential step and its index:', poten_step.name.upper(), focus_idx)
            horizon_day_of_week = self.horizon.strftime('%a').lower()

            def generate_event(step, idx):
                print(f'NOW CREATING EVENT: ', step.name.upper())

                #  If the current horizon is over the step's start_time, set the horizon to the next day
                if self.horizon.time() > step.time_start:
                    print(f'horizon time: {self.horizon.time()} is later than start time: {step.time_start}. setting horizon to next day: {dt.datetime.combine(self.horizon.date(), dt.time(0, 0, 0)) + dt.timedelta(1)}')
                    self.horizon = dt.datetime.combine(self.horizon.date(), dt.time(0, 0, 0)) + dt.timedelta(1)

                #  Sets horizon's time to step's start time
                s_t = (step.time_start.hour, step.time_start.minute, step.time_start.second)
                self.horizon = self.horizon.replace(hour=s_t[0], minute=s_t[1], second=s_t[2])

                # Gets the first item
                split_i = step.items.split('-')
                if len(split_i) > 1:
                    step.items = step.items[len(split_i[0]) + 1:]
                    summery = split_i[0]
                elif step.items == '':  # If there's no more items
                    summery = step.content
                else:  # There's one more item
                    summery = step.items
                    step.items = ''

                # Getting the duration of the focus
                common_date = dt.datetime(2000, 1, 1)
                d1 = dt.datetime.combine(common_date, step.time_start)
                d2 = dt.datetime.combine(common_date, step.time_end)
                dif = d2 - d1
                start = self.horizon
                self.horizon = self.horizon + dif
                end = self.horizon

                disc = f'{step.name.upper()}: {step.content}. \nGOAL: {step.goal}'

                event = Event(step.name.upper() + ': ' + summery, disc, start, end, COLORS_KEY[step.color])
                events.append(event)

                if idx == len(focuses) - 1:
                    print('RESETTING INDEX:', idx, len(focuses) - 1)
                    return 0
                else:
                    print(f'increasing index from {idx} to {idx + 1}. also {focuses[idx].name.upper()} to {focuses[idx+ 1].name.upper()}')
                    return idx + 1

            # If there's been steps that didn't fit the correct day
            if focuses_buffer:
                print(f'accessing focuses_buffer steps, number: {len(focuses_buffer)}')
                recalled_step = None
                for buffered_step in focuses_buffer:
                    print(f'in buffers: checking if current day:{horizon_day_of_week.upper()} NOW matches {buffered_step.name.upper()}s pref of {buffered_step.days}?')
                    bs_days = buffered_step.days.split('-')
                    if horizon_day_of_week in bs_days:
                        print(f"{buffered_step.name.upper()} step is NOW valid! {horizon_day_of_week.upper()} is NOW in {bs_days}. "
                              f"checking if current poten step's end time: {poten_step.name.upper()}:{poten_step.time_end} is before buffered step's start time: {buffered_step.time_start}")
                        if poten_step.time_end < buffered_step.time_start:   # If True should run potential step first becuase I can run both
                            generate_event(poten_step, focus_idx)
                        focuses_buffer.remove(buffered_step)
                        recalled_step = buffered_step
                        break

                if recalled_step:
                    focus_idx = focuses.index(recalled_step)
                    print(f'continue called. setting focus idx:{focus_idx} to idx of recalled step: {focuses.index(recalled_step)}')
                    continue

            days = poten_step.days.split('-')
            # If current step doesn't fit day
            if horizon_day_of_week not in days:
                print(f'potential step: {poten_step.name.upper()}s days:{days} doesnt fit horizon day: {horizon_day_of_week.upper()}, adding to buffer.')
                if poten_step not in focuses_buffer:
                    focuses_buffer.append(poten_step)
                else:
                    print('NEVERMIND POTEN STEP IS ALREADY IN BUFFER')

                if focus_idx == len(focuses) - 1:
                    print('RESETTING INDEX:', focus_idx, len(focuses) - 1)
                    focus_idx = 0
                    self.horizon = dt.datetime.combine(self.horizon.date(), dt.time(0, 0, 0)) + dt.timedelta(1)
                else:
                    print(f'increasing index from {focus_idx} to {focus_idx + 1}')
                    focus_idx += 1
                continue

            focus_idx = generate_event(poten_step, focus_idx)

        return events
