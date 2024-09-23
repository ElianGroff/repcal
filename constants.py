import datetime as dt


TODAY = dt.datetime.combine(dt.date.today(), dt.time(0, 0, 0))

DEFAULT_START_TIME = '8:00 AM'
DEFAULT_END_TIME = '11:59 PM'

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_NAME = 'repcal_demo'

COLORS_KEY = {
    "lavender": '1',
    "sage": '2',
    "grape": '3',
    "flamingo": '4',
    "banana": '5',
    "tangerine": '6',
    "peacock": '7',
    "graphite": '8',
    "blueberry": '9',
    "basil": '10',
    "tomato": '11'
}

ERRORS = {
    'NoStepsError': 'No steps yet... Use "mk type, prop1, prop2, etc" to create a step.',
    'HelpHint': 'Type help for commands.',
    'InvalidColorError': "INVALID COLOR FORMAT: Valid colors include: 'lavender', 'sage', 'grape', 'flamingo', "
                         "'banana', 'tangerine', 'peacock', 'graphite', 'blueberry', 'basil', 'tomato'",
    'InvalidTimeReversedError': 'INVALID TIME. Please ensure Start Time occurs after End Time.'
    'InvalidTimeFormatError' 'Invalid Time. Valid Formats include: HH:MM:SS or H:SS PM/AM'
}

HELP = {
    'edit':
        f'mk type, name, content, date, color          | Creates and selects a Step. Separate properties with comma:,\n'
        f"  ▪ goal, time_start, time_end, items, days  | Focus Step's additional properties. \n"
        f"  ▪ focus                                    | Goal Step's additional property.\n"
        f'sel [step_num:int]                           | Selects the step by the number given.\n'
        f'del                                          | Deletes the currently selected step.\n'
        f'set [prop:str] [change:value]                | Changes the property of the selected step to a new value.\n'
        f'reload                                       | Re-renders all the current steps in the terminal.\n'
        f'save                                         | Saves all the current steps into data.json and moves you back to Menu Mode.\n'
        f'gen                                          | Generates or regenerates the steps as events on Google Calendar.\n'
    ,
    'setting':
        f"reload                                       | Re-renders the current settings in the terminal.\n"
        f"set [setting] [change:value]                 | Configures the specified setting to the given value.\n"
        f"save                                         | Saves the changes you made to settings and moves you back to Menu Mode.\n"
}

