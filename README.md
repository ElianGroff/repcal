## SKIBITY OHIO CALENDER 
To say the core of this calendar program is to generate a ToDo List onto Google Calendar wood be an understatement. The features of this program revolve around three types of Steps. 
- **Task Step** - Events a few hours in length that could be done today or around today. (ex. shopping lists, misc to dos, etc)
- **Focus Step** - Events repeating across the week and beyond that have sub-tasks to them. (ex. work, social events, sleeping, etc)
- **Goal Step** - General long-term goals that you're aiming for over course of 5 or more years. These steps are not generated onto the calendar. (ex. career goals, family goals)

Eventually, I'll be adding more types of steps to fill in the spaces in the micro to macro scales of planning but for now this will do. 

So how do you use it? Learn the following commands and interface to be able to create, load, edit, save and most 
importantly generate onto google calendar all these types of steps from your terminal. You also can change the configuration of 
how these events are generated in the settings menu.


### How to Use
The program starts in _Menu Mode_ from which you can proceed to _Edit Mode_ or _Settings Mode_  with the following.
##### ```edit``` moves you to _Edit Mode_ and prints all steps in terminal

- ```mk type, name, content, date, color``` Creates and selects a _Step_. **Separate properties with comma: ,**
  - ```goal, time_start, time_end, items, days``` _Focus Step's_ additional properties. 
  - ```focus``` _Goal Step's_ additional property.
- ```sel [step_num:int]``` Selects the step by the number given.
- ```del``` Deletes the currently selected step.
- ```set [prop:str] [change:value]``` Changes the property of the selected step to a new value.
- ```reload``` Re-renders all the current steps in the terminal.
- ```save``` Saves all the current steps into data.json and moves you back to _Menu Mode_.
- ```gen``` Generates or regenerates the steps as events on Google Calendar.
- ```help``` Displays this list of commands.

##### ```settings``` moves you to _Settings Mode_ and displays the settings of the app
 
- ```reload``` Re-renders the current settings in the terminal.
- ```set [setting] [change:value]``` Configures the specified setting to the given value.
- ```save``` Saves the changes you made to settings and moves you back to _Menu Mode_.
- ```help``` Displays this list of commands.

### Settings
 
- ```horizon:int``` The duration in days the program will generate Google Calendar events. (Over 40 not recommended.)
- ```default_task_color:str``` The color a _Task_ will be set to if no color is specified. 
- ```default_focus_color:str``` The color a _Focus_ will be set to if no color is specified.
- ```calendar_name:str``` The name the generated calendar will have.
- ```task_duration:int``` The length of tasks event.

### Step Properties

- ```type:str``` The type of step. (Task, Focus, Goal)
- ```name:str``` Name of the step.
- ```content:str``` Content of the step.
- ```date:datetime``` When the step is to be done by.
  - If left blank will default to today plus: (45 days for _Task_. One year for _Focus_. 5 years for _Goal_)
- ```color:str``` Color of the step's event once generated onto Google Calendar.
  - Valid colors include Google Calendar's provided colors of 'lavender', 'sage', 'grape', 'flamingo', 
  'banana', 'tangerine', 'peacock', 'graphite', 'blueberry', 'basil', or 'tomato'.
  - If left blank will default to the default color specified in settings.

#### Focus Step Properties (Inherits the Step Properties)

- ```goal:str``` The name of the focus's goal.
- ```time_start:time``` When during the day you can start working on focus.
- ```time_end:time``` The end time of when you can work on the focus.
- ```items:str``` The sub-tasks of the Focus. Separated with -.(ex: start project-work on project-finish project)
- ```days:str``` The days of week you can work on the _Focus_. Separated with -.(ex:sun-mon-tue-wed-thu-fri-sat)
  - Use `all` for property to automatically set to 'sun-mon-tue-wed-thu-fri-sat'.

#### Goal Step Properties (Inherits the Step Properties)

- ```focus:str``` What the _Focus_ of the _Goal_ is.
  - There's no functionality over this property yet.