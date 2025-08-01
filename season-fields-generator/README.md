# season-fields-generator

![A view of the main screen of season-fields-generator](/repo/images/season-fields-generator.png)

A terminal app used to quickly generate and edit season fields for [Open Scouting](https://github.com/FRC-Team3484/open-scouting)

## Features
- Quickly create season fields without editing JSON directly
- Edit existing season fields by loading files
- Search the user's system for existing season field files

## Installation
Create a virtual environment
```bash
cd season-fields-generator
python3 -m venv .venv
```

Activate it
```bash
source ./.venv/bin/activate
```

And install any necessary packages
```
pip install -r requirements.txt
```

## Running the application
```bash
textual run main.py
```

## Development
You can run the application and open a Textual console to view any debug or error messages using the following commands, in two separate terminals
```bash
textual console
```

```bash
textual run --dev main.py
```

The `textual console` command can have optional parameters to exclude certain things from being outputted, to more clearly spot print statements 
```bash
textual console -x SYSTEM -x EVENT -x DEBUG -x INFO 
```

## To-Do
- [x] Warn if there's unsaved progress when loading a file or switching sections
- [x] Be able to edit items
- [x] Be able to delete items
- [x] Be able to move items up or down
- [x] Be able to create new sections or fields
- [x] Add the ability to save files
- [x] Add the ability to create a new file and specify the save location
- [x] Be able to add new top level fields or sections
- [x] Be able to create new file sections
- [x] Fix issues where running off of data in memory doesn't always work