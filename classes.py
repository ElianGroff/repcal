from enum import Enum

from utils import val_time, get_datetime, read_json
from constants import *


class Mode(Enum):
    BLANK = 'MENU (commands: edit, settings) > '
    EDIT = 'EDITING (help for commands) > '
    CONFIG = 'SETTINGS (help for commands) > '


class Step:
    def __init__(self, step_type, step_id, name, content, datetime, color):
        self._step_type = step_type
        self.step_id = step_id
        self.name = name
        self.content = content
        self.datetime = datetime
        self.color = color

    def __repr__(self):
        return f'{self.name.upper()}: {self.content}. | Type: {self.step_type} | Datetime: {self.datetime} | Color: {self.color} |'

    def repr_sum(self):
        return f'{self.name.upper()}: {self.content}. | Type: {self.step_type} | Datetime: {self.datetime} | Color: {self.color} |'

    @property
    def step_type(self):
        return self._step_type

    @step_type.setter
    def step_type(self, value):
        if value in ('task', 'focus', 'goal'):
            self._step_type = value
        else:
            raise ValueError('INVALID STEP TYPE: Valid types include: "task", "focus", "goal"')

    @property
    def datetime(self):
        return self._datetime

    @datetime.setter
    def datetime(self, value):
        p_d = value.lower().strip()
        #&print(p_d)
        if converted_dt := get_datetime(p_d):
            self._datetime = converted_dt
        elif p_d == '':
            match self.step_type:
                case 'task':
                    self._datetime = TODAY + dt.timedelta(days=45)
                case 'focus':
                    self._datetime = TODAY + dt.timedelta(days=365)
                case 'goal':
                    self._datetime = TODAY + dt.timedelta(days=1826)  # Five years
        else:
            raise ValueError('INVALID DATETIME: Valid datetime formats include: "YYYY-MM-DD", "YYYY-MM-DD H:MM PM/AM", or "YYYY-MM-DD HH:MM:SS"')

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        processed_value = value.lower().strip()
        if processed_value in COLORS_KEY.keys():
            self._color = processed_value
        elif processed_value == '':
            if self.step_type == 'task':
                self._color = read_json('config.json')['default_task_color']
            elif self.step_type == 'focus':
                self._color = read_json('config.json')['default_focus_color']
            else:
                self._color = 'lavender'
        else:
            raise ValueError(ERRORS['InvalidColorError'])


class FocusStep(Step):
    def __init__(self, step_type, step_id, name, content, datetime, color, goal, time_start, time_end, items, days):
        super().__init__(step_type, step_id, name, content, datetime, color)
        self.goal = goal
        self.time_start = time_start
        self.time_end = time_end
        self.items = items
        self.days = days

    def __repr__(self):
        return (f'{self.name.upper()}: {self.content}. | Type: {self.step_type} | Datetime: {self.datetime} | Color: {self.color} |\n'
                f'Time_Start: {self.time_start} | Time_End: {self.time_end} | Days: {self.days}\n'
                f'Goal: {self.goal} | Items: {self.items}')

    @property
    def time_start(self):
        return self._time_start

    @time_start.setter
    def time_start(self, value):
        processed_value = value.lower().strip()
        if converted_time := val_time(processed_value):
            if hasattr(self, '_time_end') and self._time_end < converted_time:
                raise ValueError(ERRORS['InvalidTimeReversedError'])
            self._time_start = converted_time
        elif processed_value == '':
            self._time_start = val_time(DEFAULT_START_TIME)
        else:
            raise ValueError(ERRORS['InvalidTimeFormatError'])

    @property
    def time_end(self):
        return self._time_end

    @time_end.setter
    def time_end(self, value):
        processed_value = value.lower().strip()
        if converted_time := val_time(processed_value):
            if hasattr(self, '_time_start') and converted_time < self._time_start:
                raise ValueError(ERRORS['InvalidTimeReversedError'])
            self._time_end = converted_time
        elif processed_value == '':
            print('SETS', DEFAULT_END_TIME)
            self._time_end = val_time(DEFAULT_END_TIME)
            print(self._time_start)
        else:
            raise ValueError(ERRORS['InvalidTimeFormatError'])

    @property
    def days(self):
        return self._days

    @days.setter
    def days(self, value):
        processed_value = value.lower().strip()

        if processed_value == 'all':
            self._days = 'sun-mon-tue-wed-thu-fri-sat'
        else:
            days = value.split('-')

            for d in days:
                if d not in ('sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'):
                    raise ValueError(f'INVALID DAY VALUE. Valid values include: sun-mon-tue-wed-thu-fri-sat or all.')
            self._days = processed_value
class GoalStep(Step):
    def __init__(self, step_type, step_id, name, content, datetime, color, focus):
        super().__init__(step_type, step_id, name, content, datetime, color)
        self.focus = focus

    def __repr__(self):
        return (f'{self.name.upper()}: {self.content}. | Type: {self.step_type} | Datetime: {self.datetime} | Color: {self.color} |\n'
                f'Focus: {self.focus}')

class Event:
    def __init__(self, summary, description, start, end, color_id):
        self.summary = summary
        self.description = description
        self.start = start
        self.end = end
        self.color_id = color_id

    def __repr__(self):
        return f"{self.summary} {''.join(self.description.splitlines())} {self.start} {self.end} {self.color_id}"
