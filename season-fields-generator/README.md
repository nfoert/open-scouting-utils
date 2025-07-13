# season-fields-generator

A terminal app used to quickly generate and edit season fields for [Open Scouting](https://github.com/FRC-Team3484/open-scouting)

## Features
- Create season fields
- Edit existing season fields by import
- Add the path to the season fields file when developing and edit all of the season fields there

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