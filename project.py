import uuid
import sys

from generator import Generator
from classes import Step, FocusStep, GoalStep, Mode
from utils import read_json, write_json
from constants import COLORS_KEY, HELP, ERRORS


class App:
    def __init__(self, **kwargs):
        self.current_mode = Mode.BLANK
        self.selected_step = None
        self.steps_cache = []
        self.settings_cache = {}

        if 'test' not in kwargs or not kwargs['test']:
            self.main_loop()

    def main_loop(self):
        while True:
            inp = input(self.current_mode.value).strip().lower()

            if self.current_mode == Mode.BLANK:
                if inp == 'edit':
                    self.load_steps()
                    self.current_mode = Mode.EDIT
                elif inp == 'settings':
                    self.settings_cache = read_json('config.json')
                    self.reload_settings()
                    self.current_mode = Mode.CONFIG
            elif self.current_mode == Mode.EDIT:
                if inp.startswith('sel '):
                    err = self.sel_step(inp)
                    if err: print(err)
                elif inp.startswith('set '):
                    if not self.selected_step:
                        print('PLEASE SELECT STEP TO SET!')
                        continue
                    err = self.set_step(inp)
                    if err: print(err)
                elif inp.startswith('mk '):
                    if s := self.mk_step(inp):
                        self.steps_cache.append(s)
                        self.selected_step = s
                        self.render_steps()
                    else:
                        print('INVALID INPUT. Please use following format: mk type, name, content, date, color')
                elif inp == 'del':
                    if not self.selected_step:
                        print('PLEASE SELECT STEP TO DELETE!')
                        continue
                    self.del_step()
                elif inp == 'reload':
                    self.render_steps()
                elif inp == 'save':
                    self.save_steps()
                    self.current_mode = Mode.BLANK
                elif inp == 'gen':
                    self.generate()
                    self.current_mode = Mode.BLANK
                elif inp == 'help':
                    print(HELP['edit'])
                else:
                    print(ERRORS['HelpHint'])
            elif self.current_mode == Mode.CONFIG:
                if inp.startswith('set '):
                    err = self.set_setting(inp)
                    if err: print('ERROR: ', err)
                elif inp == 'reload':
                    self.reload_settings()
                elif inp == 'save':
                    self.current_mode = Mode.BLANK
                    write_json('config.json', self.settings_cache)
                elif inp == 'help':
                    print(HELP['setting'])
                else:
                    print(ERRORS['HelpHint'])

    # STEP METHODS
    ###############

    def render_steps(self):
        """reprints the steps in steps_cache"""

        self.steps_cache.sort(key=lambda step: step.datetime)

        if len(self.steps_cache) == 0:
            print(ERRORS['NoStepsError'])
            return

        last_sel = False

        for i, stp in enumerate(self.steps_cache):
            spaces = ' ' * (130 - len(stp.name) - len(stp.content))
            if stp.step_id == self.selected_step.step_id:
                last_sel = True
                print('─────────────────────────────────────────────────────────────────────────────────────────────────── SELECTED ───────────────────────────────────────────────────────────────────────────────────────────────────')
                print(str(i + 1) + ' ➤  ' + str(stp).replace('| Type:', spaces+'| Type:'))
            else:
                if last_sel:
                    last_sel = False
                    print('────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────')
                else:
                    print('・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・')
                print(str(i + 1) + '・  ' + stp.repr_sum().replace('| Type:', spaces+'| Type:'))

        if last_sel:
            print('────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────')
        else:
            print('・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・')

    def load_steps(self):
        """deserializes step data from data.json to steps_cache"""
        self.steps_cache = []
        step_data = read_json('data.json')['steps']
        if step_data:
            for v in step_data:
                inp = 'mk '
                for i, prop in enumerate(v.values()):
                    if i == len(v) - 1:
                        inp += str(prop)
                    else:
                        inp += f'{prop}, '
                self.steps_cache.append(self.mk_step(inp))
            self.selected_step = self.steps_cache[0]
            self.render_steps()
        else:
            print(ERRORS['NoStepsError'])

    def sel_step(self, inp):
        """
        Selects the number index specified or returns error if no valid int index is specified

        :param inp:
        :return: error or None
        """
        s_i = inp[4:].split(' ')
        if len(s_i) != 1 or not s_i[0].isdigit():
            return 'INVALID SELECTION: Please provide step index as int.'

        step_num = int(s_i[0]) - 1
        if len(self.steps_cache) <= step_num or step_num < 0:
            return 'INVALID SELECTION: Please specify existing step index.'

        self.selected_step = self.steps_cache[step_num]
        self.render_steps()

        return None

    def del_step(self):
        """
        Deletes currently selected_step or if error returns False

        :returns: True or False
        """
        for i, s in enumerate(self.steps_cache):
            if s.step_id == self.selected_step.step_id:
                self.steps_cache.remove(self.selected_step)

                if len(self.steps_cache) >= 1:
                    self.selected_step = self.steps_cache[0]
                else:
                    self.selected_step = None
                self.render_steps()

                return True
        return False

    def set_step(self, inp):
        """
        Sets step's property to specified value or returns error

        :param inp:
        :returns: None or Error
        """
        setting = inp[4:].split(' ')[0]
        set_to = inp[4+len(setting):]

        if hasattr(self.selected_step, setting):
            setattr(self.selected_step, setting, set_to)
        else:
            return 'INVALID PROPERTY!'

        self.render_steps()
        return None

    def mk_step(self, inp):
        """
        Creates and returns a step or returns False if invalid input

        :param inp:
        :return: Step/FocusStep/GoalStep or False if invalid input
        """
        props = [p.strip() for p in inp[2:].split(',')]

        s = props[0] == 'task' and len(props) == 5
        f = props[0] == 'focus' and len(props) == 10
        g = props[0] == 'goal' and len(props) == 6

        new_id = str(uuid.uuid4())
        props.insert(1, new_id)

        if s:
            return Step(*props)
        elif f:
            return FocusStep(*props)
        elif g:
            return GoalStep(*props)

        return False

    def save_steps(self):
        """Serializes step data to data.json to steps_cache"""
        steps_data = []
        for step in self.steps_cache:
            step_dict = {}
            for var, value in vars(step).items():
                if var != 'step_id':
                    step_dict.update({var.removeprefix('_'): str(value)})
            steps_data.append(step_dict)
        write_json('data.json', {'steps': steps_data})

    # SETTINGS METHODS
    ################

    def reload_settings(self):
        """Prints out current settings in setting_cache"""
        for key, val in self.settings_cache.items():
            print('───────────────────────────────────────────────')
            print(f'{key.upper()}: {str(val)}')
        print('───────────────────────────────────────────────')

    def set_setting(self, inp):
        """
        Sets a particular setting to a value or returns Error

        :param inp:
        :return: None or Error
        """
        setting = inp[4:].split(' ')[0]
        set_to = inp[4 + len(setting):].strip()

        match setting:
            case 'horizon':
                if not set_to.isdigit() or int(set_to) < 1:
                    return 'INVALID VALUE: Horizon must be a positive int.'
                self.settings_cache[setting] = int(set_to)
            case 'default_task_color':
                if set_to not in COLORS_KEY.keys():
                    return ERRORS['InvalidColorError']
                self.settings_cache[setting] = set_to
            case 'default_focus_color':
                if set_to not in COLORS_KEY.keys():
                    return ERRORS['InvalidColorError']
                self.settings_cache[setting] = set_to
            case 'task_duration':
                if not set_to.isdigit() or int(set_to) < 1:
                    return 'INVALID VALUE: Task_Duration must be a positive int.'
                self.settings_cache[setting] = int(set_to)
            case 'calendar_name':
                self.settings_cache[setting] = set_to
            case _:
                return 'INVALID SETTING!'

        self.reload_settings()
        return None

    # GENERATION METHODS
    ####################

    def generate(self):
        self.save_steps()
        gen = Generator(self.steps_cache)
        suc, fail = gen.generate()

        if suc:
            print("STEP GENERATION SUCCESS!")
        else:
            print("STEP GENERATION FAILED: " + str(fail))


if __name__ == '__main__':
    main = App()
