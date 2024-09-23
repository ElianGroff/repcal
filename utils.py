import datetime as dt
import re
import json


def get_datetime(d):
    m_date = re.findall(r'^(\d{4})-(\d{2})-(\d{2})$', d)  # 2034-12-15
    m_datetime = re.findall(r'^(\d{4})-(\d{2})-(\d{2}) ([0-9][0-2]*):([0-5][0-9])+ ([A|P]M)$', d, re.IGNORECASE)  # 2034-12-15 5:14 PM
    m_alt = re.findall(r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$', d)  # 2025-11-24 00:00:00

    today = dt.datetime.today()

    if m_date:
        date = dt.datetime.strptime(d, "%Y-%m-%d")
        if today < date:
            return date
        return today
    elif m_datetime:
        date = dt.datetime.strptime(d, "%Y-%m-%d %I:%M %p")
        if today < date:
            return date
        return today
    elif m_alt:
        date = dt.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
        if today < date:
            return date
        return today

    return False


def val_time(t):
    m = re.search(r'^([0-9][0-2]*):([0-5][0-9])+ ([A|P]M)$', t, re.IGNORECASE)
    m_alt = re.search(r'^(\d{2}):(\d{2}):(\d{2})$', t, re.IGNORECASE)

    if m:
        time = dt.datetime.strptime(t, "%I:%M %p").time()
        return time
    elif m_alt:
        time = dt.datetime.strptime(t, "%H:%M:%S").time()
        return time

    return False


def read_json(fn):
    with open(fn, 'r') as f:
        return json.load(f)


def write_json(fn, data):
    with open(fn, 'w') as f:
        json.dump(data, f, indent=4)
