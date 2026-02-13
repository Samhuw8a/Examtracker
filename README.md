[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FSamhuw8a%2FExamtracker%2Fmaster%2Fpyproject.toml&color=d8634c)

# A Python examtracker for the "Lernphase"
Allows you to keep track of all the Exams you already finished and the scores you got.
Uses Sqlalchemy and sqlite for storing data and Textual as the TUI backend


# Instalation
- Clone the repository to your mashine
```bash
git clone https://github.com/Samhuw8a/Examtracker.git
```

- Install the Project on your computer
```bash
cd Examtracker
python -m pip install -e .
```
_You might have to add the --break-system-packages flag to the install command._


- You then need to change the location of the config file inside the main.py file
get the location:
```bash
cd data
echo "$(pwd)/config.yml"
```
change this line:
```python
    config: Settings = read_settings_from_config(
        "/Users/samuel/Repositories/Examtracker/data/config.yml"  # Change this value
    )
```


# Usage
Once installed the programm can be used like so:
```bash
examtracker
```

## SQL Tables
__exams__: ID; name; max\_points; scored\_points; class\_id

__classes__: ID; Name; semester\_id

__semester__: ID; Name (Unique),

## TODOS

- [x] Handle SQL Errors
- [x] Initialize DB
- [x] Settings.json file
- [x] Abort edit and add screens
- [ ] system independant config searching
- [ ] better CSS
