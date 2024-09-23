import pytest

from classes import FocusStep, Mode
from utils import val_time, get_datetime
from repcal import App
from constants import ERRORS
from datetime import datetime as dt

def main():
    test_get_datetime()
    test_val_time()
    test_focus_step()
    test_app()
    print('TEST COMPETE SUCCESSFULLY!')

# utils.py TESTS
##################


def test_get_datetime():
    assert get_datetime('11-10-2002 12:14 PM') == False  # Incorrect Order
    #?assert get_datetime('1999-10-22 12:14 PM') == dt.today()  # Past Date
    assert get_datetime('2029-11-12 13:14 PM') == False  # Incorrect digits

    assert get_datetime('2025-11-24 5:40 AM') != False
    assert get_datetime('2029-11-12 12:14 PM') != False
    assert get_datetime('2029-10-12 13:02:13') != False


def test_val_time():
    assert val_time('12 PM') == False
    assert val_time('1:62 PPM') == False
    assert val_time('13:14 AM') == False

    assert val_time('12:14 PM') != False
    assert val_time('13:02:13') != False

# classes.py TESTS
##################


def test_focus_step():
    with pytest.raises(ValueError):
        # Testing Invalid Color
        FocusStep('task', 't_id', 't_name', 't_content', '2029-11-12 12:14 PM', 'orange', 't_goal', '12:14 PM', '11:14 PM', 't_items', 'all')


# project.py App UNIT TESTS
#######################

def test_app():
    app = App(test=True)
    app.current_mode = Mode.EDIT

    assert app.mk_step('mk task, t_name, t_content, 2025-11-24, sage, woops') == False  # Too many props
    assert app.mk_step('mk focus, t_name, t_content, 2025-11-24, sage, t_goal, 4:44 AM, 5:23 PM, t_items, all, woops') == False  # Too many props

    with pytest.raises(ValueError):
        app.mk_step('mk task, t_name, t_content, 2025-11-24, orange')  # Invalid types

    # No steps selected
    assert app.del_step() == False

    # Create steps to test
    app.steps_cache.append(app.mk_step('mk task, t_name, t_content, 2025-11-24, sage'))
    app.steps_cache.append(app.mk_step('mk task, t_name, t_content, 2025-11-24 00:31:01, sage'))
    app.steps_cache.append(app.mk_step('mk goal, t_name, t_content, 2025-11-24 5:40 AM, sage, t_focus'))
    app.steps_cache.append(app.mk_step('mk focus, t_name, t_content, 2028-11-24, sage, t_goal, 4:44 AM, 5:23 PM, t_items, all'))

    assert app.sel_step('sel 5') == 'INVALID SELECTION: Please specify existing step index.'
    assert app.sel_step('sel nonint') == 'INVALID SELECTION: Please provide step index as int.'

    # Selects step to test
    assert app.sel_step('sel 4') == None

    assert app.del_step() == True
    assert app.sel_step('sel 4') == 'INVALID SELECTION: Please specify existing step index.'

    # Selects step to test
    assert app.sel_step('sel 2') == None

    # Correctly changing properties
    assert app.set_step('set name t_set_name') == None
    assert app.set_step('set content t_set_content') == None

    # Incorrect property
    assert app.set_step('set woops value') == 'INVALID PROPERTY!'

    app.save_steps()
    app.load_steps()

    assert app.sel_step('sel 2') == None

    app.save_steps()
    app.current_mode = Mode.CONFIG

    assert app.set_setting('set horizon -10') == 'INVALID VALUE: Horizon must be a positive int.'
    assert app.set_setting('set horizon woops') == 'INVALID VALUE: Horizon must be a positive int.'

    assert app.set_setting('set task_duration -42') == 'INVALID VALUE: Task_Duration must be a positive int.'
    assert app.set_setting('set task_duration woops') == 'INVALID VALUE: Task_Duration must be a positive int.'

    assert app.set_setting('set default_task_color woops') == ERRORS['InvalidColorError']
    assert app.set_setting('set default_focus_color woops') == ERRORS['InvalidColorError']

    assert app.set_setting('set woops') == 'INVALID SETTING!'


if __name__ == '__main__':
    main()
